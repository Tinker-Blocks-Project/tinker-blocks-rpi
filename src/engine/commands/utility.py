from typing import ClassVar
from dataclasses import dataclass
import asyncio
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, ExpressionParser


@dataclass
class WaitCommand(Command):
    """WAIT command - pauses execution for a specified time or while a condition is true."""

    COMMAND_NAMES: ClassVar[list[str]] = ["WAIT", "PAUSE", "SLEEP", "DELAY"]

    # Command-specific attributes
    time_value: Value | None = None
    while_condition: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse WAIT arguments.

        Formats:
        - WAIT | 2
        - WAIT | 0.5
        - WAIT | WHILE | condition
        """
        if not tokens:
            raise ValueError("WAIT requires time in seconds or WHILE condition")

        # Check for WHILE modifier
        if tokens[0].upper() == "WHILE":
            # WAIT | WHILE | condition
            if len(tokens) < 2:
                raise ValueError("WHILE requires a condition")

            condition_tokens = tokens[1:]
            self.while_condition = ExpressionParser.parse_tokens(condition_tokens)
            if not self.while_condition:
                raise ValueError(f"Invalid condition: {' '.join(condition_tokens)}")
        else:
            # WAIT | time
            self.time_value = ValueParser.parse(tokens[0])
            if not self.time_value:
                raise ValueError(f"Invalid time value: {tokens[0]}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the WAIT command."""
        if context.send_message:
            await context.send_message(
                f"Executing WAIT at {self.grid_position}", LogLevel.DEBUG
            )

        if self.while_condition:
            # WAIT WHILE condition
            while True:
                # Check cancellation
                if context.check_cancelled and context.check_cancelled():
                    break

                # Evaluate condition
                if context.send_message:
                    await context.send_message(
                        f"⚙️ WAIT WHILE evaluating condition: {self.while_condition}",
                        LogLevel.DEBUG,
                    )
                condition_result = await self.while_condition.evaluate(context)
                if context.send_message:
                    await context.send_message(
                        f"🔍 WAIT WHILE condition result: {condition_result}",
                        LogLevel.DEBUG,
                    )
                if not condition_result:
                    break

                # Wait a bit before checking again
                await asyncio.sleep(0.1)  # Check every 100ms

                # Increment steps to prevent infinite loops
                context.increment_steps()

                # Check for runaway execution
                if context.steps_executed > context.max_steps:
                    raise RuntimeError("Maximum steps exceeded")

        elif self.time_value:
            # Regular WAIT with time
            if context.send_message:
                await context.send_message(
                    f"⚙️ WAIT evaluating time: {self.time_value}", LogLevel.DEBUG
                )
            time_seconds = await self.time_value.evaluate(context)

            if not isinstance(time_seconds, (int, float)):
                raise ValueError(
                    f"Wait time must be a number, got {type(time_seconds)}"
                )

            wait_time = float(time_seconds)
            if wait_time < 0:
                raise ValueError(f"Wait time must be positive, got {wait_time}")

            if context.send_message:
                await context.send_message(
                    f"⏱️ Waiting for {wait_time} seconds...", LogLevel.INFO
                )

            # Wait with cancellation support
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < wait_time:
                if context.check_cancelled and context.check_cancelled():
                    break
                await asyncio.sleep(0.1)  # Check every 100ms

            context.increment_steps()
        else:
            raise ValueError("WAIT command has neither time nor WHILE condition")

    def __repr__(self) -> str:
        if self.while_condition:
            return f"WaitCommand(WHILE {self.while_condition})"
        return f"WaitCommand({self.time_value})"
