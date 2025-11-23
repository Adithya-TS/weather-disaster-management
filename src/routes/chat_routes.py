"""Chat history routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..api.dependencies import get_current_user
from ..services.chat_service import ChatService
import structlog

logger = structlog.get_logger("chat_routes")

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatHistoryResponse(BaseModel):
    """Response model for chat history entry."""
    id: int
    user_id: int
    input_text: str
    output_text: str
    model: Optional[str]
    created_at: str


class ChatHistoryListResponse(BaseModel):
    """Response model for chat history list."""
    success: bool
    chats: List[ChatHistoryResponse]
    count: int


@router.get("/history", response_model=ChatHistoryListResponse)
async def get_chat_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of chats to return"),
    offset: int = Query(0, ge=0, description="Number of chats to skip"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history for the authenticated user.
    """
    try:
        chat_service = ChatService(db)
        chats = await chat_service.get_user_chat_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "chats": chats,
            "count": len(chats)
        }
    except Exception as e:
        logger.error("chat_routes.get_chat_history.error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_by_id(
    chat_id: int = Path(..., description="Chat history ID"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific chat conversation by ID.
    """
    try:
        chat_service = ChatService(db)
        chat = await chat_service.get_chat_by_id(chat_id, user_id)
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        return chat
    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_routes.get_chat_by_id.error", chat_id=chat_id, user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat: {str(e)}"
        )

