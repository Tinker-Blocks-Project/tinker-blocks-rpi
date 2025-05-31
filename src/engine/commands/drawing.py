from typing import ClassVar
from dataclasses import dataclass

from .base import Command
from ..context import ExecutionContext


@dataclass
class PenUpCommand(Command):
    """PEN_UP command - lifts the drawing pen."""

    COMMAND_NAMES: ClassVar[list[str]] = ["PEN_UP", "PENUP", "UP"]

    def parse_args(self, tokens: list[str]) -> None:
        """PEN_UP takes no arguments."""
        if tokens:
            raise ValueError("PEN_UP takes no arguments")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the PEN_UP command."""
        if context.send_message:
            await context.send_message(f"Executing PEN_UP at {self.grid_position}")

        context.pen_down = False
        context.increment_steps()

        if context.send_message:
            await context.send_message("Pen lifted")

    def __repr__(self) -> str:
        return "PenUpCommand()"


@dataclass
class PenDownCommand(Command):
    """PEN_DOWN command - lowers the drawing pen."""

    COMMAND_NAMES: ClassVar[list[str]] = ["PEN_DOWN", "PENDOWN", "DOWN"]

    def parse_args(self, tokens: list[str]) -> None:
        """PEN_DOWN takes no arguments."""
        if tokens:
            raise ValueError("PEN_DOWN takes no arguments")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the PEN_DOWN command."""
        if context.send_message:
            await context.send_message(f"Executing PEN_DOWN at {self.grid_position}")

        context.pen_down = True
        context.increment_steps()

        # Start tracking from current position
        if not context.path or context.path[-1] != context.position:
            context.path.append(context.position)

        if context.send_message:
            await context.send_message("Pen lowered")

    def __repr__(self) -> str:
        return "PenDownCommand()"
