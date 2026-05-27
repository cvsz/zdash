from enum import Enum


class GovernanceDriftLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
