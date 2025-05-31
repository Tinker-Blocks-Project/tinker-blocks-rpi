from dataclasses import dataclass

from .base import Value
from ..types import Number, SensorType
from ..context import ExecutionContext


@dataclass
class NumberValue(Value):
    """A numeric constant value."""

    value: Number

    async def evaluate(self, context: ExecutionContext) -> Number:
        return self.value

    def __repr__(self) -> str:
        return f"NumberValue({self.value})"


@dataclass
class BooleanValue(Value):
    """A boolean constant value."""

    value: bool

    async def evaluate(self, context: ExecutionContext) -> bool:
        return self.value

    def __repr__(self) -> str:
        return f"BooleanValue({self.value})"


@dataclass
class VariableValue(Value):
    """A variable reference."""

    name: str

    async def evaluate(self, context: ExecutionContext) -> Number | bool:
        return context.get_variable(self.name)

    def __repr__(self) -> str:
        return f"VariableValue({self.name})"


@dataclass
class SensorValue(Value):
    """A sensor reading value."""

    sensor_name: str

    async def evaluate(self, context: ExecutionContext) -> Number | bool:
        sensor_map = {
            "DISTANCE": SensorType.DISTANCE,
            "OBSTACLE": SensorType.OBSTACLE,
            "BLACK_DETECTED": SensorType.BLACK_DETECTED,
            "BLACK_LOST": SensorType.BLACK_LOST,
        }

        sensor_type = sensor_map.get(self.sensor_name.upper())
        if sensor_type:
            return await context.get_sensor_value(sensor_type)

        raise ValueError(f"Unknown sensor: {self.sensor_name}")

    def __repr__(self) -> str:
        return f"SensorValue({self.sensor_name})"


@dataclass
class DirectionValue(Value):
    """A direction value (LEFT, RIGHT, etc.)."""

    direction_name: str

    async def evaluate(self, context: ExecutionContext) -> str | Number:
        # For turns, LEFT and RIGHT map to degrees
        if self.direction_name == "LEFT":
            return -90
        elif self.direction_name == "RIGHT":
            return 90
        # For other uses, return the direction name
        return self.direction_name

    def __repr__(self) -> str:
        return f"DirectionValue({self.direction_name})"
