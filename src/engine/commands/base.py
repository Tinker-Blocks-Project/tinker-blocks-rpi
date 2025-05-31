"""Base command class and registry."""

from abc import ABC, abstractmethod
from typing import ClassVar, Type
from dataclasses import dataclass, field

from ..context import ExecutionContext
from ..types import GridPosition


@dataclass
class Command(ABC):
    """Abstract base class for all commands."""

    # Class-level attributes to be overridden by subclasses
    COMMAND_NAMES: ClassVar[list[str]] = []  # e.g., ["MOVE", "FORWARD", "FWD"]

    # Instance attributes
    grid_position: GridPosition = field(default_factory=lambda: GridPosition(0, 0))
    nested_commands: list["Command"] = field(default_factory=list)

    @abstractmethod
    def parse_args(self, tokens: list[str]) -> None:
        """Parse command arguments from tokens.

        Args:
            tokens: List of tokens after the command name
        """
        pass

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> None:
        """Execute the command.

        Args:
            context: The execution context
        """
        pass

    def add_nested_command(self, command: "Command") -> None:
        """Add a nested command (for control flow commands)."""
        self.nested_commands.append(command)

    def get_nested_commands(self) -> list["Command"]:
        """Get all nested commands."""
        return self.nested_commands

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}(pos={self.grid_position})"


class CommandRegistry:
    """Registry for all available commands."""

    _commands: dict[str, Type[Command]] = {}

    @classmethod
    def register(cls, command_class: Type[Command]) -> None:
        """Register a command class.

        Args:
            command_class: The command class to register
        """
        for name in command_class.COMMAND_NAMES:
            cls._commands[name.upper()] = command_class

    @classmethod
    def get_command_class(cls, name: str) -> Type[Command] | None:
        """Get a command class by name.

        Args:
            name: The command name (case-insensitive)

        Returns:
            The command class or None if not found
        """
        return cls._commands.get(name.upper())

    @classmethod
    def create_command(
        cls, name: str, tokens: list[str], position: GridPosition
    ) -> Command | None:
        """Create a command instance from name and tokens.

        Args:
            name: The command name
            tokens: The argument tokens
            position: The grid position

        Returns:
            A command instance or None if not recognized
        """
        command_class = cls.get_command_class(name)
        if command_class:
            command = command_class(grid_position=position)
            command.parse_args(tokens)
            return command
        return None

    @classmethod
    def get_all_command_names(cls) -> list[str]:
        """Get all registered command names."""
        return list(cls._commands.keys())
