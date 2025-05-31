from typing import ClassVar
from dataclasses import dataclass
import asyncio

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, ExpressionParser, NumberValue, DirectionValue


@dataclass
class MoveCommand(Command):
    """MOVE command - moves the car forward or backward."""

    COMMAND_NAMES: ClassVar[list[str]] = ["MOVE"]

    # Command-specific attributes
    distance_value: Value | None = None
    while_condition: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse MOVE arguments.

        Formats:
        - MOVE (no args = move 1 unit forward)
        - MOVE | 5
        - MOVE | -3 (negative = backward)
        - MOVE | WHILE | condition
        """
        if not tokens:
            # No arguments - default to moving 1 unit forward
            self.distance_value = NumberValue(1)
            return

        # Check for WHILE modifier
        if tokens[0].upper() == "WHILE":
            # MOVE | WHILE | condition
            if len(tokens) < 2:
                raise ValueError("WHILE requires a condition")

            condition_tokens = tokens[1:]
            self.while_condition = ExpressionParser.parse_tokens(condition_tokens)
            if not self.while_condition:
                raise ValueError(f"Invalid condition: {' '.join(condition_tokens)}")
        else:
            # MOVE | distance
            self.distance_value = ValueParser.parse(tokens[0])
            if not self.distance_value:
                raise ValueError(f"Invalid distance value: {tokens[0]}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the MOVE command."""
        if context.send_message:
            await context.send_message(f"Executing MOVE at {self.grid_position}")

        if self.while_condition:
            # MOVE WHILE condition
            step_distance = 1  # Move 1 unit at a time
            while True:
                # Check cancellation
                if context.check_cancelled and context.check_cancelled():
                    break

                # Evaluate condition
                condition_result = await self.while_condition.evaluate(context)
                if not condition_result:
                    break

                # Move one step
                context.move(step_distance)

                # Small delay to prevent tight loops
                await asyncio.sleep(0.01)

                # Check for runaway execution
                if context.steps_executed > context.max_steps:
                    raise RuntimeError("Maximum steps exceeded")
        elif self.distance_value:
            # Regular MOVE with distance
            distance = await self.distance_value.evaluate(context)
            if not isinstance(distance, (int, float)):
                raise ValueError(f"Distance must be a number, got {type(distance)}")

            context.move(float(distance))
        else:
            raise ValueError("MOVE command has neither distance nor WHILE condition")

    def __repr__(self) -> str:
        if self.while_condition:
            return f"MoveCommand(WHILE {self.while_condition})"
        return f"MoveCommand({self.distance_value})"


@dataclass
class TurnCommand(Command):
    """TURN command - rotates the car."""

    COMMAND_NAMES: ClassVar[list[str]] = ["TURN"]

    # Command-specific attributes
    direction: Value | None = None
    while_condition: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse TURN arguments.

        Formats:
        - TURN | LEFT
        - TURN | RIGHT
        - TURN | 45 (degrees - positive=right, negative=left)
        - TURN | LEFT | 45 (turn left by 45 degrees)
        - TURN | RIGHT | 30 (turn right by 30 degrees)
        - TURN | LEFT | WHILE | condition
        - TURN | RIGHT | WHILE | condition
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
            # Check for WHILE modifier
            if tokens[1].upper() == "WHILE":
                # TURN | direction | WHILE | condition
                self.direction = DirectionValue(direction_str)

                if len(tokens) < 3:
                    raise ValueError("WHILE requires a condition")

                condition_tokens = tokens[2:]
                self.while_condition = ExpressionParser.parse_tokens(condition_tokens)
                if not self.while_condition:
                    raise ValueError(f"Invalid condition: {' '.join(condition_tokens)}")
            else:
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
            await context.send_message(f"Executing TURN at {self.grid_position}")

        if not self.direction:
            raise ValueError("TURN command has no direction")

        if self.while_condition:
            # TURN direction WHILE condition
            direction_value = await self.direction.evaluate(context)
            # DirectionValue returns -90 for LEFT, 90 for RIGHT
            if not isinstance(direction_value, (int, float)):
                raise ValueError(
                    f"Expected numeric degrees, got {type(direction_value)}"
                )
            step_degrees = 5 if direction_value > 0 else -5  # 5 degrees at a time

            while True:
                # Check cancellation
                if context.check_cancelled and context.check_cancelled():
                    break

                # Evaluate condition
                condition_result = await self.while_condition.evaluate(context)
                if not condition_result:
                    break

                # Turn one step
                context.turn(step_degrees)

                # Small delay to prevent tight loops
                await asyncio.sleep(0.01)

                # Check for runaway execution
                if context.steps_executed > context.max_steps:
                    raise RuntimeError("Maximum steps exceeded")
        else:
            # Regular TURN with direction
            turn_degrees = await self.direction.evaluate(context)

            if isinstance(turn_degrees, (int, float)):
                context.turn(float(turn_degrees))
            else:
                raise ValueError(f"Invalid turn degrees: {turn_degrees}")

    def __repr__(self) -> str:
        if self.while_condition:
            return f"TurnCommand({self.direction} WHILE {self.while_condition})"
        return f"TurnCommand({self.direction})"
