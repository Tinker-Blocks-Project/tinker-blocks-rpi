"""Vision processing workflow."""

import os
import time
import json
from datetime import datetime
from typing import Callable, Awaitable
from vision.types import Image, Grid
from vision.grid import PerspectiveGrid
from vision.ocr import OCRProtocol
from core.config import config
from core.types import LogLevel


async def ocr_grid_workflow(
    ocr_engine: OCRProtocol,
    send_message: Callable[[str, LogLevel], Awaitable[None]],
    check_cancelled: Callable[[], bool],
) -> Grid:
    """
    Complete OCR grid processing workflow.

    Args:
        ocr_engine: OCR implementation that conforms to OCRProtocol
        send_message: Function to send status messages
        check_cancelled: Function to check if process was cancelled

    Returns:
        Grid object representing the detected commands
    """
    # Start total timing
    total_start_time = time.time()

    # Generate timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Step 1: Capture image
    if check_cancelled():
        return Grid(blocks=[])

    await send_message("\n📸 Capturing image...", LogLevel.INFO)
    # In production, replace with: image_path = capture_image_client() or capture_image_local()
    image_path = "assets/oak-d_images/frame_064.png"
    await send_message(f"Using image: {image_path}", LogLevel.DEBUG)

    # Step 2: Load and process image
    if check_cancelled():
        return Grid(blocks=[])

    processing_start_time = time.time()
    await send_message("\n🔄 Processing image...", LogLevel.INFO)
    try:
        image = Image.from_file(image_path)
        rotated = image.rotate_90_clockwise()

        # Create timestamped output folder early to save all processing images
        output_folder = f"{config.output_dir}/{timestamp}"
        os.makedirs(output_folder, exist_ok=True)

        # Save rotated original image
        rotated_path = f"{output_folder}/rotated_original.jpg"
        rotated.save(rotated_path)

        # Convert to grayscale for grid processing
        gray = rotated.to_grayscale()
        await send_message(
            "✓ Image rotated and converted to grayscale", LogLevel.SUCCESS
        )
    except Exception as e:
        await send_message(f"❌ Image processing failed: {str(e)}", LogLevel.ERROR)
        return Grid(blocks=[])

    # Step 3: Create perspective grid and apply transformation
    if check_cancelled():
        return Grid(blocks=[])

    await send_message("\n📐 Creating perspective grid...", LogLevel.INFO)
    grid = PerspectiveGrid(
        top_right=config.grid_corners["top_right"],
        top_left=config.grid_corners["top_left"],
        bottom_left=config.grid_corners["bottom_left"],
        bottom_right=config.grid_corners["bottom_right"],
    )

    # Save grid visualization on original image
    grid_image = grid.draw_grid(gray)
    grid_overlay_path = f"{output_folder}/grid_overlay.jpg"
    grid_image.save(grid_overlay_path)

    # Apply perspective transformation to get rectified grid image
    transformed_image = grid.apply_perspective_transform(grid_image)

    # Save the perspective-transformed image for OCR processing
    transformed_path = f"{output_folder}/transformed_grid.jpg"
    transformed_image.save(transformed_path)
    await send_message(
        f"✓ Processing images saved to folder: {output_folder}/", LogLevel.SUCCESS
    )

    processing_end_time = time.time()
    processing_time = processing_end_time - processing_start_time

    # Step 4: Run OCR on transformed image
    if check_cancelled():
        return Grid(blocks=[])

    ocr_start_time = time.time()
    await send_message("\n🔍 Running OCR on transformed grid...", LogLevel.INFO)
    try:
        # OCR engine processes the transformed image directly
        grid_result = await ocr_engine.process_image(transformed_path)
        non_empty_cells = len(
            [cell for row in grid_result.blocks for cell in row if cell.strip()]
        )
        await send_message(
            f"✓ OCR completed, found {non_empty_cells} non-empty cells",
            LogLevel.SUCCESS,
        )
    except Exception as e:
        await send_message(f"❌ OCR failed: {str(e)}", LogLevel.ERROR)
        return Grid(blocks=[])

    ocr_end_time = time.time()
    ocr_time = ocr_end_time - ocr_start_time
    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # Format and display final grid result
    await send_message("✓ Grid processing complete!", LogLevel.SUCCESS)
    formatted_grid = _format_grid_for_display(grid_result)
    await send_message(f"\n📊 Grid Result:\n{formatted_grid}", LogLevel.INFO)

    # Save grid result as JSON
    grid_json_path = f"{output_folder}/grid_result.json"
    with open(grid_json_path, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "blocks": grid_result.blocks,
                "non_empty_cells": len(
                    [cell for row in grid_result.blocks for cell in row if cell.strip()]
                ),
                "grid_dimensions": {
                    "rows": len(grid_result.blocks),
                    "cols": len(grid_result.blocks[0]) if grid_result.blocks else 0,
                },
            },
            f,
            indent=2,
        )

    # Send timing information
    await send_message("\n⏱️ Timing Summary:", LogLevel.INFO)
    await send_message(f"   Processing time: {processing_time:.2f}s", LogLevel.DEBUG)
    await send_message(f"   OCR time: {ocr_time:.2f}s", LogLevel.DEBUG)
    await send_message(f"   Total time: {total_time:.2f}s", LogLevel.DEBUG)

    # Report all saved files
    await send_message(f"\n💾 Saved files in {output_folder}/:", LogLevel.INFO)
    await send_message("   - rotated_original.jpg", LogLevel.DEBUG)
    await send_message("   - grid_overlay.jpg", LogLevel.DEBUG)
    await send_message("   - transformed_grid.jpg", LogLevel.DEBUG)
    await send_message("   - grid_result.json", LogLevel.DEBUG)

    return grid_result


def _format_grid_for_display(grid: Grid) -> str:
    """Format grid for console display."""
    lines = []
    for i, row in enumerate(grid.blocks):
        formatted_row = " | ".join(f"{cell:>8}" if cell else "        " for cell in row)
        lines.append(f"Row {i:2d}: {formatted_row}")
    return "\n".join(lines)
