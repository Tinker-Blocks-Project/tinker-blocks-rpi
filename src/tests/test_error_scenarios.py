"""Tests for error scenarios and edge cases."""

import asyncio
import pytest
from unittest.mock import patch
from core import ProcessController
from core.types import LogLevel
from engine.workflow import engine_workflow
from vision.workflow import ocr_grid_workflow


@pytest.mark.asyncio
async def test_engine_with_no_grid():
    """Test engine workflow with no grid provided."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Run engine with no grid
    success, result = await controller.run_workflow(
        lambda send_message, check_cancelled: engine_workflow(
            send_message, check_cancelled, None
        ),
        "Engine No Grid",
    )

    assert success is True
    assert result is not None
    assert result["success"] is False
    assert result["error"] == "No grid data provided"
    assert any("No grid data provided" in msg for msg in messages)


@pytest.mark.asyncio
async def test_engine_with_invalid_commands():
    """Test engine workflow with invalid/unknown commands."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Grid with invalid commands
    invalid_grid = [
        ["FORWARD", "INVALID_CMD", "RIGHT"],
        ["UNKNOWN", "LEFT", "NOT_A_COMMAND"],
    ]

    success, result = await controller.run_workflow(
        lambda send_message, check_cancelled: engine_workflow(
            send_message, check_cancelled, invalid_grid
        ),
        "Invalid Commands",
    )

    assert success is True
    assert result is not None
    assert result["success"] is False  # Should fail with unknown commands

    # Should have error about unknown command
    assert "Unknown command" in result["error"]


@pytest.mark.asyncio
async def test_workflow_exception_handling():
    """Test workflow exception handling."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Workflow that throws exception
    async def failing_workflow(send_message, check_cancelled):
        await send_message("About to fail...", LogLevel.INFO)
        raise RuntimeError("Catastrophic failure!")

    success, result = await controller.run_workflow(failing_workflow, "Exception Test")

    assert success is False
    assert result is None
    assert any("failed: Catastrophic failure!" in msg for msg in messages)


@pytest.mark.asyncio
async def test_workflow_timeout_simulation():
    """Test workflow with simulated timeout/long running task."""
    messages = []
    cancelled = False

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    async def slow_workflow(send_message, check_cancelled):
        nonlocal cancelled
        await send_message("Starting slow task...", LogLevel.INFO)

        # Simulate long running task with cancellation checks
        for i in range(100):
            if check_cancelled():
                cancelled = True
                await send_message("Task cancelled during execution", LogLevel.INFO)
                return None

            if i % 10 == 0:
                await send_message(f"Progress: {i}%", LogLevel.INFO)

            await asyncio.sleep(0.001)  # Small delay

        await send_message("Task completed!", LogLevel.INFO)
        return {"completed": True}

    # Start and quickly cancel
    task = asyncio.create_task(controller.run_workflow(slow_workflow, "Slow Task"))

    await asyncio.sleep(0.02)  # Increased to ensure it starts
    controller.cancel()

    success, result = await task

    assert success is False
    # Just check that cancellation happened
    assert any("was cancelled" in msg for msg in messages)


@pytest.mark.asyncio
async def test_ocr_workflow_with_missing_image():
    """Test OCR workflow when image file is missing."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    with (
        patch("vision.workflow.capture_image_client") as mock_capture,
        patch("vision.workflow.Image.from_file") as mock_from_file,
    ):
        # Setup mocks
        mock_capture.return_value = "test_image.jpg"
        mock_from_file.side_effect = FileNotFoundError("Image not found")

        # Create a mock OCR engine
        from unittest.mock import AsyncMock

        mock_ocr = AsyncMock()

        success, result = await controller.run_workflow(
            lambda send_message, check_cancelled: ocr_grid_workflow(
                mock_ocr, send_message, check_cancelled
            ),
            "Missing Image Test",
        )

        assert success is True  # Workflow completes but returns empty grid
        assert result is not None
        assert result.blocks == []  # Empty grid due to error
        assert any(
            "Image processing failed: Image not found" in msg for msg in messages
        )


@pytest.mark.asyncio
async def test_concurrent_workflow_attempts():
    """Test that controller prevents concurrent workflow execution."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    async def slow_workflow(send_message, check_cancelled):
        await send_message("Slow workflow started", LogLevel.INFO)
        await asyncio.sleep(0.1)
        await send_message("Slow workflow finished", LogLevel.INFO)
        return {"done": True}

    # Start first workflow
    task1 = asyncio.create_task(controller.run_workflow(slow_workflow, "First"))

    # Small delay to ensure first starts
    await asyncio.sleep(0.01)

    # Verify controller is running
    assert controller.is_running is True

    # Try to start second workflow (should be rejected in main.py logic)
    # This test verifies the is_running property works correctly
    assert controller.is_running is True

    # Wait for first to complete
    success1, result1 = await task1
    assert success1 is True

    # Now should be able to run another
    assert controller.is_running is False


@pytest.mark.asyncio
async def test_empty_and_edge_case_grids():
    """Test engine with various edge case grids."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Test cases
    test_grids = [
        # Empty grid
        ([[], []], "Empty rows"),
        # Single cell
        ([["MOVE"]], "Single cell"),
        # Only empty strings
        ([["", ""], ["", ""]], "All empty cells"),
        # Mixed valid/empty
        ([["MOVE", ""], ["", ""], ["TURN", "RIGHT"]], "Mixed cells"),
        # Very large grid (performance test)
        ([["MOVE"] for _ in range(50)], "Large grid"),
    ]

    for grid, description in test_grids:
        messages.clear()

        success, result = await controller.run_workflow(
            lambda send_message, check_cancelled, g=grid: engine_workflow(
                send_message, check_cancelled, g
            ),
            description,
        )

        assert success is True
        assert result is not None

        # Some grids might be empty or have parsing issues
        if description == "Empty rows" or description == "All empty cells":
            assert result["success"] is True
            assert result["final_state"]["steps_executed"] == 0
        else:
            assert result["success"] is True

            # Verify appropriate execution
            if description == "Large grid":
                assert result["final_state"]["steps_executed"] == 50
            elif description == "Single cell":
                assert result["final_state"]["steps_executed"] == 1
            elif description == "Mixed cells":
                assert result["final_state"]["steps_executed"] == 2
