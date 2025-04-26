from image_processing.Image import *
import cv2
img = Image('pics/frame_000.jpg', scale_percent=50)
def has_distinct_color_channel(rgb, threshold=30):
    """
    Check if at least one RGB channel is significantly different from others.
    
    Args:
        rgb: Tuple of (R, G, B) values
        threshold: Minimum difference required between max and min channel
    
    Returns:
        True if the color has a distinct channel, False otherwise
    """
    r, g, b = rgb
    
    # Calculate the range between max and min channel values
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    range_val = max_val - min_val
    
    # If the range is greater than threshold, then at least one channel is distinct
    return range_val > threshold

def find_border(rows,cols):
    start_pixel = (0, 0)
    for i in range(rows):
        for j in range(cols):
            # Get the RGB values of the pixel
            rgb = tuple(img.image[i, j])
            
            # Check if the pixel has a distinct color channel
            if has_distinct_color_channel(rgb):
                start_pixel = (i, j)
                print(rgb)
                # Draw a circle around the pixel
                
                return start_pixel
rows = img.image.shape[0]
cols = img.image.shape[1]


start_pixel_y , start_pixel_x = find_border(rows,cols)

cell_width = 40
cell_height = 40

print("Start pixel:", start_pixel_y, start_pixel_x)

i = start_pixel_y 
for j in range(start_pixel_x, cols, cell_width+12):
    # Draw a rectangle around the cell
    cv2.rectangle(img.image, (j, i), (j + cell_width, i + cell_height), (255, 0, 0), 1)

        

print("Start pixel with distinct color channel:", find_border(rows,cols))

img.show()