from typing import Optional, TypedDict, Generic, TypeVar

T = TypeVar('T')

class ApiResponse(TypedDict, Generic[T]):
    success: Optional[bool]
    message: Optional[str] 
    data: Optional[T]