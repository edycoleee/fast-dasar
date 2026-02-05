#!/usr/bin/env python3
"""Quick test for production features"""

print("Testing imports...")

from app.core import setup_logging, get_logger
from app.schemas import success_response, error_response
from app.core.exceptions import UserNotFoundException

print("✅ All imports successful!")

# Test logging
setup_logging()
logger = get_logger(__name__)
logger.info("Test log entry")

# Test response
resp = success_response("Test message", {"key": "value"})
print(f"✅ Response format: {resp}")

# Test exception
try:
    raise UserNotFoundException(user_id=999)
except UserNotFoundException as e:
    print(f"✅ Exception: {e.message} (Status: {e.status_code})")

print("\n✅ All production features working correctly!")
