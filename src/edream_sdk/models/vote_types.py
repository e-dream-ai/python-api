from enum import Enum
from dataclasses import dataclass


# Enum for VoteType
class VoteType(Enum):
    NONE = "none"
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


# Data class for Vote
@dataclass
class Vote:
    id: int
    vote: VoteType
    created_at: str
    updated_at: str
