import asyncio
import json
import os
from image_processing import Image
from image_processing.grid import PerspectiveGrid
from image_processing.ocr import EasyOCRClient
from image_processing import OCR2Grid
from camera.capture import capture_image
import websockets.exceptions
from typing import Optional, Callable, Awaitable

# Global variables
send_to_mobile = None
connected_clients = set()
current_process_task = None
# Shared state
_current_process_task: Optional[asyncio.Task] = None
_send_to_mobile: Optional[Callable[[str], Awaitable[None]]] = None
def register_send_func(send_func):
    global send_to_mobile
    send_to_mobile = send_func

async def _send(message: str):
    if _send_to_mobile:
        await _send_to_mobile(message)   

async def start_process():
    global _current_process_task
    
    if _current_process_task and not _current_process_task.done():
        await _send("⚠️ Process already running!")
        return

    _current_process_task = asyncio.create_task(_process_workflow())
    await _send("🚀 Process started")

async def _process_workflow():
    try:
        await _send("Raspberry Pi: started processing")
        
        # Your actual processing steps
        image_path = await asyncio.get_event_loop().run_in_executor(None, capture_image)
        await _send(f"Captured image: {image_path}")
        await _check_cancellation()
        
        image = Image.from_file(f"assets/{image_path}")
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
        await send_to_mobile("Grid image saved.")

        await _check_cancellation()

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

        await _check_cancellation()

        squares = grid.get_grid_squares(gray)
        OCR2Grid_instance = OCR2Grid(ocr_list, squares)
        OCR2Grid_instance.fill_grid()
        OCR2Grid_instance.print_grid()

        await send_to_mobile("Grid processed:")
        await send_to_mobile("Processing complete.")
        await _check_cancellation()
    except asyncio.CancelledError:
        await _send("🛑 Processing cancelled")
    except Exception as e:
        await _send(f"❌ Error: {str(e)}")
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
        await _send("⏹️ Process stopped")
    else:
        await _send("⚠️ No active process to stop")

def get_current_task():
    return _current_process_task

