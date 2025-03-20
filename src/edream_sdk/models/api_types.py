from typing import Optional, TypedDict
from dataclasses import dataclass
from .types import T


@dataclass
class ApiResponse(TypedDict):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[T] = None
