from image_processing import Image
from image_processing.grid import PerspectiveGrid
import os

# Load and process the image
image = Image.from_file("assets/oak-d_images/frame_010.jpg")

# Rotate the image
rotated = image.rotate_90_clockwise()

# Convert to grayscale
gray = rotated.to_grayscale()

# Define the corner points
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

# First, draw and show the grid
grid_image = grid.draw_grid(gray)
grid_image.show()

# Then, extract and save the squares
squares = grid.get_grid_squares(gray)

# Create output directory for squares
os.makedirs("output/squares", exist_ok=True)

# Save each square
for square in squares:
    # Save the square image
    output_path = f"output/squares/row_{square.row}_col_{square.col}.jpg"
    square.save(output_path)

    # Print square information
    print(f"Saved square at row {square.row}, col {square.col} to {output_path}")
