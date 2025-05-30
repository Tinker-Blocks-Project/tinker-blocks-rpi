"""Process controller for managing task execution."""

import asyncio
from typing import List, Callable, Awaitable, Optional
from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single task to be executed."""

    name: str
    func: Callable[..., Awaitable[None]]
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)


class ProcessController:
    """Manages execution of a sequence of tasks with cancellation support."""

    def __init__(self, send_message: Callable[[str], Awaitable[None]]):
        self.send_message = send_message
        self._current_task: Optional[asyncio.Task] = None
        self._cancelled = False

    async def run_tasks(self, tasks: List[Task]) -> bool:
        """
        Run a sequence of tasks.

        Args:
            tasks: List of tasks to execute

        Returns:
            True if all tasks completed successfully, False if cancelled or error
        """
        self._cancelled = False

        try:
            await self.send_message(f"Starting {len(tasks)} tasks...")

            for i, task in enumerate(tasks, 1):
                if self._cancelled:
                    await self.send_message("Process cancelled by user")
                    return False

                await self.send_message(f"\n**Task {i}/{len(tasks)}: {task.name}**")

                # Create and run the task
                self._current_task = asyncio.create_task(self._run_single_task(task))

                try:
                    await self._current_task
                except asyncio.CancelledError:
                    await self.send_message(f"Task '{task.name}' was cancelled")
                    return False

                # Check for cancellation between tasks
                await asyncio.sleep(0)  # Yield control

            await self.send_message("\n✅ All tasks completed successfully!")
            return True

        except Exception as e:
            await self.send_message(f"\n❌ Error: {str(e)}")
            return False
        finally:
            self._current_task = None

    async def _run_single_task(self, task: Task):
        """Run a single task with error handling."""
        try:
            await task.func(*task.args, **task.kwargs)
            await self.send_message(f"✓ Task '{task.name}' completed")
        except Exception as e:
            await self.send_message(f"✗ Task '{task.name}' failed: {str(e)}")
            raise

    def cancel(self):
        """Cancel the current running process."""
        self._cancelled = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    @property
    def is_running(self) -> bool:
        """Check if a process is currently running."""
        return self._current_task is not None and not self._current_task.done()


# Global process controller instance
_process_controller: Optional[ProcessController] = None


def initialize_controller(send_func: Callable[[str], Awaitable[None]]):
    """Initialize the global process controller."""
    global _process_controller
    _process_controller = ProcessController(send_func)


def get_controller() -> Optional[ProcessController]:
    """Get the global process controller instance."""
    return _process_controller
