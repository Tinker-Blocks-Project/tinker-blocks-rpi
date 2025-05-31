"""Command executor - executes the parsed command tree."""

from typing import Callable, Awaitable

from .commands import Command
from .context import ExecutionContext, SensorInterface


class Executor:
    """Executes a command tree."""

    def __init__(
        self,
        send_message: Callable[[str], Awaitable[None]] | None = None,
        check_cancelled: Callable[[], bool] | None = None,
        sensors: SensorInterface | None = None,
    ):
        """Initialize the executor.

        Args:
            send_message: Callback for sending status messages
            check_cancelled: Callback for checking if execution should be cancelled
            sensors: Sensor interface for getting sensor readings
        """
        self.send_message = send_message
        self.check_cancelled = check_cancelled
        self.sensors = sensors

    async def execute(self, commands: list[Command]) -> ExecutionContext:
        """Execute a list of commands.

        Args:
            commands: List of commands to execute

        Returns:
            The execution context after execution
        """
        # Create execution context
        context = ExecutionContext()
        context.send_message = self.send_message
        context.check_cancelled = self.check_cancelled

        if self.sensors:
            context.sensors = self.sensors

        # Execute each command
        try:
            for command in commands:
                # Check for cancellation
                if self.check_cancelled and self.check_cancelled():
                    if self.send_message:
                        await self.send_message("Execution cancelled by user")
                    break

                # Execute the command
                await command.execute(context)

        except Exception as e:
            if self.send_message:
                await self.send_message(f"Execution error: {str(e)}")
            raise

        return context

    # Extra
    async def execute_single(
        self,
        command: Command,
        context: ExecutionContext | None = None,
    ) -> ExecutionContext:
        """Execute a single command, optionally with an existing context.

        Args:
            command: The command to execute
            context: Optional existing context to use

        Returns:
            The execution context after execution
        """
        if context is None:
            context = ExecutionContext()

        # Always set the callbacks
        context.send_message = self.send_message
        context.check_cancelled = self.check_cancelled

        if self.sensors:
            context.sensors = self.sensors

        await command.execute(context)
        return context
