from image_processing import Image
from image_processing.grid import PerspectiveGrid
from image_processing.ocr import EasyOCR
from image_processing.ocr import EasyOCRClient
from image_processing import OCR2Grid
import os
import cv2
import numpy as np


# Load and process the image
image = Image.from_file("assets/oak-d_images/frame_010.jpg")

# Rotate the image
rotated = image.rotate_90_clockwise()

# Convert to grayscale
gray = rotated.to_grayscale()

# Define the corner points for the grid
top_right_corner = (1054, 104)
top_left_corner = (30, 91)
bottom_left_corner = (33, 1712)
bottom_right_corner = (1014, 1726)

# Create the perspective grid
grid = PerspectiveGrid(
    top_right=top_right_corner,
    top_left=top_left_corner,
    bottom_left=bottom_left_corner,
    bottom_right=bottom_right_corner,
)

# Instead of showing the grid, save it directly
# Create output directory for results
os.makedirs("output", exist_ok=True)

# Draw the grid and save it
grid_image = grid.draw_grid(gray)
grid_image.save("output/grid_image.jpg")
print("Grid image saved to output/grid_image.jpg")

# For text detection, save the rotated image to a temporary file
temp_path = "temp_rotated_image.jpg"
rotated.save(temp_path)
print("Rotated image saved to", temp_path)

# Read Text using OCR MODEL
ocr_reader = EasyOCRClient('127.0.0.1')
ocr_list = ocr_reader.process_image(temp_path)

# Clean up temporary file
if os.path.exists(temp_path):
    try:
        os.remove(temp_path)
    except:
        print(f"Could not remove temporary file {temp_path}")


# Continue with your original code for grid squares
print("\nProcessing grid squares...")
squares = grid.get_grid_squares(gray)

# this will convert ocr results to final grid
OCR2Grid_instance = OCR2Grid(ocr_list, squares)
OCR2Grid_instance.fill_grid()
OCR2Grid_instance.print_grid()



print("\nAll processing complete!")