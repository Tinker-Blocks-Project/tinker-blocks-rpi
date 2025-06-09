from enum import Enum, auto
from typing import TypeAlias, Union
from dataclasses import dataclass


class CommandType(Enum):
    """Types of commands supported by the engine."""

    # Movement
    MOVE = auto()
    TURN = auto()

    # Control Flow
    LOOP = auto()
    IF = auto()
    ELSE = auto()

    # Variables
    SET = auto()

    # Drawing
    PEN_UP = auto()
    PEN_DOWN = auto()

    # Utility
    WAIT = auto()
    ALERT_ON = auto()
    ALERT_OFF = auto()


class Direction(Enum):
    """Movement directions."""

    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"

    @property
    def degrees(self) -> float:
        """Get rotation degrees for turn directions."""
        if self == Direction.LEFT:
            return -90
        elif self == Direction.RIGHT:
            return 90
        elif self == Direction.BACKWARD:
            return 180
        return 0


class ValueType(Enum):
    """Types of values in the system."""

    NUMBER = auto()
    VARIABLE = auto()
    SENSOR = auto()
    DIRECTION = auto()
    BOOLEAN = auto()


class SensorType(Enum):
    """Available sensor types."""

    DISTANCE = "distance"
    OBSTACLE = "obstacle"
    BLACK_DETECTED = "black_detected"
    BLACK_LOST = "black_lost"


class OperatorType(Enum):
    """Operator types for expressions."""

    # Comparison
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    EQUAL = "="
    NOT_EQUAL = "!="

    # Logical
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Arithmetic
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


@dataclass(frozen=True)
class Position:
    """2D position in the car's coordinate system."""

    x: float
    y: float

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)


@dataclass(frozen=True)
class GridPosition:
    """Position in the grid (row, col)."""

    row: int
    col: int

    @property
    def indentation_level(self) -> int:
        """Get indentation level from column position."""
        return self.col


# Type aliases
Number: TypeAlias = Union[int, float]
