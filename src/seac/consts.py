from dataclasses import dataclass
from enum import Enum

class MissionType(Enum):
    PICKING = 1
    RETURNING = 2
    DELIVERING = 3

@dataclass
class Mission:
    mission_type: MissionType
    location_id: int
    location_x: int
    location_y: int
    assigned_time: int
    at_location: bool = False