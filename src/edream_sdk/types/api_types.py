from typing import Optional, TypedDict


class ApiResponse[T](TypedDict):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[T] = None
