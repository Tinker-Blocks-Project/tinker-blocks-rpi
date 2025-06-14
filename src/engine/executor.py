"""Command executor - executes the parsed command tree."""

from typing import Callable, Awaitable, Union, TYPE_CHECKING
from core.types import LogLevel

from .commands import Command
from .context import ExecutionContext, SensorInterface

if TYPE_CHECKING:
    from .hardware import HardwareInterface


class Executor:
    """Executes a command tree."""

    def __init__(
        self,
        send_message: Callable[[str, LogLevel], Awaitable[None]] | None = None,
        sensors: SensorInterface | None = None,
        hardware: Union["HardwareInterface", None] = None,
    ):
        """Initialize the executor.

        Args:
            send_message: Callback for sending status messages
            sensors: Sensor interface for getting sensor readings
            hardware: Hardware interface for actual car control
        """
        self.send_message = send_message
        self.sensors = sensors
        self.hardware = hardware

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

        if self.sensors:
            context.sensors = self.sensors

        if self.hardware:
            context.hardware = self.hardware

        for command in commands:
            await command.execute(context)

        return context

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

        if self.sensors:
            context.sensors = self.sensors

        if self.hardware:
            context.hardware = self.hardware

        await command.execute(context)
        return context
