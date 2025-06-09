"""Control flow commands: LOOP, IF, ELSE."""

from typing import ClassVar
from dataclasses import dataclass, field
from core.types import LogLevel

from .base import Command
from ..context import ExecutionContext
from ..values import Value, ValueParser, ExpressionParser


@dataclass
class LoopCommand(Command):
    """LOOP command - repeats nested commands."""

    COMMAND_NAMES: ClassVar[list[str]] = ["LOOP", "REPEAT", "FOR"]

    # Command-specific attributes
    count_value: Value | None = None
    while_condition: Value | None = None

    def parse_args(self, tokens: list[str]) -> None:
        """Parse LOOP arguments.

        Formats:
        - LOOP | 5
        - LOOP | FOREVER
        - LOOP | WHILE | condition
        """
        if not tokens:
            raise ValueError("LOOP requires count or WHILE condition")

        # Check for WHILE modifier
        if tokens[0].upper() == "WHILE":
            # LOOP | WHILE | condition
            if len(tokens) < 2:
                raise ValueError("WHILE requires a condition")

            condition_tokens = tokens[1:]
            self.while_condition = ExpressionParser.parse_tokens(condition_tokens)
            if not self.while_condition:
                raise ValueError(f"Invalid condition: {' '.join(condition_tokens)}")
        else:
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

        if self.while_condition:
            # LOOP WHILE condition
            while True:
                # Check cancellation
                if context.check_cancelled and context.check_cancelled():
                    break

                # Evaluate condition
                condition_result = await self.while_condition.evaluate(context)
                if not condition_result:
                    break

                # Execute nested commands
                for command in self.nested_commands:
                    if context.check_cancelled and context.check_cancelled():
                        break
                    await command.execute(context)

                # Check for runaway execution
                if context.steps_executed > context.max_steps:
                    raise RuntimeError("Maximum steps exceeded")

        elif self.count_value:
            # Regular LOOP with count
            count = await self.count_value.evaluate(context)

            # Handle TRUE/FALSE for infinite/no loop
            if isinstance(count, bool):
                if count:  # TRUE = infinite loop
                    while True:
                        # Check cancellation
                        if context.check_cancelled and context.check_cancelled():
                            break

                        # Execute nested commands
                        for command in self.nested_commands:
                            if context.check_cancelled and context.check_cancelled():
                                break
                            await command.execute(context)

                        # Check for runaway execution
                        if context.steps_executed > context.max_steps:
                            raise RuntimeError("Maximum steps exceeded")
                else:  # FALSE = no loop
                    return
            elif isinstance(count, (int, float)):
                # Fixed count loop
                iterations = int(count)
                for i in range(iterations):
                    # Check cancellation
                    if context.check_cancelled and context.check_cancelled():
                        break

                    # Execute nested commands
                    for command in self.nested_commands:
                        if context.check_cancelled and context.check_cancelled():
                            break
                        await command.execute(context)
            else:
                raise ValueError(
                    f"Loop count must be a number or boolean, got {type(count)}"
                )
        else:
            raise ValueError("LOOP command has neither count nor WHILE condition")

    def __repr__(self) -> str:
        if self.while_condition:
            return f"LoopCommand(WHILE {self.while_condition}, {len(self.nested_commands)} commands)"
        return f"LoopCommand({self.count_value}, {len(self.nested_commands)} commands)"


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
        condition_result = await self.condition.evaluate(context)

        if context.send_message:
            await context.send_message(
                f"IF condition evaluated to: {condition_result}", LogLevel.DEBUG
            )

        if condition_result:
            # Execute IF block
            for command in self.nested_commands:
                if context.check_cancelled and context.check_cancelled():
                    break
                await command.execute(context)
        else:
            # Execute ELSE block if present
            for command in self.else_commands:
                if context.check_cancelled and context.check_cancelled():
                    break
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
