from typing import Optional, TypedDict, TypeVar

T = TypeVar('T')

class ApiResponse(TypedDict):
    success: Optional[bool]
    message: Optional[str]
    data: Optional[T]