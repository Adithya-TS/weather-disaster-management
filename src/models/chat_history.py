"""Chat history model for storing conversations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.connection import Base


class ChatHistory(Base):
    """Chat history model for storing user conversations."""
    
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    model = Column(String(100), nullable=True)  # Model used for generation
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", backref="chat_history")
    
    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"

