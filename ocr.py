import cv2
import pytesseract
import os
custom_config = r'--oem 3 --psm 8'  # For single word or number
# Optional: Enhance OCR for small images
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize image (3x)
    scale_percent = 300
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )

    return thresh

def extract_text_from_images(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(folder_path, filename)
            image = cv2.imread(path)

            if image is None:
                print(f"Error loading {filename}")
                continue

            processed = preprocess_image(image)
            text = pytesseract.image_to_string(processed, config=custom_config)
            print(f"{filename}: '{text.strip()}'")

# Example usage
# Set the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
extract_text_from_images("output/squares")
