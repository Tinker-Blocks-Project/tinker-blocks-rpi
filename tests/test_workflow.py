import pytest
from unittest.mock import patch, MagicMock
from vision.workflow import ocr_grid_workflow


@pytest.mark.asyncio
async def test_ocr_grid_workflow_cancellation():
    """Test that workflow respects cancellation."""
    messages = []

    async def mock_send(msg):
        messages.append(msg)

    # Simulate cancellation after first message
    cancel_count = 0

    def mock_check_cancelled():
        nonlocal cancel_count
        cancel_count += 1
        return cancel_count > 1  # Cancel after first check

    await ocr_grid_workflow(mock_send, mock_check_cancelled)

    # Should have started but not completed
    assert any("Starting OCR grid processing workflow" in msg for msg in messages)
    assert not any("Workflow completed successfully" in msg for msg in messages)


@pytest.mark.asyncio
async def test_ocr_grid_workflow_messages():
    """Test that workflow sends appropriate status messages."""
    messages = []

    async def mock_send(msg):
        messages.append(msg)

    def never_cancelled():
        return False

    # Mock external dependencies
    with (
        patch("vision.workflow.Image") as mock_image_class,
        patch("vision.workflow.PerspectiveGrid") as mock_grid_class,
        patch("vision.workflow.EasyOCR") as mock_ocr_class,
        patch("vision.workflow.OCR2Grid") as mock_ocr2grid_class,
        patch("os.makedirs"),
        patch("os.path.exists", return_value=True),
        patch("os.remove"),
    ):
        # Setup mocks
        mock_image = MagicMock()
        mock_image.rotate_90_clockwise.return_value = mock_image
        mock_image.to_grayscale.return_value = mock_image
        mock_image_class.from_file.return_value = mock_image

        mock_grid = MagicMock()
        mock_grid.draw_grid.return_value = MagicMock()
        mock_grid.get_grid_squares.return_value = [MagicMock() for _ in range(160)]
        mock_grid_class.return_value = mock_grid

        mock_ocr = MagicMock()
        mock_ocr.process_image.return_value = []
        mock_ocr_class.return_value = mock_ocr

        mock_ocr2grid = MagicMock()
        mock_ocr2grid.get_grid_as_json.return_value = "{}"
        mock_ocr2grid_class.return_value = mock_ocr2grid

        # Run workflow
        await ocr_grid_workflow(mock_send, never_cancelled)

    # Verify expected messages
    expected_phrases = [
        "Starting OCR grid processing",
        "Capturing image",
        "Processing image",
        "Creating perspective grid",
        "Running OCR",
        "Mapping OCR results",
        "Workflow completed successfully",
    ]

    for phrase in expected_phrases:
        assert any(phrase in msg for msg in messages), (
            f"Missing expected phrase: {phrase}"
        )
