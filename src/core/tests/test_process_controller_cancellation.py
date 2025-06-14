"""Integration tests for ProcessController with asyncio cancellation."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from core.process_controller import ProcessController
from core.types import LogLevel

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestProcessControllerCancellation:
    """Test ProcessController cancellation behavior."""

    @pytest.fixture
    def controller(self):
        """Create a ProcessController for testing."""
        send_message = AsyncMock()
        return ProcessController(send_message)

    async def test_cancel_running_workflow(self, controller):
        """Test cancelling a running workflow."""

        # Create a long-running workflow
        async def long_workflow(send_message):
            await send_message("Starting long task...", LogLevel.INFO)
            await asyncio.sleep(2)  # 2 second sleep
            await send_message("Long task completed", LogLevel.INFO)
            return "completed"

        # Start the workflow in a task
        workflow_task = asyncio.create_task(
            controller.run_workflow(long_workflow, "Long Task")
        )

        # Wait a bit to ensure it starts
        await asyncio.sleep(0.05)

        # Should be running
        assert controller.is_running

        # Cancel it
        await controller.cancel()

        # Wait for the workflow task to complete
        success, result = await workflow_task

        # Should not be running anymore
        assert not controller.is_running

        # Should have been cancelled
        assert success is False
        assert result is None

        # Should have sent cancellation message
        controller.send_message.assert_any_call(
            "🛑 Cancelling current process...", LogLevel.INFO
        )

    async def test_cancel_no_running_workflow(self, controller):
        """Test cancelling when no workflow is running."""
        # Should not be running
        assert not controller.is_running

        # Try to cancel
        await controller.cancel()

        # Should send appropriate message
        controller.send_message.assert_any_call(
            "⚠️ No active process to cancel", LogLevel.WARNING
        )

    async def test_cancel_completed_workflow(self, controller):
        """Test cancelling a workflow that has already completed."""

        # Create a quick workflow
        async def quick_workflow(send_message):
            await send_message("Quick task", LogLevel.INFO)
            return "done"

        # Run and complete the workflow
        success, result = await controller.run_workflow(quick_workflow, "Quick Task")

        # Should have completed successfully
        assert success is True
        assert result == "done"
        assert not controller.is_running

        # Try to cancel the completed workflow
        await controller.cancel()

        # Should send appropriate message
        controller.send_message.assert_any_call(
            "⚠️ No active process to cancel", LogLevel.WARNING
        )

    async def test_is_running_property(self, controller):
        """Test the is_running property behavior."""
        # Should not be running initially
        assert not controller.is_running

        # Create a workflow
        async def test_workflow(send_message):
            await asyncio.sleep(0.1)
            return "test"

        # Start workflow
        task = asyncio.create_task(
            controller.run_workflow(test_workflow, "Test Workflow")
        )

        # Wait a bit
        await asyncio.sleep(0.05)

        # Should be running
        assert controller.is_running

        # Wait for completion
        await task

        # Should not be running anymore
        assert not controller.is_running

    async def test_workflow_exception_handling(self, controller):
        """Test that workflow exceptions are handled properly."""

        # Create a workflow that raises an exception
        async def failing_workflow(send_message):
            await send_message("About to fail", LogLevel.INFO)
            raise ValueError("Test error")

        # Run the workflow
        success, result = await controller.run_workflow(
            failing_workflow, "Failing Task"
        )

        # Should have failed
        assert success is False
        assert result is None
        assert not controller.is_running

        # Should have sent error message (check the actual format used)
        controller.send_message.assert_any_call(
            "\n❌ Failing Task failed: Test error", LogLevel.ERROR
        )


if __name__ == "__main__":
    pytest.main([__file__])
