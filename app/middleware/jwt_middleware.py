"""
JWT Middleware
Automatically inject user from JWT token into request
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token, extract_bearer_token
from app.core.deps import get_db
from app.models.user import User


class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically validate JWT and inject user into request state
    
    This middleware:
    1. Extracts JWT token from Authorization header
    2. Validates and decodes the token
    3. Fetches user from database
    4. Injects user into request.state.user
    
    Protected endpoints can then access request.state.user
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip middleware for public endpoints
        public_paths = ["/docs", "/redoc", "/openapi.json", "/api/v1/auth/login"]
        if request.url.path in public_paths or request.url.path == "/":
            return await call_next(request)
        
        # Extract token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # If no token, continue without user (endpoint will handle auth requirement)
            request.state.user = None
            return await call_next(request)
        
        try:
            # Extract bearer token
            token = extract_bearer_token(auth_header)
            
            # Decode token
            payload = decode_access_token(token)
            email = payload.get("sub")
            
            if not email:
                request.state.user = None
                return await call_next(request)
            
            # Get user from database
            db = next(get_db())
            user = db.query(User).filter(User.email == email).first()
            
            # Inject user into request state
            request.state.user = user
            
        except HTTPException:
            # Token invalid, continue without user
            request.state.user = None
        except Exception:
            # Any other error, continue without user
            request.state.user = None
        
        return await call_next(request)
