import easyocr
import cv2
import numpy as np
class EasyOCR:
    def __init__(self, languages=['en']):
        """
        Initialize the EasyOCR reader with the specified languages.
        """
        self.reader = easyocr.Reader(languages)
        self.text = []
    
    def detect_text(self, image_path):
        """
        Detect text in the image at the specified path.
        
        :param image_path: Path to the image file.
        :return: List of detected text regions and their bounding boxes.
        """
        # Read the image
        results = self.reader.readtext(image_path)
        
        return results
    
    def draw_boxes(self, image_path, results):
         # Load the image with OpenCV for drawing rectangles
        cv_image = cv2.imread(image_path)
            
        # Create a copy of the image to draw rectangles on
        cv_result = cv_image.copy()
        for (bbox, text, prob) in results:
            # If probability is high enough
            if prob > 0.4:
                # Extract coordinates
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = tuple(map(int, top_left))
                bottom_right = tuple(map(int, bottom_right))
                
                # Draw rectangle
                cv2.rectangle(cv_result, top_left, bottom_right, (0, 255, 0), 2)
                
                # Print coordinates and text
                print(f"Text: '{text}' - Corners: Top-Left({top_left[0]},{top_left[1]}), Bottom-Right({bottom_right[0]},{bottom_right[1]})")
                # Store the text in the dictionary
                self.text.append({
                    'text': text,
                    'corners': [[float(x), float(y)] for (x, y) in bbox]
                })
        # Save the result
        cv2.imwrite("output/text_detection_result.jpg", cv_result)
        print("\nText detection result saved to output/text_detection_result.jpg")
        return self.text
    def process_image(self, image_path):
        """
        Process the image to detect and draw text boxes.
        
        :param image_path: Path to the image file.
        """
        results = self.detect_text(image_path)
        return self.draw_boxes(image_path, results)
    