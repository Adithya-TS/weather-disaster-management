"""JWT token utilities for authentication."""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import structlog

logger = structlog.get_logger("jwt_utils")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def create_access_token(user_id: int, email: str) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        Encoded JWT token
    """
    try:
        expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        payload: Dict[str, Any] = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "exp": expiration,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        logger.info("jwt_utils.token_created", user_id=user_id, email=email)
        return token
    except Exception as e:
        logger.error("jwt_utils.create_token.error", user_id=user_id, error=str(e))
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("jwt_utils.token_expired")
        return None
    except InvalidTokenError as e:
        logger.warning("jwt_utils.invalid_token", error=str(e))
        return None
    except Exception as e:
        logger.error("jwt_utils.verify_token.error", error=str(e))
        return None


def get_current_user_id(token: str) -> Optional[int]:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            logger.warning("jwt_utils.invalid_user_id", sub=payload.get("sub"))
            return None
    return None

