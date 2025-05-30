import asyncio
import pytest
from core import ProcessController


@pytest.fixture
def mock_messages():
    """Fixture to track messages."""
    return []


@pytest.fixture
def mock_send_function(mock_messages):
    """Fixture for mock send function."""

    async def send(msg: str):
        mock_messages.append(msg)

    return send


@pytest.fixture
def controller(mock_send_function):
    """Fixture for ProcessController instance."""
    return ProcessController(mock_send_function)


@pytest.mark.asyncio
async def test_successful_workflow(controller, mock_messages):
    """Test that a successful workflow completes properly."""

    async def simple_workflow(send_message, check_cancelled):
        await send_message("Step 1")
        if check_cancelled():
            return
        await send_message("Step 2")
        await send_message("Complete")

    result = await controller.run_workflow(simple_workflow, "Test Workflow")

    assert result is True
    assert "Starting Test Workflow..." in mock_messages
    assert "Step 1" in mock_messages
    assert "Step 2" in mock_messages
    assert "Complete" in mock_messages


@pytest.mark.asyncio
async def test_workflow_cancellation(controller, mock_messages):
    """Test that workflow cancellation works properly."""

    async def long_workflow(send_message, check_cancelled):
        await send_message("Starting")

        for i in range(10):
            if check_cancelled():
                await send_message("Detected cancellation")
                return
            await send_message(f"Step {i}")
            await asyncio.sleep(0.1)

        await send_message("Should not reach here")

    # Start workflow and cancel it
    task = asyncio.create_task(controller.run_workflow(long_workflow, "Long Workflow"))
    await asyncio.sleep(0.15)  # Let it run a bit
    controller.cancel()
    result = await task

    assert result is False
    assert "Starting" in mock_messages
    # The controller adds the cancellation message, not the workflow
    assert any("was cancelled" in msg for msg in mock_messages)
    assert "Should not reach here" not in mock_messages


@pytest.mark.asyncio
async def test_workflow_error_handling(controller, mock_messages):
    """Test that workflow errors are handled properly."""

    async def failing_workflow(send_message, check_cancelled):
        await send_message("Starting")
        raise ValueError("Test error")

    result = await controller.run_workflow(failing_workflow, "Failing Workflow")

    assert result is False
    assert "Starting" in mock_messages
    assert any("failed: Test error" in msg for msg in mock_messages)


@pytest.mark.asyncio
async def test_is_running_property(controller):
    """Test the is_running property."""

    assert not controller.is_running

    async def slow_workflow(send_message, check_cancelled):
        await asyncio.sleep(0.2)

    task = asyncio.create_task(controller.run_workflow(slow_workflow, "Slow"))

    # Give a tiny bit of time for the task to start
    await asyncio.sleep(0.01)

    # Should be running during execution
    assert controller.is_running

    await task

    # Should not be running after completion
    assert not controller.is_running
