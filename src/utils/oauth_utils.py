"""Google OAuth utilities for SSO authentication."""

import os
from typing import Optional, Dict, Any

from google.auth.transport import requests
from google.oauth2 import id_token
import structlog

logger = structlog.get_logger("oauth_utils")

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google ID token and return user info.
    
    Args:
        token: Google ID token from client
        
    Returns:
        User info dict with email, name, google_id if valid, None otherwise
    """
    try:
        if not GOOGLE_CLIENT_ID:
            logger.error("oauth_utils.missing_client_id")
            return None
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning("oauth_utils.invalid_issuer", issuer=idinfo.get('iss'))
            return None
        
        # Extract user info
        user_info = {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "google_id": idinfo.get("sub"),  # Google user ID
            "picture": idinfo.get("picture"),
        }
        
        if not user_info["email"] or not user_info["google_id"]:
            logger.warning("oauth_utils.missing_user_info")
            return None
        
        logger.info("oauth_utils.token_verified", email=user_info["email"])
        return user_info
        
    except ValueError as e:
        logger.warning("oauth_utils.invalid_token", error=str(e))
        return None
    except Exception as e:
        logger.error("oauth_utils.verify_error", error=str(e))
        return None


def get_google_user_info(token: str) -> Optional[Dict[str, Any]]:
    """
    Alias for verify_google_token for consistency.
    
    Args:
        token: Google ID token
        
    Returns:
        User info dict if valid, None otherwise
    """
    return verify_google_token(token)

