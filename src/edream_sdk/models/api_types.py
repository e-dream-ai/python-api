from typing import Generic, Optional, TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[T] = None
