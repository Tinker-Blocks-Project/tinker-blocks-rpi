import cv2
import numpy as np
import pytesseract

def read_number_from_image(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Convert to RGB (OpenCV uses BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    
    # Threshold the image to get black text on white background
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Scale up the image for better OCR
    scaled = cv2.resize(thresh, (thresh.shape[1]*2, thresh.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    
    # Perform OCR with specific settings for numbers
    number = pytesseract.image_to_string(scaled, 
        config='--psm 6 -c tessedit_char_whitelist=0123456789')
    number = number.strip()
    
    if number.isdigit():
        return int(number)
    return None

if __name__ == "__main__":
    try:
        number = read_number_from_image('assets/number.png')
        if number is not None:
            print(f"Detected number: {number}")
        else:
            print("No valid number detected")
    except Exception as e:
        print(f"Error: {str(e)}")