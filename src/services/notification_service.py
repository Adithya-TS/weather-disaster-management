"""Notification service for sending alerts via email and other channels."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import structlog

from ..models import (
    Alert, 
    User, 
    UserSubscription, 
    NotificationLog, 
    NotificationType, 
    NotificationStatus,
    SeverityLevel
)

logger = structlog.get_logger("notification_service")


class NotificationService:
    """Service for sending notifications via email, SMS, and push."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Email configuration from environment
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Weather Disaster Management")
    
    async def send_alert_notifications(self, alert: Alert) -> Dict[str, Any]:
        """
        Send notifications for an alert to all subscribed users in the affected area.
        
        Args:
            alert: Alert object to send notifications for
            
        Returns:
            Summary of notifications sent
        """
        try:
            # Find users subscribed to this location
            subscribed_users = await self._get_subscribed_users(alert)
            
            if not subscribed_users:
                logger.info("notification_service.no_subscribers", 
                           alert_id=alert.id, 
                           location=alert.location)
                return {
                    "success": True,
                    "sent": 0,
                    "failed": 0,
                    "message": "No subscribers found for this location"
                }
            
            sent_count = 0
            failed_count = 0
            
            for user, subscription in subscribed_users:
                # Check if user wants notifications for this severity level
                if not self._should_notify(subscription, alert.severity):
                    continue
                
                # Send email notification
                if subscription.email_enabled and user.email:
                    success = await self._send_email_notification(user, alert, subscription)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                
                # TODO: Add SMS notifications
                # if subscription.phone_number:
                #     await self._send_sms_notification(user, alert, subscription)
                
                # TODO: Add push notifications
                # if subscription.push_enabled:
                #     await self._send_push_notification(user, alert, subscription)
            
            logger.info("notification_service.batch_complete",
                       alert_id=alert.id,
                       sent=sent_count,
                       failed=failed_count)
            
            return {
                "success": True,
                "sent": sent_count,
                "failed": failed_count,
                "total_subscribers": len(subscribed_users)
            }
            
        except Exception as e:
            logger.error("notification_service.send_error", 
                        alert_id=alert.id, 
                        error=str(e))
            return {
                "success": False,
                "error": str(e),
                "sent": 0,
                "failed": 0
            }
    
    async def _get_subscribed_users(self, alert: Alert) -> List[tuple]:
        """Get users subscribed to the alert location."""
        try:
            # Calculate distance and find nearby subscriptions
            # For now, simple location matching
            stmt = select(User, UserSubscription).join(
                UserSubscription, User.id == UserSubscription.user_id
            ).where(
                and_(
                    UserSubscription.is_active == True,
                    or_(
                        UserSubscription.location.ilike(f"%{alert.location}%"),
                        UserSubscription.city.ilike(f"%{alert.city}%") if alert.city else False,
                        UserSubscription.state.ilike(f"%{alert.state}%") if alert.state else False
                    )
                )
            )
            
            result = await self.db.execute(stmt)
            users_subscriptions = result.all()
            
            return [(row[0], row[1]) for row in users_subscriptions]
            
        except Exception as e:
            logger.error("notification_service.get_subscribers_error", error=str(e))
            return []
    
    def _should_notify(self, subscription: UserSubscription, severity: SeverityLevel) -> bool:
        """Check if user should be notified based on their preferences."""
        severity_map = {
            SeverityLevel.LOW: subscription.notify_on_low,
            SeverityLevel.MEDIUM: subscription.notify_on_medium,
            SeverityLevel.HIGH: subscription.notify_on_high,
            SeverityLevel.CRITICAL: subscription.notify_on_critical
        }
        return severity_map.get(severity, True)
    
    async def _send_email_notification(
        self, 
        user: User, 
        alert: Alert,
        subscription: UserSubscription
    ) -> bool:
        """Send email notification to a user."""
        try:
            # Create email content
            subject = f"🚨 {alert.severity.value.upper()} ALERT: {alert.title}"
            
            html_body = self._create_email_html(user, alert)
            text_body = self._create_email_text(user, alert)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = user.email
            
            # Attach both text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            if not self.smtp_user or not self.smtp_password:
                # Simulate sending in development
                logger.warning("notification_service.smtp_not_configured",
                             message="SMTP not configured, simulating email send")
                await self._log_notification(
                    user.id, alert.id, NotificationType.EMAIL,
                    user.email, subject, html_body,
                    NotificationStatus.SENT
                )
                return True
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            # Log successful send
            await self._log_notification(
                user.id, alert.id, NotificationType.EMAIL,
                user.email, subject, html_body,
                NotificationStatus.SENT
            )
            
            logger.info("notification_service.email_sent",
                       user_id=user.id,
                       alert_id=alert.id,
                       email=user.email)
            
            return True
            
        except Exception as e:
            logger.error("notification_service.email_error",
                        user_id=user.id,
                        alert_id=alert.id,
                        error=str(e))
            
            # Log failed send
            await self._log_notification(
                user.id, alert.id, NotificationType.EMAIL,
                user.email, subject if 'subject' in locals() else "",
                "", NotificationStatus.FAILED, error_message=str(e)
            )
            
            return False
    
    def _create_email_html(self, user: User, alert: Alert) -> str:
        """Create HTML email content."""
        severity_colors = {
            SeverityLevel.LOW: "#3b82f6",      # blue
            SeverityLevel.MEDIUM: "#f59e0b",   # orange
            SeverityLevel.HIGH: "#ef4444",     # red
            SeverityLevel.CRITICAL: "#7f1d1d"  # dark red
        }
        
        color = severity_colors.get(alert.severity, "#3b82f6")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; font-size: 24px;">⚠️ Weather Alert</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Severe Weather Detected in Your Area</p>
    </div>
    
    <div style="background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
        <p style="margin: 0 0 20px 0;">Hi {user.name},</p>
        
        <div style="background: white; padding: 20px; border-left: 4px solid {color}; margin-bottom: 20px; border-radius: 5px;">
            <h2 style="margin: 0 0 10px 0; color: {color}; font-size: 20px;">{alert.title}</h2>
            <p style="margin: 0; font-size: 16px;">{alert.description}</p>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: 18px;">Alert Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Location:</td>
                    <td style="padding: 8px 0;">{alert.location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Severity:</td>
                    <td style="padding: 8px 0; color: {color}; font-weight: bold;">{alert.severity.value.upper()}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Type:</td>
                    <td style="padding: 8px 0;">{alert.alert_type.value.replace('_', ' ').title()}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Detected:</td>
                    <td style="padding: 8px 0;">{alert.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                </tr>
            </table>
        </div>
        
        {self._create_weather_details_html(alert)}
        
        <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; font-weight: bold;">⚠️ Safety Recommendations:</p>
            <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                <li>Stay indoors and away from windows</li>
                <li>Monitor local news and weather updates</li>
                <li>Have emergency supplies ready</li>
                <li>Follow instructions from local authorities</li>
            </ul>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
        
        <p style="font-size: 14px; color: #6b7280; margin: 0;">
            This alert was sent to you because you subscribed to weather alerts for {alert.location}.
            <br><br>
            Stay safe,<br>
            <strong>Weather Disaster Management Team</strong>
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def _create_weather_details_html(self, alert: Alert) -> str:
        """Create weather details section for email."""
        if not any([alert.temperature, alert.wind_speed, alert.precipitation, alert.humidity]):
            return ""
        
        details = '<div style="background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px;">'
        details += '<h3 style="margin: 0 0 15px 0; font-size: 18px;">Weather Conditions</h3>'
        details += '<table style="width: 100%; border-collapse: collapse;">'
        
        if alert.temperature is not None:
            details += f'''
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">🌡️ Temperature:</td>
                    <td style="padding: 8px 0;">{alert.temperature:.1f}°C</td>
                </tr>
            '''
        
        if alert.wind_speed is not None:
            details += f'''
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">💨 Wind Speed:</td>
                    <td style="padding: 8px 0;">{alert.wind_speed:.1f} km/h</td>
                </tr>
            '''
        
        if alert.precipitation is not None:
            details += f'''
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">🌧️ Precipitation:</td>
                    <td style="padding: 8px 0;">{alert.precipitation:.1f} mm</td>
                </tr>
            '''
        
        if alert.humidity is not None:
            details += f'''
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">💧 Humidity:</td>
                    <td style="padding: 8px 0;">{alert.humidity:.1f}%</td>
                </tr>
            '''
        
        details += '</table></div>'
        return details
    
    def _create_email_text(self, user: User, alert: Alert) -> str:
        """Create plain text email content."""
        text = f"""
WEATHER ALERT - {alert.severity.value.upper()}

Hi {user.name},

{alert.title}

{alert.description}

ALERT DETAILS:
--------------
Location: {alert.location}
Severity: {alert.severity.value.upper()}
Type: {alert.alert_type.value.replace('_', ' ').title()}
Detected: {alert.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        if any([alert.temperature, alert.wind_speed, alert.precipitation, alert.humidity]):
            text += "\nWEATHER CONDITIONS:\n-------------------\n"
            if alert.temperature is not None:
                text += f"Temperature: {alert.temperature:.1f}°C\n"
            if alert.wind_speed is not None:
                text += f"Wind Speed: {alert.wind_speed:.1f} km/h\n"
            if alert.precipitation is not None:
                text += f"Precipitation: {alert.precipitation:.1f} mm\n"
            if alert.humidity is not None:
                text += f"Humidity: {alert.humidity:.1f}%\n"
        
        text += """
SAFETY RECOMMENDATIONS:
-----------------------
* Stay indoors and away from windows
* Monitor local news and weather updates
* Have emergency supplies ready
* Follow instructions from local authorities

Stay safe,
Weather Disaster Management Team
"""
        return text
    
    async def _log_notification(
        self,
        user_id: int,
        alert_id: int,
        notification_type: NotificationType,
        recipient_email: Optional[str],
        subject: str,
        message: str,
        status: NotificationStatus,
        error_message: Optional[str] = None
    ):
        """Log notification to database."""
        try:
            log = NotificationLog(
                user_id=user_id,
                alert_id=alert_id,
                notification_type=notification_type,
                status=status,
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                error_message=error_message,
                sent_at=datetime.utcnow() if status == NotificationStatus.SENT else None
            )
            
            self.db.add(log)
            await self.db.commit()
            
        except Exception as e:
            logger.error("notification_service.log_error", error=str(e))
            await self.db.rollback()

