"""User repository for database operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user import User
import structlog

logger = structlog.get_logger("user_repository")


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("user_repository.get_by_email.error", email=email, error=str(e))
            raise
    
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """
        Get user by Google ID.
        
        Args:
            google_id: Google user ID
            
        Returns:
            User if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(User).where(User.google_id == google_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("user_repository.get_by_google_id.error", google_id=google_id, error=str(e))
            raise
    
    async def create(self, email: str, name: str, google_id: str) -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            name: User name
            google_id: Google user ID
            
        Returns:
            Created User
        """
        try:
            user = User(
                email=email,
                name=name,
                google_id=google_id
            )
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)
            logger.info("user_repository.create.success", user_id=user.id, email=email)
            return user
        except Exception as e:
            logger.error("user_repository.create.error", email=email, error=str(e))
            await self.db.rollback()
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("user_repository.get_by_id.error", user_id=user_id, error=str(e))
            raise

