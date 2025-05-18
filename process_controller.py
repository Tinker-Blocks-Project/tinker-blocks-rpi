import asyncio
import json
import os
from image_processing import Image
from image_processing.grid import PerspectiveGrid
from image_processing.ocr import EasyOCRClient
from image_processing import OCR2Grid
from camera.capture import capture_image
import websockets.exceptions

# Global variables
send_to_mobile = None
connected_clients = set()
current_process_task = None

def register_send_func(send_func):
    global send_to_mobile
    send_to_mobile = send_func

async def start_process():
    print("🚀 Running Raspberry Pi main logic...")
    await send_to_mobile("Raspberry Pi: started processing")

    try:
        # Make the capture_image() cancellable
        image_path_captured = await asyncio.get_event_loop().run_in_executor(None, capture_image)
        await send_to_mobile(f"Captured image: {image_path_captured}")

        # Check for cancellation periodically
        await asyncio.sleep(0)  # Yield control to event loop

        image = Image.from_file(f"assets/{image_path_captured}")
        rotated = image.rotate_90_clockwise()
        gray = rotated.to_grayscale()

        await asyncio.sleep(0)  # Yield control

        top_right_corner = (1054, 104)
        top_left_corner = (30, 91)
        bottom_left_corner = (33, 1712)
        bottom_right_corner = (1014, 1726)

        grid = PerspectiveGrid(
            top_right=top_right_corner,
            top_left=top_left_corner,
            bottom_left=bottom_left_corner,
            bottom_right=bottom_right_corner,
        )

        os.makedirs("output", exist_ok=True)
        grid_image = grid.draw_grid(gray)
        grid_image.save("output/grid_image.jpg")
        await send_to_mobile("Grid image saved.")

        await asyncio.sleep(0)  # Yield control

        temp_path = "temp_rotated_image.jpg"
        rotated.save(temp_path)

        # Make OCR processing cancellable
        ocr_reader = EasyOCRClient('192.168.1.6')
        ocr_list = await asyncio.get_event_loop().run_in_executor(None, lambda: ocr_reader.process_image(temp_path))

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                print(f"Could not remove temporary file {temp_path}")

        await asyncio.sleep(0)  # Yield control

        squares = grid.get_grid_squares(gray)
        OCR2Grid_instance = OCR2Grid(ocr_list, squares)
        OCR2Grid_instance.fill_grid()
        OCR2Grid_instance.print_grid()

        await send_to_mobile("Grid processed:")
        await send_to_mobile("Processing complete.")

    except asyncio.CancelledError:
        await send_to_mobile("Processing was cancelled")
        raise
    except Exception as e:
        await send_to_mobile(f"Error during processing: {e}")
    finally:
        await send_to_mobile("Raspberry Pi: finished processing")

async def stop_process():
    global current_process_task
    if current_process_task and not current_process_task.done():
        current_process_task.cancel()
        try:
            await current_process_task
        except asyncio.CancelledError:
            pass  # Expected when cancelling
        await send_to_mobile("Raspberry Pi: process stopped")
    else:
        await send_to_mobile("No process to stop")

