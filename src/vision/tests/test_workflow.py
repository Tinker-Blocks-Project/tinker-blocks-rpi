import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from vision.workflow import ocr_grid_workflow
from vision.types import Grid


@pytest.mark.asyncio
async def test_ocr_grid_workflow_cancellation():
    """Test that workflow respects cancellation."""
    messages = []

    async def mock_send(message, level):
        messages.append(message)

    # Simulate cancellation after first message
    cancel_count = 0

    def mock_check_cancelled():
        nonlocal cancel_count
        cancel_count += 1
        return cancel_count > 1  # Cancel after first check

    # Mock OCR engine
    mock_ocr = AsyncMock()

    result = await ocr_grid_workflow(mock_ocr, mock_send, mock_check_cancelled)

    # Should return empty grid due to cancellation
    assert isinstance(result, Grid)
    assert result.blocks == []

    # Should have started but not completed
    assert any("Capturing image" in msg for msg in messages)
    assert not any("Grid processing complete" in msg for msg in messages)


@pytest.mark.asyncio
async def test_ocr_grid_workflow_messages():
    """Test that workflow sends appropriate status messages."""
    messages = []

    async def mock_send(message, level):
        messages.append(message)

    def never_cancelled():
        return False

    # Mock OCR engine
    mock_ocr = AsyncMock()
    mock_grid_result = Grid(blocks=[["MOVE", "TURN"], ["", "LEFT"]])
    mock_ocr.process_image.return_value = mock_grid_result

    # Mock external dependencies
    with (
        patch("vision.workflow.Image") as mock_image_class,
        patch("vision.workflow.PerspectiveGrid") as mock_grid_class,
        patch("os.makedirs"),
        patch("os.path.exists", return_value=True),
        patch("os.remove"),
        patch("builtins.open", mock_open()) as mock_file,
    ):
        # Setup mocks
        mock_image = MagicMock()
        mock_image.rotate_90_clockwise.return_value = mock_image
        mock_image.to_grayscale.return_value = mock_image
        mock_image.save = MagicMock()
        mock_image_class.from_file.return_value = mock_image

        mock_grid = MagicMock()
        mock_grid.draw_grid.return_value = mock_image
        mock_grid.apply_perspective_transform.return_value = mock_image
        mock_grid_class.return_value = mock_grid

        # Run workflow
        grid_result = await ocr_grid_workflow(mock_ocr, mock_send, never_cancelled)

    # Verify it returned a Grid object
    assert isinstance(grid_result, Grid)
    assert grid_result.blocks == [["MOVE", "TURN"], ["", "LEFT"]]

    # Verify expected messages
    expected_phrases = [
        "Capturing image",
        "Processing image",
        "Creating perspective grid",
        "Processing images saved to folder",
        "Running OCR on transformed grid",
        "Grid processing complete",
    ]

    for phrase in expected_phrases:
        assert any(
            phrase in msg for msg in messages
        ), f"Missing expected phrase: {phrase}. Messages: {messages}"
