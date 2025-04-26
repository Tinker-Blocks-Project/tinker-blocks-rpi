from models import Image, PerspectiveGrid
import cv2
import os

# Define the corner points
top_right_corner = (1054, 104)
top_left_corner = (30, 91)
bottom_left_corner = (33, 1712)
bottom_right_corner = (1014, 1726)

# Load and process the image
image = Image("assets/oak-d_images/frame_010.jpg")

# Convert to grayscale
gray_image = image.to_grayscale()
image.set_image(gray_image)

# Create the perspective grid
grid = PerspectiveGrid(
    top_right_corner, top_left_corner, bottom_left_corner, bottom_right_corner
)

# First, draw and show the grid
grid_image = grid.draw_grid(image.get_image())
cv2.imshow("Grid", grid_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Then, extract and save the squares
squares = grid.get_grid_squares(image.get_image())

# Create output directory for squares
os.makedirs("output/squares", exist_ok=True)

# Save each square
for square in squares:
    # Save the square image
    output_path = f"output/squares/row_{square.row}_col_{square.col}.jpg"
    cv2.imwrite(output_path, square.image)

    # Print square information
    print(f"Saved square at row {square.row}, col {square.col} to {output_path}")
