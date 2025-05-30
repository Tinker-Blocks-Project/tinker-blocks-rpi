"""Vision processing tasks."""

import asyncio
import os
from typing import Callable, Awaitable, Dict, Any
from vision import Image
from vision.grid import PerspectiveGrid, OCR2Grid
from vision.ocr import EasyOCR
from core.config import config


# Shared state between tasks
_task_state: Dict[str, Any] = {
    "image_path": None,
    "image": None,
    "rotated": None,
    "gray": None,
    "grid": None,
    "ocr_results": None,
    "squares": None,
}


async def check_cancellation():
    """Yield control to allow task cancellation."""
    await asyncio.sleep(0)


async def capture_image_task(send_message: Callable[[str], Awaitable[None]]):
    """Capture image from camera."""
    # For testing, use a hardcoded image
    # In production: image_path = capture_image_client()

    image_path = "assets/oak-d_images/frame_010.jpg"
    _task_state["image_path"] = image_path

    await send_message(f"Image path: {image_path}")
    await check_cancellation()


async def process_image_task(send_message: Callable[[str], Awaitable[None]]):
    """Load and process the image (rotate, grayscale)."""
    image_path = _task_state.get("image_path")
    if not image_path:
        raise ValueError("No image path available")

    # Load and process image
    image = Image.from_file(image_path)
    rotated = image.rotate_90_clockwise()
    gray = rotated.to_grayscale()

    # Store in state
    _task_state["image"] = image
    _task_state["rotated"] = rotated
    _task_state["gray"] = gray

    await send_message("Image loaded and processed (rotated, grayscale)")
    await check_cancellation()


async def create_grid_task(send_message: Callable[[str], Awaitable[None]]):
    """Create perspective grid and save visualization."""
    gray = _task_state.get("gray")
    if not gray:
        raise ValueError("No grayscale image available")

    # Create perspective grid
    grid = PerspectiveGrid(
        top_right=config.grid_corners["top_right"],
        top_left=config.grid_corners["top_left"],
        bottom_left=config.grid_corners["bottom_left"],
        bottom_right=config.grid_corners["bottom_right"],
    )

    # Save grid visualization
    os.makedirs(config.output_dir, exist_ok=True)
    grid_image = grid.draw_grid(gray)
    grid_image.save(f"{config.output_dir}/grid_image.jpg")

    # Get grid squares for later use
    squares = grid.get_grid_squares(gray)

    # Store in state
    _task_state["grid"] = grid
    _task_state["squares"] = squares

    await send_message(f"Grid created with {len(squares)} squares")
    await check_cancellation()


async def run_ocr_task(send_message: Callable[[str], Awaitable[None]]):
    """Run OCR on the rotated image."""
    rotated = _task_state.get("rotated")
    if not rotated:
        raise ValueError("No rotated image available")

    # Save temporary image for OCR
    temp_path = "temp_rotated_image.jpg"
    rotated.save(temp_path)

    try:
        # Run OCR
        ocr_reader = EasyOCR()
        ocr_results = ocr_reader.process_image(temp_path)

        # Store results
        _task_state["ocr_results"] = ocr_results

        await send_message(f"OCR found {len(ocr_results)} text regions")

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Could not remove temporary file {temp_path}: {e}")

    await check_cancellation()


async def map_ocr_to_grid_task(send_message: Callable[[str], Awaitable[None]]):
    """Map OCR results to grid positions."""
    ocr_results = _task_state.get("ocr_results")
    squares = _task_state.get("squares")

    if not ocr_results:
        raise ValueError("No OCR results available")
    if not squares:
        raise ValueError("No grid squares available")

    # Map OCR results to grid
    ocr2grid = OCR2Grid(ocr_results, squares)
    ocr2grid.fill_grid()
    ocr2grid.print_grid()
    grid_json = ocr2grid.get_grid_as_json()

    await send_message("Grid mapping complete:")
    await send_message(grid_json)

    await check_cancellation()


# Legacy function for compatibility
async def create_ocr_grid_task(send_message: Callable[[str], Awaitable[None]]):
    """Legacy function that runs all tasks in sequence."""
    await capture_image_task(send_message)
    await process_image_task(send_message)
    await create_grid_task(send_message)
    await run_ocr_task(send_message)
    await map_ocr_to_grid_task(send_message)
