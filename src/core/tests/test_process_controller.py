import asyncio
import pytest
from core import ProcessController
from core.types import LogLevel


@pytest.fixture
def mock_messages():
    """Fixture to track messages."""
    return []


@pytest.fixture
def mock_send_function(mock_messages):
    """Fixture for mock send function."""

    async def send(msg: str, level):
        mock_messages.append(msg)

    return send


@pytest.fixture
def controller(mock_send_function):
    """Fixture for ProcessController instance."""
    return ProcessController(mock_send_function)


@pytest.mark.asyncio
async def test_successful_workflow():
    """Test successful workflow execution."""
    messages = []

    async def mock_send(msg, level):
        messages.append(msg)

    controller = ProcessController(mock_send)

    async def simple_workflow(send_message, check_cancelled):
        await send_message("Task started", LogLevel.INFO)
        await asyncio.sleep(0.01)  # Simulate work
        await send_message("Task completed", LogLevel.INFO)
        return "test_result"

    success, result = await controller.run_workflow(simple_workflow, "Test Task")

    assert success is True
    assert result == "test_result"
    assert "Starting Test Task..." in messages
    assert "Task started" in messages
    assert "Task completed" in messages
    assert not controller.is_running


@pytest.mark.asyncio
async def test_workflow_cancellation():
    """Test workflow cancellation."""
    messages = []

    async def mock_send(msg, level):
        messages.append(msg)

    controller = ProcessController(mock_send)

    async def long_workflow(send_message, check_cancelled):
        await send_message("Starting long task", LogLevel.INFO)

        for i in range(10):
            if check_cancelled():
                await send_message("Cancelled!", LogLevel.INFO)
                return
            await asyncio.sleep(0.01)

        await send_message("Should not reach here", LogLevel.INFO)

    # Start workflow
    workflow_task = asyncio.create_task(
        controller.run_workflow(long_workflow, "Long Task")
    )

    # Wait a bit then cancel
    await asyncio.sleep(0.02)
    controller.cancel()

    # Wait for completion
    success, result = await workflow_task

    assert success is False
    assert result is None
    assert any("Long Task was cancelled" in msg for msg in messages)
    assert "Should not reach here" not in messages


@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Test workflow error handling."""
    messages = []

    async def mock_send(msg, level):
        messages.append(msg)

    controller = ProcessController(mock_send)

    async def failing_workflow(send_message, check_cancelled):
        await send_message("About to fail", LogLevel.INFO)
        raise ValueError("Test error")

    success, result = await controller.run_workflow(failing_workflow, "Failing Task")

    assert success is False
    assert result is None
    assert any("❌ Failing Task failed: Test error" in msg for msg in messages)


@pytest.mark.asyncio
async def test_is_running_property():
    """Test is_running property."""
    messages = []

    async def mock_send(msg, level):
        messages.append(msg)

    controller = ProcessController(mock_send)

    async def check_running_workflow(send_message, check_cancelled):
        # Controller should be running at this point
        assert controller.is_running
        await asyncio.sleep(0.01)

    assert not controller.is_running

    await controller.run_workflow(check_running_workflow, "Running Check")

    assert not controller.is_running
