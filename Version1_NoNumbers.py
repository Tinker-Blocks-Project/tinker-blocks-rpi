import cv2
import numpy as np

def hex_to_rgb(hex_color):
    """Convert hex color to RGB"""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def rgb_to_ansi(r, g, b):
    """Convert RGB to ANSI escape code for terminal coloring"""
    return f"\033[38;2;{r};{g};{b}m"

class Colors:
    RESET = "\033[0m"
    MAPPINGS = {
        'loop':  {'hex': '#ff0000', 'rgb': hex_to_rgb('#ff0000')},
        'inf':   {'hex': '#cc6600', 'rgb': hex_to_rgb('#cc6600')},
        'mov':   {'hex': '#3333ff', 'rgb': hex_to_rgb('#3333ff')},
        'if':    {'hex': '#00cc00', 'rgb': hex_to_rgb('#00cc00')},
        'frw':   {'hex': '#ffff00', 'rgb': hex_to_rgb('#ffff00')},
        'block': {'hex': '#80063d', 'rgb': hex_to_rgb('#80063d')},
        'turn':  {'hex': '#00ff99', 'rgb': hex_to_rgb('#00ff99')},
        'right': {'hex': '#6600cc', 'rgb': hex_to_rgb('#6600cc')},
        'left':  {'hex': '#cc00ff', 'rgb': hex_to_rgb('#cc00ff')},
        'X=':    {'hex': '#99cc00', 'rgb': hex_to_rgb('#99cc00')},
        'Y=':    {'hex': '#cc9900', 'rgb': hex_to_rgb('#cc9900')},
        'Z=':    {'hex': '#ffff66', 'rgb': hex_to_rgb('#ffff66')},
        'X':     {'hex': '#6699ff', 'rgb': hex_to_rgb('#6699ff')},
        'Y':     {'hex': '#ff99cc', 'rgb': hex_to_rgb('#ff99cc')},
        'Z':     {'hex': '#996600', 'rgb': hex_to_rgb('#996600')},
    }
    
    @classmethod
    def get_ansi(cls, component):
        if component not in cls.MAPPINGS:
            return ""
        rgb = cls.MAPPINGS[component]['rgb']
        return rgb_to_ansi(*rgb)

def crop_white_margins(image):
    """Crop white margins from the image more accurately"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold with a slightly lower value to better detect content
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)
    
    # Find non-zero points (pixels that aren't white)
    coords = cv2.findNonZero(thresh)
    
    if coords is None:
        return image
    
    # Get the bounding box of non-white pixels
    x, y, w, h = cv2.boundingRect(coords)
    
    # Add a small padding (5 pixels) to avoid cutting too tight
    padding = 2
    height, width = image.shape[:2]
    
    # Ensure we don't exceed image boundaries
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(width - x, w + 2 * padding)
    h = min(height - y, h + 2 * padding)
    
    # Crop the image
    return image[y:y+h, x:x+w]

def detect_programming_grid(image_path, rows=19, cols=8):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    image = crop_white_margins(image)
    cv2.imwrite('debug_cropped.png', image)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image_rgb.shape[:2]
    
    cell_height = height // rows
    cell_width = width // cols
    
    def is_cell_empty(cell):
        """Check if cell is empty (mostly white)"""
        # Convert to grayscale
        gray = cv2.cvtColor(cell, cv2.COLOR_RGB2GRAY)
        # Count non-white pixels (using a high threshold to detect even light colors)
        non_white = np.sum(gray < 240)
        return non_white < (cell.shape[0] * cell.shape[1] * 0.05)  # 5% threshold
    
    def get_dominant_color(cell):
        if is_cell_empty(cell):
            return None
            
        # Get center region of cell (to avoid grid lines)
        h, w = cell.shape[:2]
        margin = 5  # Increase margin to avoid grid lines
        center = cell[margin:h-margin, margin:w-margin]
        
        # Calculate average color of entire cell first
        avg_color = np.mean(center.reshape(-1, 3), axis=0)
        
        # Check if the block is predominantly white or black
        if np.all(avg_color > 230):  # White check
            return None
        if np.all(avg_color < 25):   # Black check
            return None
        
        # Flatten pixels for detailed analysis
        pixels = center.reshape(-1, 3)
        
        # Remove very light and very dark colors
        valid_pixels = pixels[~np.all(pixels > 230, axis=1)]  # Remove whites
        valid_pixels = valid_pixels[~np.all(valid_pixels < 25, axis=1)]  # Remove blacks
        
        if len(valid_pixels) < 10:
            return None
            
        # Get average color of valid pixels
        avg_color = np.mean(valid_pixels, axis=0)
        
        # Find closest matching color
        min_dist = float('inf')
        closest_component = None
        
        for component, color_data in Colors.MAPPINGS.items():
            dist = np.linalg.norm(avg_color - color_data['rgb'])
            if dist < min_dist:
                min_dist = dist
                closest_component = component
        
        # More strict threshold for color matching
        return closest_component if min_dist < 120 else None
    
    # Create grid
    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            top = i * cell_height
            left = j * cell_width
            cell = image_rgb[top + 5:top + cell_height - 5, left + 5:left + cell_width - 5]  # Adjusted to avoid grid lines
            component = get_dominant_color(cell)
            row.append(component)
        grid.append(row)
    
    return grid

def print_grid(grid):
    """Print the grid with colors in terminal"""
    for row in grid:
        line = []
        for cell in row:
            if cell is None:
                # Print empty cells as dots
                line.append("........  ")
            else:
                # Get color code and create colored text
                color_code = Colors.get_ansi(cell)
                colored_text = f"{color_code}{str(cell).ljust(8)}{Colors.RESET}  "
                line.append(colored_text)
        print("".join(line))

if __name__ == "__main__":
    try:
        print("Starting grid detection...")
        grid = detect_programming_grid('assets/image.png')
        print("\nDetected grid (with colors):")
        print_grid(grid)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please ensure:")
        print("1. The image file exists and is named 'image.png'")
        print("2. The image is readable and not corrupted")
        print("3. You have sufficient permissions to read the file")