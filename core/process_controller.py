import asyncio
from typing import Callable, Awaitable, Optional, Protocol


class WorkflowFunc(Protocol):
    """Protocol for workflow functions."""

    async def __call__(
        self,
        send_message: Callable[[str], Awaitable[None]],
        check_cancelled: Callable[[], bool],
    ) -> None: ...


class ProcessController:
    """Manages execution of workflows with cancellation support."""

    def __init__(self, send_message: Callable[[str], Awaitable[None]]):
        self.send_message = send_message
        self._current_task: Optional[asyncio.Task] = None
        self._cancelled = False

    def check_cancelled(self) -> bool:
        """Check if the current process has been cancelled."""
        return self._cancelled

    async def run_workflow(
        self,
        workflow: WorkflowFunc,
        name: str = "Workflow",
    ) -> bool:
        """
        Run a workflow function.

        Args:
            workflow: Workflow function that takes send_message and check_cancelled
            name: Name of the workflow for logging

        Returns:
            True if workflow completed successfully, False if cancelled or error
        """
        self._cancelled = False

        try:
            await self.send_message(f"Starting {name}...")

            # Create task that runs the workflow
            self._current_task = asyncio.create_task(
                workflow(self.send_message, self.check_cancelled)
            )

            await self._current_task
            return True

        except asyncio.CancelledError:
            await self.send_message(f"\n❌ {name} was cancelled")
            return False
        except Exception as e:
            await self.send_message(f"\n❌ {name} failed: {str(e)}")
            return False
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
