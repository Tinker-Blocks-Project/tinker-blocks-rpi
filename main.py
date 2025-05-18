# main.py

from image_processing import Image
from image_processing.grid import PerspectiveGrid
from image_processing.ocr import EasyOCRClient
from image_processing import OCR2Grid
from camera.capture import capture_image
from ws_server import send_to_mobile

import os
import asyncio

async def start_process(websocket):
    try:
        image_path_captured = capture_image()
        send_to_mobile(websocket, f"Captured image: {image_path_captured}")

        image = Image.from_file(f"assets/{image_path_captured}")
        rotated = image.rotate_90_clockwise()
        gray = rotated.to_grayscale()

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
        send_to_mobile(websocket, "Grid image saved.")

        temp_path = "temp_rotated_image.jpg"
        rotated.save(temp_path)

        ocr_reader = EasyOCRClient('192.168.1.6')
        ocr_list = ocr_reader.process_image(temp_path)

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                print(f"Could not remove temporary file {temp_path}")

        squares = grid.get_grid_squares(gray)
        OCR2Grid_instance = OCR2Grid(ocr_list, squares)
        OCR2Grid_instance.fill_grid()
        grid_output = OCR2Grid_instance.get_grid_as_text()

        send_to_mobile(websocket, "Grid processed:")
        send_to_mobile(websocket, grid_output)

        send_to_mobile(websocket, "Processing complete.")
    except Exception as e:
        send_to_mobile(websocket, f"Error during processing: {e}")

async def stop_process(websocket):
    # Add any cleanup or stop logic here
    send_to_mobile(websocket, "Processing stopped.")

if __name__ == '__main__':
    from ws_server import start_ws_server
    start_ws_server()
