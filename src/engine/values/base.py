from abc import ABC, abstractmethod

from ..types import Number
from ..context import ExecutionContext


class Value(ABC):
    """Abstract base class for all values."""

    @abstractmethod
    async def evaluate(self, context: ExecutionContext) -> Number | bool | str:
        """Evaluate the value in the given context."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """String representation for debugging."""
        pass


class ValueParser:
    """Parser for converting tokens to Value objects."""

    @staticmethod
    def parse(token: str) -> Value | None:
        """Parse a token into a Value object.

        Returns None if the token is not a recognized value.
        """
        from .types import (
            NumberValue,
            VariableValue,
            SensorValue,
            DirectionValue,
            BooleanValue,
        )

        # Try to parse as number
        try:
            if "." in token:
                return NumberValue(float(token))
            else:
                return NumberValue(int(token))
        except ValueError:
            pass

        # Check for special values
        token_upper = token.upper()

        # Boolean values
        if token_upper in ("TRUE", "FALSE"):
            return BooleanValue(token_upper == "TRUE")

        # Direction values
        if token_upper in ("LEFT", "RIGHT", "FORWARD", "BACKWARD"):
            return DirectionValue(token_upper)

        # Sensor values
        if token_upper in ("DISTANCE", "OBSTACLE", "BLACK_DETECTED", "BLACK_LOST"):
            return SensorValue(token_upper)

        # Variable values - any alphabetic string that's not a command
        if token.isalpha():
            return VariableValue(token_upper)

        # Not a recognized value
        return None
