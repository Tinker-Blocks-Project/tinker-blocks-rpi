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
send_to_mobile = None  # placeholder for injected function
connected_clients = set()
process_active = False
should_stop = False

def register_send_func(send_func):
    global send_to_mobile
    send_to_mobile = send_func

async def start_process():
    global process_active, should_stop
    
    if process_active:
        await send_to_mobile("Process is already running")
        return
        
    process_active = True
    should_stop = False
    
    print("🚀 Running Raspberry Pi main logic...")
    await send_to_mobile("Raspberry Pi: started processing")

    try:
        # Check if we should stop before each major step
        if should_stop:
            return
            
        image_path_captured = capture_image()
        await send_to_mobile(f"Captured image: {image_path_captured}")

        if should_stop:
            return
            
        image = Image.from_file(f"assets/{image_path_captured}")
        rotated = image.rotate_90_clockwise()
        gray = rotated.to_grayscale()

        if should_stop:
            return
            
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

        if should_stop:
            return
            
        temp_path = "temp_rotated_image.jpg"
        rotated.save(temp_path)

        if should_stop:
            return
            
        ocr_reader = EasyOCRClient('192.168.1.6')
        ocr_list = ocr_reader.process_image(temp_path)

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                print(f"Could not remove temporary file {temp_path}")

        if should_stop:
            return
            
        squares = grid.get_grid_squares(gray)
        OCR2Grid_instance = OCR2Grid(ocr_list, squares)
        OCR2Grid_instance.fill_grid()
        OCR2Grid_instance.print_grid()

        await send_to_mobile("Grid processed:")
        await send_to_mobile("Processing complete.")
        
    except Exception as e:
        await send_to_mobile(f"Error during processing: {e}")
    finally:
        process_active = False
        should_stop = False
        await send_to_mobile("Raspberry Pi: finished processing")

async def stop_process():
    global should_stop, process_active
    
    if not process_active:
        await send_to_mobile("No process is currently running")
        return
        
    print("🛑 Stopping processing...")
    should_stop = True
    await send_to_mobile("Raspberry Pi: stopping process...")
    