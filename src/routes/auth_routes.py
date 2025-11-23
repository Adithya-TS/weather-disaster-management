"""Authentication routes for Google SSO."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..services.auth_service import AuthService
import structlog

logger = structlog.get_logger("auth_routes")

router = APIRouter(prefix="/auth", tags=["Authentication"])


class GoogleLoginRequest(BaseModel):
    """Request model for Google login."""
    credential: str = Field(..., description="Google ID token from client")


class AuthResponse(BaseModel):
    """Response model for authentication."""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/google/login", response_model=AuthResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate Google OAuth login.
    This endpoint receives the Google ID token from the client.
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate_google(request.credential)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        logger.info("auth_routes.google_login.success", user_id=result["user"]["id"])
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("auth_routes.google_login.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


@router.post("/google/callback", response_model=AuthResponse)
async def google_callback(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Google OAuth callback endpoint.
    Receives Google ID token and returns JWT token.
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate_google(request.credential)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        logger.info("auth_routes.google_callback.success", user_id=result["user"]["id"])
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("auth_routes.google_callback.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

