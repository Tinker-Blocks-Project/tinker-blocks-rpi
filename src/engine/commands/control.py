"""Control flow commands: LOOP, WHILE, IF, ELSE."""

import asyncio
from typing import ClassVar
from dataclasses import dataclass, field
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, ExpressionParser


@dataclass
class LoopCommand(Command):
    """LOOP command - repeats nested commands a specified number of times."""

    COMMAND_NAMES: ClassVar[list[str]] = ["LOOP", "REPEAT", "FOR"]

    # Command-specific attributes
    count_value: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse LOOP arguments.

        Formats:
        - LOOP | 5
        - LOOP | TRUE (infinite loop)
        - LOOP | FALSE (no loop)
        """
        if not tokens:
            raise ValueError("LOOP requires a count")

        # LOOP | count
        self.count_value = ValueParser.parse(tokens[0])
        if not self.count_value:
            raise ValueError(f"Invalid loop count: {tokens[0]}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the LOOP command."""
        if context.send_message:
            await context.send_message(
                f"Executing LOOP at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.count_value:
            raise ValueError("LOOP command has no count")

        if context.send_message:
            await context.send_message(
                f"⚙️ LOOP evaluating count: {self.count_value}", LogLevel.DEBUG
            )
        count = await self.count_value.evaluate(context)
        if context.send_message:
            await context.send_message(
                f"🔢 LOOP count evaluated to: {count}", LogLevel.DEBUG
            )

        # Handle TRUE/FALSE for infinite/no loop
        if isinstance(count, bool):
            if count:  # TRUE = infinite loop
                while True:
                    # Execute nested commands
                    for command in self.nested_commands:
                        await command.execute(context)

                    # Yield control to allow cancellation
                    await asyncio.sleep(0)

                    # Check for runaway execution
                    if context.steps_executed > context.max_steps:
                        raise RuntimeError("Maximum steps exceeded")
            else:  # FALSE = no loop
                return
        elif isinstance(count, (int, float)):
            # Fixed count loop
            iterations = int(count)
            for i in range(iterations):
                # Execute nested commands
                for command in self.nested_commands:
                    await command.execute(context)

                # Yield control to allow cancellation
                await asyncio.sleep(0)
        else:
            raise ValueError(
                f"Loop count must be a number or boolean, got {type(count)}"
            )

    def __repr__(self) -> str:
        return f"LoopCommand({self.count_value}, {len(self.nested_commands)} commands)"


@dataclass
class WhileCommand(Command):
    """WHILE command - repeats nested commands while a condition is true."""

    COMMAND_NAMES: ClassVar[list[str]] = ["WHILE"]

    # Command-specific attributes
    condition: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse WHILE arguments.

        Format:
        - WHILE | condition
        """
        if not tokens:
            raise ValueError("WHILE requires a condition")

        self.condition = ExpressionParser.parse_tokens(tokens)
        if not self.condition:
            raise ValueError(f"Invalid condition: {' '.join(tokens)}")

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the WHILE command."""
        if context.send_message:
            await context.send_message(
                f"Executing WHILE at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.condition:
            raise ValueError("WHILE command has no condition")

        # WHILE condition loop
        while True:
            # Evaluate condition
            if context.send_message:
                await context.send_message(
                    f"⚙️ WHILE evaluating condition: {self.condition}",
                    LogLevel.DEBUG,
                )
            condition_result = await self.condition.evaluate(context)
            if context.send_message:
                await context.send_message(
                    f"🔍 WHILE condition result: {condition_result}",
                    LogLevel.DEBUG,
                )
            if not condition_result:
                break

            # Execute nested commands
            for command in self.nested_commands:
                await command.execute(context)

            # Yield control to allow cancellation
            await asyncio.sleep(0)

            # Check for runaway execution
            if context.steps_executed > context.max_steps:
                raise RuntimeError("Maximum steps exceeded")

    def __repr__(self) -> str:
        return f"WhileCommand({self.condition}, {len(self.nested_commands)} commands)"


@dataclass
class IfCommand(Command):
    """IF command - conditional execution."""

    COMMAND_NAMES: ClassVar[list[str]] = ["IF"]

    # Command-specific attributes
    condition: Value | None = None
    else_commands: list[Command] = field(default_factory=list)

    def parse_args(self, tokens: list[str]) -> None:
        """Parse IF arguments.

        Format:
        - IF | condition
        """
        if not tokens:
            raise ValueError("IF requires a condition")

        self.condition = ExpressionParser.parse_tokens(tokens)
        if not self.condition:
            raise ValueError(f"Invalid condition: {' '.join(tokens)}")

    def add_else_command(self, command: Command) -> None:
        """Add a command to the ELSE block."""
        self.else_commands.append(command)

    async def execute(self, context: ExecutionContext) -> None:
        """Execute the IF command."""
        if context.send_message:
            await context.send_message(
                f"Executing IF at {self.grid_position}", LogLevel.DEBUG
            )

        if not self.condition:
            raise ValueError("IF command has no condition")

        # Evaluate condition
        if context.send_message:
            await context.send_message(
                f"⚙️ IF evaluating condition: {self.condition}", LogLevel.DEBUG
            )
        condition_result = await self.condition.evaluate(context)

        if context.send_message:
            await context.send_message(
                f"🔍 IF condition result: {condition_result}", LogLevel.DEBUG
            )

        if condition_result:
            # Execute IF block
            for command in self.nested_commands:
                await command.execute(context)
        else:
            # Execute ELSE block if present
            for command in self.else_commands:
                await command.execute(context)

    def __repr__(self) -> str:
        else_info = (
            f", {len(self.else_commands)} else commands" if self.else_commands else ""
        )
        return f"IfCommand({self.condition}, {len(self.nested_commands)} commands{else_info})"


@dataclass
class ElseCommand(Command):
    """ELSE command - marks the else block of an IF."""

    COMMAND_NAMES: ClassVar[list[str]] = ["ELSE"]

    def parse_args(self, tokens: list[str]) -> None:
        """ELSE takes no arguments."""
        if tokens:
            raise ValueError("ELSE takes no arguments")

    async def execute(self, context: ExecutionContext) -> None:
        """ELSE is not executed directly - it's a marker."""
        raise RuntimeError("ELSE command should not be executed directly")

    def __repr__(self) -> str:
        return "ElseCommand()"
