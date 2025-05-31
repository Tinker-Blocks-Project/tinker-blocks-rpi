"""Interpreter for executing block commands."""

from typing import List, Callable, Optional, Awaitable
from engine.state import ExecutionState
from engine.commands import CommandRegistry


class Interpreter:
    """Interpreter that executes commands from a grid."""

    def __init__(self, command_registry: Optional[CommandRegistry] = None):
        """Initialize the interpreter with a command registry."""
        self.registry = command_registry or CommandRegistry()
        self.state = ExecutionState()
        self._cancelled = False

    def reset(self) -> None:
        """Reset the interpreter state."""
        self.state = ExecutionState()
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel execution."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if execution has been cancelled."""
        return self._cancelled

    async def execute_grid(
        self,
        grid: List[List[str]],
        on_command: Optional[Callable[[int, int, str], Awaitable[None]]] = None,
        on_unknown_command: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> ExecutionState:
        """
        Execute commands from a 2D grid.

        Args:
            grid: 2D list of command strings
            on_command: Async callback for each command execution (row, col, command)
            on_unknown_command: Async callback for unknown commands

        Returns:
            The final execution state
        """
        self.reset()

        for row_idx, row in enumerate(grid):
            if self.is_cancelled:
                break

            for col_idx, cell in enumerate(row):
                if self.is_cancelled:
                    break

                # Skip empty cells
                if not cell or not cell.strip():
                    continue

                command_name = cell.strip()

                # Notify about command execution
                if on_command:
                    await on_command(row_idx, col_idx, command_name)

                # Get and execute command
                command = self.registry.get(command_name)
                if command:
                    command.execute(self.state)
                    self.state.record_step(command_name.upper())
                else:
                    # Handle unknown command
                    if on_unknown_command:
                        await on_unknown_command(command_name)

        return self.state

    def get_state(self) -> ExecutionState:
        """Get the current execution state."""
        return self.state
