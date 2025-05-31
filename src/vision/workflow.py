"""Vision processing workflow."""

import os
from typing import Callable, Awaitable
from vision import Image
from vision.grid import PerspectiveGrid, OCR2Grid
from vision.ocr import EasyOCR
from core.config import config


async def ocr_grid_workflow(
    send_message: Callable[[str], Awaitable[None]],
    check_cancelled: Callable[[], bool],
) -> list[list[str]]:
    """
    Complete OCR grid processing workflow.

    Args:
        send_message: Function to send status messages
        check_cancelled: Function to check if process was cancelled

    Returns:
        2D list representing the grid of commands
    """
    await send_message("Starting OCR grid processing workflow...")

    # Step 1: Capture image
    if check_cancelled():
        return []

    await send_message("\n📸 Capturing image...")
    # TODO: In production, use: image_path = capture_image_client()
    image_path = "assets/oak-d_images/frame_010.jpg"
    await send_message(f"Using image: {image_path}")

    # Step 2: Load and process image
    if check_cancelled():
        return []

    await send_message("\n🔄 Processing image...")
    image = Image.from_file(image_path)
    rotated = image.rotate_90_clockwise()
    gray = rotated.to_grayscale()
    await send_message("✓ Image rotated and converted to grayscale")

    # Step 3: Create perspective grid
    if check_cancelled():
        return []

    await send_message("\n📐 Creating perspective grid...")
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

    # Get grid squares
    squares = grid.get_grid_squares(gray)
    await send_message(f"✓ Grid created with {len(squares)} squares")

    # Step 4: Run OCR
    if check_cancelled():
        return []

    await send_message("\n🔍 Running OCR...")
    temp_path = "temp_rotated_image.jpg"
    rotated.save(temp_path)

    try:
        ocr_reader = EasyOCR()
        ocr_results = ocr_reader.process_image(temp_path)
        await send_message(f"✓ OCR found {len(ocr_results)} text regions")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Could not remove temporary file {temp_path}: {e}")

    # Step 5: Map OCR to grid
    if check_cancelled():
        return []

    await send_message("\n🗺️ Mapping OCR results to grid...")
    ocr2grid = OCR2Grid(ocr_results, squares)
    ocr2grid.fill_grid()
    ocr2grid.print_grid()
    grid_json = ocr2grid.get_grid_as_json()

    await send_message("✓ Grid mapping complete!")
    await send_message(f"\n📊 Results:\n{grid_json}")

    # Return the grid data
    return ocr2grid.grid
