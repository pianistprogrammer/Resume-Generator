"""Generic response models for API endpoints."""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


# Generic type for data
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response model with data and message."""
    success: bool = True
    msg: str
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "msg": "Operation completed successfully",
                "data": {}
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    msg: str
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "msg": "An error occurred",
                "error": "Detailed error message"
            }
        }
