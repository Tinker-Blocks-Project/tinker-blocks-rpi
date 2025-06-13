from typing import ClassVar
from dataclasses import dataclass
import asyncio
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser


@dataclass
class WaitCommand(Command):
    """WAIT command - pauses execution for a specified time."""

    COMMAND_NAMES: ClassVar[list[str]] = ["WAIT", "PAUSE", "SLEEP", "DELAY"]

    # Command-specific attributes
    time_value: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse WAIT arguments.

        Formats:
        - WAIT | 2
        - WAIT | 0.5
        """
        if not tokens:
            raise ValueError("WAIT requires time in seconds")

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

        if not self.time_value:
            raise ValueError("WAIT command has no time")

        # Regular WAIT with time
        if context.send_message:
            await context.send_message(
                f"⚙️ WAIT evaluating time: {self.time_value}", LogLevel.DEBUG
            )
        time_seconds = await self.time_value.evaluate(context)

        if not isinstance(time_seconds, (int, float)):
            raise ValueError(f"Wait time must be a number, got {type(time_seconds)}")

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

    def __repr__(self) -> str:
        return f"WaitCommand({self.time_value})"
