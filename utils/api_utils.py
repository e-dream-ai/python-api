from models.api_types import ApiResponse
from dacite import from_dict, DaciteError, Config, MissingValueError
from enum import Enum
from typing import TypeVar, Type, Dict, Any
from models.vote_types import VoteType
from models.dream_types import DreamStatusType

T = TypeVar("T")


class StrEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


def enum_config(*enums: Type[StrEnum]) -> Config:
    def cast_enum(enum_class: Type[StrEnum], value: Any) -> Any:
        if isinstance(value, str):
            return enum_class(value)
        return value

    return Config(
        strict=False,
        check_types=False,
        cast={enum: lambda x: cast_enum(enum, x) for enum in enums},
    )


def deserialize_api_response(
    data: Dict[str, Any], data_type: Type[T]
) -> ApiResponse[T]:
    try:
        success = data.get("success")
        message = data.get("message")
        raw_data = data.get("data")

        deserialized_data = None
        if raw_data is not None:

            try:
                deserialized_data = from_dict(
                    data_class=data_type,
                    data=raw_data,
                    config=enum_config(VoteType, DreamStatusType),
                )
            except MissingValueError as e:
                print(f"Warning: Missing value for field {e.field_path}")

        return ApiResponse(success=success, message=message, data=deserialized_data)

    except DaciteError as e:
        print(f"Error parsing data: {e}")
    except Exception as e:
        print(f"Error: {e}")
