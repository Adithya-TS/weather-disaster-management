"""Authentication service for handling user authentication."""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.user_repository import UserRepository
from ..utils.jwt_utils import create_access_token
from ..utils.oauth_utils import verify_google_token
import structlog

logger = structlog.get_logger("auth_service")


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
    
    async def authenticate_google(self, google_token: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with Google token.
        Creates user if doesn't exist, returns JWT token.
        
        Args:
            google_token: Google ID token from client
            
        Returns:
            Dict with access_token and user info, or None if authentication fails
        """
        try:
            # Verify Google token
            user_info = verify_google_token(google_token)
            if not user_info:
                logger.warning("auth_service.google_verification_failed")
                return None
            
            email = user_info["email"]
            name = user_info["name"]
            google_id = user_info["google_id"]
            
            # Check if user exists
            user = await self.user_repo.get_by_google_id(google_id)
            
            if not user:
                # Create new user
                user = await self.user_repo.create(
                    email=email,
                    name=name,
                    google_id=google_id
                )
                logger.info("auth_service.user_created", user_id=user.id, email=email)
            else:
                logger.info("auth_service.user_found", user_id=user.id, email=email)
            
            # Generate JWT token
            access_token = create_access_token(user.id, user.email)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                }
            }
        except Exception as e:
            logger.error("auth_service.authenticate_google.error", error=str(e))
            raise

