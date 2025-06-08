"""End-to-end tests for complete workflows."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, mock_open
from core import ProcessController
from vision.workflow import ocr_grid_workflow
from engine.workflow import engine_workflow


@pytest.mark.asyncio
async def test_ocr_workflow_full_execution():
    """Test OCR workflow from start to finish."""
    messages = []

    async def capture_messages(msg):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Mock OCR engine
    from vision.types import Grid
    from unittest.mock import AsyncMock

    mock_ocr = AsyncMock()
    mock_grid_result = Grid(
        blocks=[
            ["FORWARD", "RIGHT", "", ""],
            ["LEFT", "FORWARD", "", ""],
            ["", "", "", ""],
        ]
    )
    mock_ocr.process_image.return_value = mock_grid_result

    # Mock the external dependencies
    with (
        patch("vision.workflow.Image") as mock_image,
        patch("vision.workflow.PerspectiveGrid") as mock_grid,
        patch("os.makedirs"),
        patch("os.path.exists", return_value=True),
        patch("os.remove"),
        patch("builtins.open", mock_open()),
    ):
        # Setup mocks
        mock_image_inst = MagicMock()
        mock_image_inst.rotate_90_clockwise.return_value = mock_image_inst
        mock_image_inst.to_grayscale.return_value = mock_image_inst
        mock_image_inst.save = MagicMock()
        mock_image.from_file.return_value = mock_image_inst

        mock_grid_inst = MagicMock()
        mock_grid_inst.draw_grid.return_value = mock_image_inst
        mock_grid_inst.apply_perspective_transform.return_value = mock_image_inst
        mock_grid.return_value = mock_grid_inst

        # Run workflow
        success, result = await controller.run_workflow(
            lambda send_message, check_cancelled: ocr_grid_workflow(
                mock_ocr, send_message, check_cancelled
            ),
            "OCR Grid Test",
        )

        # Verify success
        assert success is True
        assert isinstance(result, Grid)
        assert result.blocks == mock_grid_result.blocks

        # Verify workflow steps executed
        workflow_steps = [
            "Capturing image",
            "Processing image",
            "Creating perspective grid",
            "Processing images saved to folder",
            "Running OCR on transformed grid",
            "Grid processing complete",
        ]

        for step in workflow_steps:
            assert any(step in msg for msg in messages), f"Missing step: {step}"


@pytest.mark.asyncio
async def test_engine_workflow_execution():
    """Test engine workflow with sample grid."""
    messages = []

    async def capture_messages(msg):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Sample grid
    test_grid = [
        ["MOVE"],
        ["MOVE"],
        ["TURN", "RIGHT"],
        ["MOVE"],
        ["TURN", "LEFT"],
        ["MOVE"],
        ["MOVE"],
    ]

    # Run workflow
    success, result = await controller.run_workflow(
        lambda send_message, check_cancelled: engine_workflow(
            send_message, check_cancelled, test_grid
        ),
        "Engine Test",
    )

    # Verify success
    assert success is True
    assert result is not None
    assert result["success"] is True

    # Verify final state
    final_state = result["final_state"]
    assert final_state["steps_executed"] == 7
    # Fixed expectations based on correct execution:
    # MOVE, MOVE (now at 0,2 facing forward)
    # TURN RIGHT (now at 0,2 facing right)
    # MOVE (now at 1,2 facing right)
    # TURN LEFT (now at 1,2 facing forward)
    # MOVE, MOVE (now at 1,4 facing forward)
    assert final_state["position"]["x"] == 1.0
    assert final_state["position"]["y"] == 4.0
    assert final_state["direction"] == "forward"

    # Verify execution messages
    assert any("Executing commands" in msg for msg in messages)
    assert any("Execution complete" in msg for msg in messages)
    assert any("Total steps executed: 7" in msg for msg in messages)


@pytest.mark.asyncio
async def test_full_pipeline_workflow():
    """Test complete OCR to Engine pipeline."""
    messages = []

    async def capture_messages(msg):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Mock OCR workflow to return a grid
    mock_grid = [
        ["MOVE"],
        ["TURN", "RIGHT"],
        ["TURN", "LEFT"],
        ["MOVE"],
    ]

    from vision.types import Grid

    with patch("vision.workflow.ocr_grid_workflow") as mock_ocr_workflow:
        mock_ocr_workflow.return_value = Grid(blocks=mock_grid)

        # Run OCR workflow
        success1, grid_result = await controller.run_workflow(
            mock_ocr_workflow, "OCR Phase"
        )

        assert success1 is True
        assert isinstance(grid_result, Grid)
        assert grid_result.blocks == mock_grid

        # Run Engine workflow with the grid
        success2, engine_result = await controller.run_workflow(
            lambda send_message, check_cancelled: engine_workflow(
                send_message, check_cancelled, grid_result.blocks
            ),
            "Engine Phase",
        )

        assert success2 is True
        assert engine_result is not None
        assert engine_result["success"] is True
        assert engine_result["final_state"]["steps_executed"] == 4


@pytest.mark.asyncio
async def test_workflow_cancellation_propagation():
    """Test that cancellation propagates through workflows."""
    messages = []
    cancelled = False

    async def capture_messages(msg):
        messages.append(msg)

    async def long_workflow(send_message, check_cancelled):
        nonlocal cancelled
        await send_message("Starting long task...")

        for i in range(10):
            if check_cancelled():
                cancelled = True
                await send_message("Detected cancellation")
                return {"cancelled": True}

            await send_message(f"Step {i}")
            await asyncio.sleep(0.01)

        return {"completed": True}

    controller = ProcessController(capture_messages)

    # Start workflow and cancel it
    task = asyncio.create_task(
        controller.run_workflow(long_workflow, "Cancellable Task")
    )

    # Let it run a bit more to ensure it's actually running
    await asyncio.sleep(0.05)  # Increased from 0.03

    # Cancel it
    controller.cancel()

    # Wait for completion
    success, result = await task

    assert success is False
    # Check that cancellation was processed
    assert any("was cancelled" in msg for msg in messages)


@pytest.mark.asyncio
async def test_workflow_with_empty_grid():
    """Test engine workflow with empty grid."""
    messages = []

    async def capture_messages(msg):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Empty grid
    empty_grid = [
        ["", "", ""],
        ["", "", ""],
    ]

    success, result = await controller.run_workflow(
        lambda send_message, check_cancelled: engine_workflow(
            send_message, check_cancelled, empty_grid
        ),
        "Empty Grid Test",
    )

    assert success is True
    assert result is not None
    assert result["final_state"]["steps_executed"] == 0
    assert result["final_state"]["position"]["x"] == 0
    assert result["final_state"]["position"]["y"] == 0
