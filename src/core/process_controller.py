import asyncio
from typing import Callable, Awaitable, Optional, Protocol, TypeVar, Any

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


class WorkflowFunc(Protocol[T_co]):
    """Protocol for workflow functions."""

    async def __call__(
        self,
        send_message: Callable[[str], Awaitable[None]],
        check_cancelled: Callable[[], bool],
    ) -> T_co: ...


class ProcessController:
    """Manages execution of workflows with cancellation support."""

    def __init__(self, send_message: Callable[[str], Awaitable[None]]):
        self.send_message = send_message
        self._current_task: Optional[asyncio.Task] = None
        self._cancelled = False
        self._last_result: Any = None  # Store last workflow result

    def check_cancelled(self) -> bool:
        """Check if the current process has been cancelled."""
        return self._cancelled

    async def run_workflow(
        self,
        workflow: WorkflowFunc[T],
        name: str = "Workflow",
    ) -> tuple[bool, Optional[T]]:
        """
        Run a workflow function.

        Args:
            workflow: Workflow function that takes send_message and check_cancelled
            name: Name of the workflow for logging

        Returns:
            Tuple of (success: bool, result: Optional[T])
        """
        self._cancelled = False
        result = None

        try:
            await self.send_message(f"Starting {name}...")

            # Create task that runs the workflow
            self._current_task = asyncio.create_task(
                workflow(self.send_message, self.check_cancelled)
            )

            result = await self._current_task
            self._last_result = result
            return True, result

        except asyncio.CancelledError:
            await self.send_message(f"\n❌ {name} was cancelled")
            return False, None
        except Exception as e:
            await self.send_message(f"\n❌ {name} failed: {str(e)}")
            return False, None
        finally:
            self._current_task = None

    def cancel(self):
        """Cancel the current running workflow."""
        self._cancelled = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    @property
    def is_running(self) -> bool:
        """Check if a workflow is currently running."""
        return self._current_task is not None and not self._current_task.done()

    @property
    def last_result(self) -> Any:
        """Get the result from the last completed workflow."""
        return self._last_result
