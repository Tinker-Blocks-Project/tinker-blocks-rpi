"""Command definitions and registry for the interpreter pattern."""

from typing import Protocol, Dict
from engine.state import ExecutionState


class Command(Protocol):
    """Protocol for executable commands."""

    def execute(self, state: ExecutionState) -> None:
        """Execute the command and update the state."""
        ...

    @property
    def name(self) -> str:
        """Get the command name."""
        ...


class MoveForwardCommand:
    """Command to move forward in the current direction."""

    name = "MOVE_FORWARD"

    def execute(self, state: ExecutionState) -> None:
        """Move forward based on current direction."""
        directions = {
            "right": (1, 0),
            "down": (0, 1),
            "left": (-1, 0),
            "up": (0, -1),
        }
        dx, dy = directions[state.direction]
        state.move(dx, dy)


class TurnRightCommand:
    """Command to turn 90 degrees clockwise."""

    name = "TURN_RIGHT"

    def execute(self, state: ExecutionState) -> None:
        """Turn right (90 degrees clockwise)."""
        turns = {"right": "down", "down": "left", "left": "up", "up": "right"}
        state.direction = turns[state.direction]


class TurnLeftCommand:
    """Command to turn 90 degrees counter-clockwise."""

    name = "TURN_LEFT"

    def execute(self, state: ExecutionState) -> None:
        """Turn left (90 degrees counter-clockwise)."""
        turns = {"right": "up", "up": "left", "left": "down", "down": "right"}
        state.direction = turns[state.direction]


class CommandRegistry:
    """Registry for mapping command names to command instances."""

    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register the default set of commands."""
        default_commands = [
            MoveForwardCommand(),
            TurnRightCommand(),
            TurnLeftCommand(),
        ]

        for cmd in default_commands:
            self.register(cmd)
            # Also register common aliases
            if cmd.name == "MOVE_FORWARD":
                self.register_alias("FORWARD", cmd)
                self.register_alias("FWD", cmd)
            elif cmd.name == "TURN_RIGHT":
                self.register_alias("RIGHT", cmd)
            elif cmd.name == "TURN_LEFT":
                self.register_alias("LEFT", cmd)

    def register(self, command: Command) -> None:
        """Register a new command."""
        self._commands[command.name] = command

    def register_alias(self, alias: str, command: Command) -> None:
        """Register an alias for an existing command."""
        self._commands[alias] = command

    def get(self, name: str) -> Command | None:
        """Get a command by name (case-insensitive)."""
        return self._commands.get(name.upper())

    def has_command(self, name: str) -> bool:
        """Check if a command exists."""
        return name.upper() in self._commands
