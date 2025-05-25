import asyncio
import json
import os
from image_processing import Image
from image_processing.grid import PerspectiveGrid
from image_processing.ocr import EasyOCR
from image_processing import OCR2Grid
from camera.capture import capture_image
from camera.CameraClient import capture_image_client
import websockets.exceptions
from typing import Optional, Callable, Awaitable

# Global variables
send_to_mobile = None
connected_clients = set()
current_process_task = None
server_ip = '192.168.1.102'
# Shared state
_current_process_task: Optional[asyncio.Task] = None
_send_to_mobile: Optional[Callable[[str], Awaitable[None]]] = None
def register_send_func(send_func):
    global _send_to_mobile
    _send_to_mobile = send_func

async def _send(message: str):
    if _send_to_mobile:
        await _send_to_mobile(message)   
async def start_process():
    global _current_process_task
    
    if _current_process_task and not _current_process_task.done():
        await _send("Process already running!")
        return

    _current_process_task = asyncio.create_task(_process_workflow())
    await _send("**Process started**")

async def _process_workflow():
    try:
        await _send("**Processing Started**\n\nHere are the steps:\n1. Capture Image\n2. OCR Scan\n3. Grid Mapping")
        
        # Your actual processing steps
        image_path = capture_image_client()
        await _send(f"Captured image: {image_path}")
        await _check_cancellation()
        
        image = Image.from_file(image_path)
        rotated = image.rotate_90_clockwise()
        gray = rotated.to_grayscale()

        await _check_cancellation()
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
        await _send("Grid image saved.")

        await _check_cancellation()

        temp_path = "temp_rotated_image.jpg"
        rotated.save(temp_path)

        # Make OCR processing cancellable
        ocr_reader = EasyOCR()
        ocr_list = ocr_reader.process_image(temp_path)
        await _send("OCR processing complete.")
        await _check_cancellation()
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                print(f"Could not remove temporary file {temp_path}")

        await _check_cancellation()

        squares = grid.get_grid_squares(gray)
        OCR2Grid_instance = OCR2Grid(ocr_list, squares)
        OCR2Grid_instance.fill_grid()
        OCR2Grid_instance.print_grid()
        grid_json = OCR2Grid_instance.get_grid_as_json()
        await _send("Grid processed:")
        await _send(grid_json)
        await _send("Processing complete.")
        await _check_cancellation()

        # interpreter pattern will be here



        
    except asyncio.CancelledError:
        await _send("Processing cancelled")
    except Exception as e:
        await _send(f"Error: {str(e)}")
    finally:
        global _current_process_task
        _current_process_task = None
        await _send("Raspberry Pi: finished processing")

async def _check_cancellation():
    await asyncio.sleep(0)  # Yield control for cancellation

async def stop_process():
    global _current_process_task
    if _current_process_task and not _current_process_task.done():
        _current_process_task.cancel()
        try:
            await _current_process_task
        except asyncio.CancelledError:
            pass
        await _send("Process stopped")
    else:
        await _send("No active process to stop")

def get_current_task():
    return _current_process_task

