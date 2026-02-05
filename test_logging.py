"""
Test script to verify logging and error handling
"""
from app.core import setup_logging, get_logger
from app.core.exceptions import UserNotFoundException, InvalidCredentialsException
from app.schemas import success_response, error_response

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Test logging
logger.info("Testing info log")
logger.warning("Testing warning log")
logger.error("Testing error log")

# Test exceptions
try:
    raise UserNotFoundException(user_id=123)
except UserNotFoundException as e:
    logger.error(f"Caught exception: {e.message}")
    print(f"Exception status: {e.status_code}, message: {e.message}")

# Test response format
response = success_response({"user": "test"}, "Operation successful")
print(f"\nSuccess response: {response}")

error = error_response("Test error", 400)
print(f"Error response: {error}")

print("\n✅ All tests passed! Check logs/app.log for log entries")
