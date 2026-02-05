"""
Authentication Utilities
JWT token generation, validation, dan password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# ==================== CONFIGURATION ====================

# Secret key untuk JWT - GANTI dengan random secret di production!
# Generate dengan: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context untuk hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== PASSWORD HASHING ====================

def hash_password(password: str) -> str:
    """
    Hash password menggunakan bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    
    Example:
        >>> hashed = hash_password("secret123")
        >>> print(hashed)
        $2b$12$KIXn0q4z...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password dengan hash
    
    Args:
        plain_password: Plain text password dari user
        hashed_password: Hashed password dari database
    
    Returns:
        True jika password cocok, False jika tidak
    
    Example:
        >>> hashed = hash_password("secret123")
        >>> verify_password("secret123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT TOKEN ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate JWT access token
    
    Args:
        data: Data yang akan di-encode dalam token (biasanya {"sub": email})
        expires_delta: Durasi expire token (default 30 menit)
    
    Returns:
        JWT token string
    
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    
    Token structure:
        {
            "sub": "user@example.com",  # Subject (user identifier)
            "exp": 1234567890            # Expiration timestamp
        }
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode dan validasi JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload jika valid, None jika invalid/expired
    
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {'sub': 'user@example.com', 'exp': 1234567890}
    
    Raises:
        JWTError: Jika token invalid atau expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_email(token: str) -> Optional[str]:
    """
    Extract email dari JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Email jika token valid, None jika invalid
    
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> email = get_current_user_email(token)
        >>> print(email)
        user@example.com
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    email: str = payload.get("sub")
    return email


# ==================== HELPER FUNCTIONS ====================

def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extract token dari Authorization header
    
    Args:
        authorization_header: Header value "Bearer <token>"
    
    Returns:
        Token string atau None jika invalid format
    
    Example:
        >>> token = extract_bearer_token("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    if not authorization_header:
        return None
    
    if not authorization_header.startswith("Bearer "):
        return None
    
    token = authorization_header.replace("Bearer ", "")
    return token
