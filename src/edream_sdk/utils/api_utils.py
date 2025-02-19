from dacite import from_dict, DaciteError, Config, MissingValueError
from enum import Enum
from typing import TypeVar, Type, Dict, Any, Optional
from ..models.api_types import ApiResponse
from ..models.vote_types import VoteType
from ..models.dream_types import DreamStatusType
from ..models.types import T

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
    data: Dict[str, Any], data_type: Optional[Type[T]] = None
) -> ApiResponse[T]:
    try:
        success = data.get("success")
        message = data.get("message")
        raw_data = data.get("data")

        # If no data_type provided or data_type is ApiResponse, just create ApiResponse directly
        if data_type is None or data_type == ApiResponse:
            return ApiResponse(success=success, message=message, data=raw_data)

        deserialized_data = None
        try:
            deserialized_data = from_dict(
                data_class=data_type,
                data=raw_data,
                config=enum_config(VoteType, DreamStatusType),
            )

        except MissingValueError as e:
            print(f"Missing value error: {e.field_path}")
            raise
        except DaciteError as e:
            print(f"Dacite error: {str(e)}")
            raise
        except Exception as e:
            print(f"Deserialization error: {str(e)}")
            raise

        result = ApiResponse(success=success, message=message, data=deserialized_data)
        return result

    except Exception as e:
        print(f"Error in deserialize_api_response: {str(e)}")
        print(f"Error type: {type(e)}")
        raise
