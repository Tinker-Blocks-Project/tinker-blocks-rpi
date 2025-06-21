from typing import ClassVar
from dataclasses import dataclass
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, NumberValue, DirectionValue, ExpressionParser


@dataclass
class MoveCommand(Command):
    """MOVE command - moves the car forward or backward."""

    COMMAND_NAMES: ClassVar[list[str]] = ["MOVE"]

    # Command-specific attributes
    distance_value: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse MOVE arguments.

        Formats:
        - MOVE (no args = move 999 units forward - effectively "move until obstacle")
        - MOVE | 5
        - MOVE | -3 (negative = backward)
        """
        if not tokens:
            # No arguments - default to moving 999 units forward (effectively infinite)
            self.distance_value = NumberValue(999)
            return

        # MOVE | distance
        self.distance_value = ValueParser.parse(tokens[0])
        if not self.distance_value:
            raise ValueError(f"Invalid distance value: {tokens[0]}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the MOVE command."""
        if context.send_message:
            await context.send_message(
                f"Executing MOVE at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.distance_value:
            raise ValueError("MOVE command has no distance")

        # Regular MOVE with distance
        if context.send_message:
            await context.send_message(
                f"⚙️ MOVE evaluating distance: {self.distance_value}", LogLevel.DEBUG
            )

        distance = await self.distance_value.evaluate(context)
        if not isinstance(distance, (int, float)):
            raise ValueError(f"Distance must be a number, got {type(distance)}")

        if context.send_message:
            await context.send_message(f"🚗 Moving {distance} units", LogLevel.INFO)

        await context.move(float(distance))

        if context.send_message:
            await context.send_message(
                f"📍 Moved to position ({context.position.x}, {context.position.y}), direction: {context.direction.value}",
                LogLevel.DEBUG,
            )

    def __repr__(self) -> str:
        return f"MoveCommand({self.distance_value})"


@dataclass
class TurnCommand(Command):
    """TURN command - rotates the car."""

    COMMAND_NAMES: ClassVar[list[str]] = ["TURN"]

    # Command-specific attributes
    direction: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse TURN arguments.

        Formats:
        - TURN | LEFT
        - TURN | RIGHT
        - TURN | 45 (degrees - positive=right, negative=left)
        - TURN | LEFT | 45 (turn left by 45 degrees)
        - TURN | RIGHT | 30 (turn right by 30 degrees)
        - TURN | A (where A is a variable)
        - TURN | expr (where expr is an expression or variable)
        """
        if not tokens:
            raise ValueError("TURN requires direction (LEFT or RIGHT) or degrees or variable/expression")

        # If two tokens: direction + degrees (e.g., TURN | LEFT | 45)
        if len(tokens) == 2:
            direction_val = ValueParser.parse(tokens[0])
            degrees_val = ValueParser.parse(tokens[1])
            if direction_val and isinstance(direction_val, DirectionValue) and degrees_val and isinstance(degrees_val, NumberValue):
                # Compose a NumberValue with sign based on direction
                deg = degrees_val.value
                if direction_val.direction_name == "LEFT":
                    deg = -abs(deg)
                else:
                    deg = abs(deg)
                self.direction = NumberValue(deg)
                return
            # Otherwise, treat as expression
            self.direction = ExpressionParser.parse_tokens(tokens)
            return

        # Otherwise, parse as a single value or expression
        self.direction = ValueParser.parse(tokens[0])
        if not self.direction:
            # Try as expression
            self.direction = ExpressionParser.parse_tokens(tokens)
        if not self.direction:
            raise ValueError(f"TURN argument not recognized: {' '.join(tokens)}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the TURN command."""
        if context.send_message:
            await context.send_message(
                f"Executing TURN at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.direction:
            raise ValueError("TURN command has no direction")

        # Evaluate the direction/expression/variable
        if context.send_message:
            await context.send_message(
                f"⚙️ TURN evaluating direction: {self.direction}", LogLevel.DEBUG
            )

        turn_val = await self.direction.evaluate(context)

        # Acceptable: number (degrees), or string (LEFT/RIGHT)
        if isinstance(turn_val, (int, float)):
            turn_degrees = float(turn_val)
        elif isinstance(turn_val, str):
            turn_val_upper = turn_val.upper()
            if turn_val_upper == "LEFT":
                turn_degrees = -90.0
            elif turn_val_upper == "RIGHT":
                turn_degrees = 90.0
            else:
                raise ValueError(f"TURN variable/expression must resolve to LEFT, RIGHT, or degrees, got: {turn_val}")
        else:
            raise ValueError(f"TURN variable/expression must resolve to LEFT, RIGHT, or degrees, got: {turn_val}")

        if context.send_message:
            await context.send_message(f"🔄 Turning {turn_degrees}°", LogLevel.INFO)

        await context.turn(turn_degrees)

        if context.send_message:
            await context.send_message(
                f"🧭 Now facing {context.direction.value}", LogLevel.DEBUG
            )

    def __repr__(self) -> str:
        return f"TurnCommand({self.direction})"
