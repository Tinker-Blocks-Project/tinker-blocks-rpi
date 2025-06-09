from typing import ClassVar
from dataclasses import dataclass
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ExpressionParser


@dataclass
class SetCommand(Command):
    """SET command - assigns a value to a variable."""

    COMMAND_NAMES: ClassVar[list[str]] = ["SET", "ASSIGN", "LET"]

    # Command-specific attributes
    variable_name: str | None = None
    value_expression: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse SET arguments.

        Formats:
        - SET | X | 5
        - SET | Y | DISTANCE
        - SET | Z | X | + | 2
        - SET | A | DISTANCE | < | 30
        """
        if len(tokens) < 2:
            raise ValueError("SET requires variable name and value")

        # First token is variable name
        self.variable_name = tokens[0].upper()

        # Rest is the value/expression
        value_tokens = tokens[1:]
        self.value_expression = ExpressionParser.parse_tokens(value_tokens)

        if not self.value_expression:
            raise ValueError(f"Invalid value expression: {' '.join(value_tokens)}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the SET command."""
        if context.send_message:
            await context.send_message(
                f"Executing SET {self.variable_name} at {self.grid_position}",
                LogLevel.DEBUG,
            )

        if not self.variable_name or not self.value_expression:
            raise ValueError("SET command missing variable name or value")

        # Evaluate the expression
        if context.send_message:
            await context.send_message(
                f"⚙️ SET evaluating expression: {self.value_expression}", LogLevel.DEBUG
            )
        value = await self.value_expression.evaluate(context)

        if context.send_message:
            await context.send_message(
                f"🔍 SET expression result: {value} (type: {type(value).__name__})",
                LogLevel.DEBUG,
            )

        # Convert string values to appropriate types
        if isinstance(value, str):
            # Try to convert string to number
            try:
                value = float(value)
            except ValueError:
                # If it's not a number, treat as boolean
                value = value.upper() in ("TRUE", "YES", "1")

        # Ensure value is Number | bool
        if not isinstance(value, (int, float, bool)):
            raise ValueError(
                f"Variable value must be number or boolean, got {type(value)}"
            )

        # Set the variable
        await context.set_variable(self.variable_name, value)

        if context.send_message:
            await context.send_message(
                f"✅ SET complete: {self.variable_name} = {value}", LogLevel.SUCCESS
            )

    def __repr__(self) -> str:
        return f"SetCommand({self.variable_name} = {self.value_expression})"
