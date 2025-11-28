"""API routes for alerts and notifications."""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..api.dependencies import get_current_user
from ..services.alert_service import AlertService
from ..services.notification_service import NotificationService
from ..models import SeverityLevel, AlertType
import structlog

logger = structlog.get_logger("alert_routes")

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# Request/Response Models
class AlertCreateRequest(BaseModel):
    """Request to create a new alert."""
    location: str = Field(..., min_length=2, description="Location to monitor")


class AlertResponse(BaseModel):
    """Alert response model."""
    id: int
    alert_type: str
    severity: str
    title: str
    description: str
    location: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    temperature: Optional[float]
    wind_speed: Optional[float]
    precipitation: Optional[float]
    humidity: Optional[float]
    is_active: bool
    is_sent: bool
    detected_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SubscriptionCreateRequest(BaseModel):
    """Request to create a subscription."""
    location: str = Field(..., min_length=2, description="Location to monitor")
    radius_km: float = Field(50.0, ge=1, le=500, description="Alert radius in kilometers")
    email_enabled: bool = Field(True, description="Enable email notifications")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS")
    push_enabled: bool = Field(False, description="Enable push notifications")
    notify_on_low: bool = Field(False, description="Notify on LOW severity")
    notify_on_medium: bool = Field(True, description="Notify on MEDIUM severity")
    notify_on_high: bool = Field(True, description="Notify on HIGH severity")
    notify_on_critical: bool = Field(True, description="Notify on CRITICAL severity")


class SubscriptionUpdateRequest(BaseModel):
    """Request to update a subscription."""
    radius_km: Optional[float] = Field(None, ge=1, le=500)
    email_enabled: Optional[bool] = None
    phone_number: Optional[str] = None
    push_enabled: Optional[bool] = None
    notify_on_low: Optional[bool] = None
    notify_on_medium: Optional[bool] = None
    notify_on_high: Optional[bool] = None
    notify_on_critical: Optional[bool] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    """Subscription response model."""
    id: int
    user_id: int
    location: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    radius_km: float
    email_enabled: bool
    phone_number: Optional[str]
    push_enabled: bool
    notify_on_low: bool
    notify_on_medium: bool
    notify_on_high: bool
    notify_on_critical: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Alert Endpoints

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    location: Optional[str] = Query(None, description="Filter by location"),
    severity: Optional[str] = Query(None, description="Minimum severity: low, medium, high, critical"),
    active_only: bool = Query(True, description="Show only active alerts"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of alerts, optionally filtered by location and severity.
    Requires authentication.
    """
    try:
        alert_service = AlertService(db)
        
        # Parse severity
        severity_filter = None
        if severity:
            try:
                severity_filter = SeverityLevel[severity.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid severity level. Must be one of: low, medium, high, critical"
                )
        
        alerts = await alert_service.get_active_alerts(
            location=location,
            severity=severity_filter
        )
        
        # Limit results
        alerts = alerts[:limit]
        
        return [
            AlertResponse(
                id=alert.id,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value,
                title=alert.title,
                description=alert.description,
                location=alert.location,
                city=alert.city,
                state=alert.state,
                country=alert.country,
                temperature=alert.temperature,
                wind_speed=alert.wind_speed,
                precipitation=alert.precipitation,
                humidity=alert.humidity,
                is_active=alert.is_active,
                is_sent=alert.is_sent,
                detected_at=alert.detected_at,
                expires_at=alert.expires_at
            )
            for alert in alerts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("alert_routes.get_alerts_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.post("/check", response_model=dict)
async def check_location_for_alerts(
    request: AlertCreateRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check a location for severe weather and create alerts if needed.
    If alert is created, notifications are sent in the background.
    """
    try:
        alert_service = AlertService(db)
        
        # Analyze weather for the location
        alert_data = await alert_service.analyze_weather_for_alerts(request.location)
        
        if not alert_data:
            return {
                "success": True,
                "alert_created": False,
                "message": f"No severe weather conditions detected in {request.location}"
            }
        
        # Create alert
        alert = await alert_service.create_alert(alert_data)
        
        # Send notifications in background
        background_tasks.add_task(
            send_alert_notifications_task,
            alert.id,
            db
        )
        
        return {
            "success": True,
            "alert_created": True,
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "alert_type": alert.alert_type.value,
            "title": alert.title,
            "message": "Alert created and notifications are being sent"
        }
        
    except Exception as e:
        logger.error("alert_routes.check_alert_error", location=request.location, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to check for alerts: {str(e)}")


# Subscription Endpoints

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionCreateRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert subscription for the authenticated user.
    User will receive notifications when severe weather is detected in the subscribed location.
    """
    try:
        from ..models import UserSubscription
        from ..tools.custom_tools import geocode_location
        
        # Geocode location
        geo_data = geocode_location(request.location)
        if not geo_data:
            raise HTTPException(
                status_code=400,
                detail=f"Could not geocode location: {request.location}"
            )
        
        # Create subscription
        subscription = UserSubscription(
            user_id=user_id,
            location=request.location,
            city=geo_data.get("name"),
            state=geo_data.get("state"),
            country=geo_data.get("country"),
            latitude=geo_data.get("lat"),
            longitude=geo_data.get("lon"),
            radius_km=request.radius_km,
            email_enabled=request.email_enabled,
            phone_number=request.phone_number,
            push_enabled=request.push_enabled,
            notify_on_low=request.notify_on_low,
            notify_on_medium=request.notify_on_medium,
            notify_on_high=request.notify_on_high,
            notify_on_critical=request.notify_on_critical,
            is_active=True
        )
        
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        
        logger.info("alert_routes.subscription_created",
                   user_id=user_id,
                   subscription_id=subscription.id,
                   location=request.location)
        
        return SubscriptionResponse.model_validate(subscription)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("alert_routes.create_subscription_error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all alert subscriptions for the authenticated user."""
    try:
        from sqlalchemy import select
        from ..models import UserSubscription
        
        stmt = select(UserSubscription).where(
            UserSubscription.user_id == user_id
        ).order_by(UserSubscription.created_at.desc())
        
        result = await db.execute(stmt)
        subscriptions = result.scalars().all()
        
        return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
        
    except Exception as e:
        logger.error("alert_routes.get_subscriptions_error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve subscriptions: {str(e)}")


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    request: SubscriptionUpdateRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an alert subscription."""
    try:
        from sqlalchemy import select
        from ..models import UserSubscription
        
        # Get subscription
        stmt = select(UserSubscription).where(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == user_id
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Update fields
        if request.radius_km is not None:
            subscription.radius_km = request.radius_km
        if request.email_enabled is not None:
            subscription.email_enabled = request.email_enabled
        if request.phone_number is not None:
            subscription.phone_number = request.phone_number
        if request.push_enabled is not None:
            subscription.push_enabled = request.push_enabled
        if request.notify_on_low is not None:
            subscription.notify_on_low = request.notify_on_low
        if request.notify_on_medium is not None:
            subscription.notify_on_medium = request.notify_on_medium
        if request.notify_on_high is not None:
            subscription.notify_on_high = request.notify_on_high
        if request.notify_on_critical is not None:
            subscription.notify_on_critical = request.notify_on_critical
        if request.is_active is not None:
            subscription.is_active = request.is_active
        
        await db.commit()
        await db.refresh(subscription)
        
        logger.info("alert_routes.subscription_updated",
                   user_id=user_id,
                   subscription_id=subscription_id)
        
        return SubscriptionResponse.model_validate(subscription)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("alert_routes.update_subscription_error",
                    subscription_id=subscription_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an alert subscription."""
    try:
        from sqlalchemy import select, delete
        from ..models import UserSubscription
        
        # Verify subscription belongs to user
        stmt = select(UserSubscription).where(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == user_id
        )
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Delete subscription
        stmt = delete(UserSubscription).where(UserSubscription.id == subscription_id)
        await db.execute(stmt)
        await db.commit()
        
        logger.info("alert_routes.subscription_deleted",
                   user_id=user_id,
                   subscription_id=subscription_id)
        
        return {"success": True, "message": "Subscription deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("alert_routes.delete_subscription_error",
                    subscription_id=subscription_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete subscription: {str(e)}")


# Alert Detail Endpoint (must be AFTER /subscriptions routes to avoid conflicts)

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific alert by ID."""
    try:
        from sqlalchemy import select
        from ..models import Alert
        
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return AlertResponse(
            id=alert.id,
            alert_type=alert.alert_type.value,
            severity=alert.severity.value,
            title=alert.title,
            description=alert.description,
            location=alert.location,
            city=alert.city,
            state=alert.state,
            country=alert.country,
            temperature=alert.temperature,
            wind_speed=alert.wind_speed,
            precipitation=alert.precipitation,
            humidity=alert.humidity,
            is_active=alert.is_active,
            is_sent=alert.is_sent,
            detected_at=alert.detected_at,
            expires_at=alert.expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("alert_routes.get_alert_error", alert_id=alert_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")


# Background task
async def send_alert_notifications_task(alert_id: int, db: AsyncSession):
    """Background task to send alert notifications."""
    try:
        from sqlalchemy import select
        from ..models import Alert
        
        # Get alert
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if not alert:
            logger.error("alert_routes.notification_task.alert_not_found", alert_id=alert_id)
            return
        
        # Send notifications
        notification_service = NotificationService(db)
        result = await notification_service.send_alert_notifications(alert)
        
        # Mark alert as sent
        alert_service = AlertService(db)
        await alert_service.mark_alert_as_sent(alert_id)
        
        logger.info("alert_routes.notifications_sent",
                   alert_id=alert_id,
                   sent=result.get("sent", 0),
                   failed=result.get("failed", 0))
        
    except Exception as e:
        logger.error("alert_routes.notification_task_error", alert_id=alert_id, error=str(e))

