"""FastAPI dependencies for authentication."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..utils.jwt_utils import verify_token, get_current_user_id
import structlog

logger = structlog.get_logger("dependencies")

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> int:
    """
    Dependency to get current authenticated user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    
    payload = verify_token(token)
    if not payload:
        logger.warning("dependencies.invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = get_current_user_id(token)
    if not user_id:
        logger.warning("dependencies.invalid_user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[int]:
    """
    Dependency to optionally get current authenticated user ID.
    Returns None if no token is provided.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User ID if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return get_current_user_id(token)

