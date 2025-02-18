from typing import Generic, Optional, TypeVar, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json

T = TypeVar("T", bound=Any)


@dataclass_json
@dataclass
class ApiResponse(Generic[T]):
    success: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[T] = None
