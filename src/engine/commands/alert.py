from typing import ClassVar
from dataclasses import dataclass
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext


@dataclass
class AlertOnCommand(Command):
    """ALERT_ON command - turns the buzzer on."""

    COMMAND_NAMES: ClassVar[list[str]] = ["ALERT_ON"]

    def parse_args(self, tokens: list[str]) -> None:
        """ALERT_ON takes no arguments."""
        if tokens:
            raise ValueError("ALERT_ON takes no arguments")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the ALERT_ON command."""
        if context.send_message:
            await context.send_message(
                f"Executing ALERT_ON at {self.grid_position}", LogLevel.DEBUG
            )

        # Control the buzzer using hardware interface
        if context.hardware:
            success = await context.hardware.control_buzzer("on")
            if not success and context.send_message:
                await context.send_message(
                    "⚠️ Hardware buzzer control failed", LogLevel.WARNING
                )

        context.increment_steps()

        if context.send_message:
            await context.send_message("🔊 Alert started", LogLevel.SUCCESS)

    def __repr__(self) -> str:
        return "AlertOnCommand()"


@dataclass
class AlertOffCommand(Command):
    """ALERT_OFF command - turns the buzzer off."""

    COMMAND_NAMES: ClassVar[list[str]] = ["ALERT_OFF"]

    def parse_args(self, tokens: list[str]) -> None:
        """ALERT_OFF takes no arguments."""
        if tokens:
            raise ValueError("ALERT_OFF takes no arguments")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the ALERT_OFF command."""
        if context.send_message:
            await context.send_message(
                f"Executing ALERT_OFF at {self.grid_position}", LogLevel.DEBUG
            )

        # Control the buzzer using hardware interface
        if context.hardware:
            success = await context.hardware.control_buzzer("off")
            if not success and context.send_message:
                await context.send_message(
                    "⚠️ Hardware buzzer control failed", LogLevel.WARNING
                )

        context.increment_steps()

        if context.send_message:
            await context.send_message("🔊 Alert stopped", LogLevel.SUCCESS)

    def __repr__(self) -> str:
        return "AlertOffCommand()"
