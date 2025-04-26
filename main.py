from image_processing.Image import Image
import cv2

# Define the corner points
top_right_corner = (1054, 104)
top_left_corner = (30, 91)
bottom_left_corner = (33, 1712)
bottom_right_corner = (1014, 1726)

# Load and process the image
image = Image("assets/oak-d_images/frame_010.jpg")

# Draw the grid
grid_image = image.draw_grid(
    top_right_corner, top_left_corner, bottom_left_corner, bottom_right_corner
)

# Show the result
cv2.imshow("Grid", grid_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
