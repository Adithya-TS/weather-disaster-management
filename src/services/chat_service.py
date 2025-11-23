"""Chat service for handling chat operations."""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.chat_history_repository import ChatHistoryRepository
import structlog

logger = structlog.get_logger("chat_service")


class ChatService:
    """Service for chat operations."""
    
    def __init__(self, db: AsyncSession):
        self.chat_repo = ChatHistoryRepository(db)
    
    async def save_chat(
        self,
        user_id: int,
        input_text: str,
        output_text: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save a chat conversation to history.
        
        Args:
            user_id: User ID
            input_text: User input
            output_text: Model output
            model: Model name used
            
        Returns:
            Dict with saved chat entry info
        """
        try:
            chat_entry = await self.chat_repo.create(
                user_id=user_id,
                input_text=input_text,
                output_text=output_text,
                model=model
            )
            
            return {
                "id": chat_entry.id,
                "user_id": chat_entry.user_id,
                "input_text": chat_entry.input_text,
                "output_text": chat_entry.output_text,
                "model": chat_entry.model,
                "created_at": chat_entry.created_at.isoformat(),
            }
        except Exception as e:
            logger.error("chat_service.save_chat.error", user_id=user_id, error=str(e))
            raise
    
    async def get_user_chat_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of chat history entries
        """
        try:
            chat_entries = await self.chat_repo.get_by_user_id(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
            
            return [
                {
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "input_text": entry.input_text,
                    "output_text": entry.output_text,
                    "model": entry.model,
                    "created_at": entry.created_at.isoformat(),
                }
                for entry in chat_entries
            ]
        except Exception as e:
            logger.error("chat_service.get_user_chat_history.error", user_id=user_id, error=str(e))
            raise
    
    async def get_chat_by_id(
        self,
        chat_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific chat entry by ID.
        
        Args:
            chat_id: Chat history ID
            user_id: User ID (for authorization)
            
        Returns:
            Chat entry dict if found, None otherwise
        """
        try:
            chat_entry = await self.chat_repo.get_by_id(chat_id, user_id)
            
            if not chat_entry:
                return None
            
            return {
                "id": chat_entry.id,
                "user_id": chat_entry.user_id,
                "input_text": chat_entry.input_text,
                "output_text": chat_entry.output_text,
                "model": chat_entry.model,
                "created_at": chat_entry.created_at.isoformat(),
            }
        except Exception as e:
            logger.error("chat_service.get_chat_by_id.error", chat_id=chat_id, user_id=user_id, error=str(e))
            raise

