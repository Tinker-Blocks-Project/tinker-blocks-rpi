import cv2

class ImageOperations:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)

    def convert_to_gray(self):
        if self.image is None:
            raise ValueError("Image not found or invalid image path.")
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return gray_image