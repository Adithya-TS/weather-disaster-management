"""Chat history repository for database operations."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from ..models.chat_history import ChatHistory
import structlog

logger = structlog.get_logger("chat_history_repository")


class ChatHistoryRepository:
    """Repository for chat history database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        input_text: str,
        output_text: str,
        model: Optional[str] = None
    ) -> ChatHistory:
        """
        Create a new chat history entry.
        
        Args:
            user_id: User ID
            input_text: User input text
            output_text: Model output text
            model: Model name used
            
        Returns:
            Created ChatHistory
        """
        try:
            chat_entry = ChatHistory(
                user_id=user_id,
                input_text=input_text,
                output_text=output_text,
                model=model
            )
            self.db.add(chat_entry)
            await self.db.flush()
            await self.db.refresh(chat_entry)
            logger.info("chat_history_repository.create.success", chat_id=chat_entry.id, user_id=user_id)
            return chat_entry
        except Exception as e:
            logger.error("chat_history_repository.create.error", user_id=user_id, error=str(e))
            await self.db.rollback()
            raise
    
    async def get_by_user_id(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistory]:
        """
        Get chat history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of ChatHistory entries
        """
        try:
            result = await self.db.execute(
                select(ChatHistory)
                .where(ChatHistory.user_id == user_id)
                .order_by(desc(ChatHistory.created_at))
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("chat_history_repository.get_by_user_id.error", user_id=user_id, error=str(e))
            raise
    
    async def get_by_id(self, chat_id: int, user_id: int) -> Optional[ChatHistory]:
        """
        Get a specific chat history entry by ID (ensuring it belongs to the user).
        
        Args:
            chat_id: Chat history ID
            user_id: User ID (for authorization)
            
        Returns:
            ChatHistory if found and belongs to user, None otherwise
        """
        try:
            result = await self.db.execute(
                select(ChatHistory)
                .where(ChatHistory.id == chat_id)
                .where(ChatHistory.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("chat_history_repository.get_by_id.error", chat_id=chat_id, user_id=user_id, error=str(e))
            raise

