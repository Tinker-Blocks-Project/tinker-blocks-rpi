import asyncio
from typing import Callable, Awaitable, Optional, Protocol, TypeVar, Any
from .types import LogLevel

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


class WorkflowFunc(Protocol[T_co]):
    """Protocol for workflow functions."""

    async def __call__(
        self,
        send_message: Callable[[str, LogLevel], Awaitable[None]],
    ) -> T_co: ...


class ProcessController:
    """Manages execution of workflows with cancellation support."""

    def __init__(self, send_message: Callable[[str, LogLevel], Awaitable[None]]):
        self.send_message = send_message
        self._current_task: Optional[asyncio.Task] = None
        self._last_result: Any = None  # Store last workflow result
        self._cancellation_requested: bool = False

    async def run_workflow(
        self,
        workflow: WorkflowFunc[T],
        name: str = "Workflow",
    ) -> tuple[bool, Optional[T]]:
        """
        Run a workflow function.

        Args:
            workflow: Workflow function that takes send_message
            name: Name of the workflow for logging

        Returns:
            Tuple of (success: bool, result: Optional[T])
        """
        result = None
        self._cancellation_requested = False

        try:
            await self.send_message(f"Starting {name}...", LogLevel.INFO)

            # Create task that runs the workflow
            self._current_task = asyncio.create_task(workflow(self.send_message))

            result = await self._current_task
            self._last_result = result
            return True, result

        except asyncio.CancelledError:
            await self.send_message(f"\n❌ {name} was cancelled", LogLevel.ERROR)
            return False, None
        except Exception as e:
            await self.send_message(f"\n❌ {name} failed: {str(e)}", LogLevel.ERROR)
            return False, None
        finally:
            self._current_task = None
            self._cancellation_requested = False

    async def cancel(self):
        """Cancel the current running workflow."""
        if self._current_task and not self._current_task.done():
            self._cancellation_requested = True
            await self.send_message("🛑 Cancelling current process...", LogLevel.INFO)
            self._current_task.cancel()

            # Wait a bit for the task to actually cancel
            try:
                await asyncio.wait_for(self._current_task, timeout=0.5)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass  # Expected when task is cancelled or takes time to cleanup

        elif self._cancellation_requested:
            await self.send_message(
                "🛑 Cancellation already in progress...", LogLevel.INFO
            )
        else:
            await self.send_message("⚠️ No active process to cancel", LogLevel.WARNING)

    @property
    def is_running(self) -> bool:
        """Check if a workflow is currently running."""
        return self._current_task is not None and not self._current_task.done()

    @property
    def is_cancelling(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancellation_requested

    @property
    def last_result(self) -> Any:
        """Get the result from the last completed workflow."""
        return self._last_result
