"""
Standard Response Schemas
Consistent API response format
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar('DataT')


class StandardResponse(BaseModel, Generic[DataT]):
    """
    Standard API response format
    
    All API responses follow this structure:
    {
        "success": true/false,
        "message": "Description of the result",
        "data": {...}  // Optional, contains the actual data
    }
    """
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Human-readable message about the result")
    data: Optional[DataT] = Field(None, description="Response data (null if error)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Example"}
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response format
    
    Structure:
    {
        "success": false,
        "message": "Error description",
        "data": null,
        "error": {
            "code": "ERROR_CODE",
            "details": {...}  // Optional additional error details
        }
    }
    """
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    data: None = Field(None, description="Always null for errors")
    error: Optional[dict] = Field(None, description="Additional error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "User not found",
                "data": None,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "details": {"user_id": 123}
                }
            }
        }


def success_response(
    message: str,
    data: Any = None
) -> dict:
    """
    Create a success response
    
    Args:
        message: Success message
        data: Response data
        
    Returns:
        Dictionary with standard response format
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Any] = None
) -> dict:
    """
    Create an error response
    
    Args:
        message: Error message
        error_code: Optional error code
        details: Optional additional error details
        
    Returns:
        Dictionary with standard error response format
    """
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    
    if error_code or details:
        response["error"] = {}
        if error_code:
            response["error"]["code"] = error_code
        if details:
            response["error"]["details"] = details
    
    return response
