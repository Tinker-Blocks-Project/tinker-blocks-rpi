from typing import ClassVar
from dataclasses import dataclass
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, NumberValue, DirectionValue


@dataclass
class MoveCommand(Command):
    """MOVE command - moves the car forward or backward."""

    COMMAND_NAMES: ClassVar[list[str]] = ["MOVE"]

    # Command-specific attributes
    distance_value: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse MOVE arguments.

        Formats:
        - MOVE (no args = move 1 unit forward)
        - MOVE | 5
        - MOVE | -3 (negative = backward)
        """
        if not tokens:
            # No arguments - default to moving 1 unit forward
            self.distance_value = NumberValue(1)
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
        """
        if not tokens:
            raise ValueError("TURN requires direction (LEFT or RIGHT) or degrees")

        # Check if first token is a number (direct degrees)
        try:
            degrees = float(tokens[0])
            self.direction = NumberValue(degrees)
            return
        except ValueError:
            pass

        # Otherwise, expect LEFT or RIGHT
        direction_str = tokens[0].upper()
        if direction_str not in ("LEFT", "RIGHT"):
            raise ValueError(f"TURN requires LEFT, RIGHT, or degrees, got: {tokens[0]}")

        # Check for additional arguments
        if len(tokens) >= 2:
            # TURN | direction | degrees
            try:
                custom_degrees = float(tokens[1])
                # Apply sign based on direction
                if direction_str == "LEFT":
                    custom_degrees = -abs(custom_degrees)
                else:  # RIGHT
                    custom_degrees = abs(custom_degrees)
                self.direction = NumberValue(custom_degrees)
            except ValueError:
                raise ValueError(f"Invalid degrees value: {tokens[1]}")
        else:
            # Just direction, use default 90 degrees
            self.direction = DirectionValue(direction_str)

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the TURN command."""
        if context.send_message:
            await context.send_message(
                f"Executing TURN at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.direction:
            raise ValueError("TURN command has no direction")

        # Regular TURN with direction
        if context.send_message:
            await context.send_message(
                f"⚙️ TURN evaluating direction: {self.direction}", LogLevel.DEBUG
            )

        turn_degrees = await self.direction.evaluate(context)

        if isinstance(turn_degrees, (int, float)):
            if context.send_message:
                await context.send_message(f"🔄 Turning {turn_degrees}°", LogLevel.INFO)

            await context.turn(float(turn_degrees))

            if context.send_message:
                await context.send_message(
                    f"🧭 Now facing {context.direction.value}", LogLevel.DEBUG
                )
        else:
            raise ValueError(f"Invalid turn degrees: {turn_degrees}")

    def __repr__(self) -> str:
        return f"TurnCommand({self.direction})"
