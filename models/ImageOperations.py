import cv2
import numpy as np
from typing import Optional, Tuple


class ImageOperations:
    def __init__(self, image: Optional[np.ndarray] = None):
        self.image = image

    def to_grayscale(self) -> np.ndarray:
        """Convert the image to grayscale."""
        if self.image is None:
            raise ValueError("Image not loaded. Set image first.")
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def resize(self, scale_percent: int = 100) -> np.ndarray:
        """Resize the image by a percentage."""
        if self.image is None:
            raise ValueError("Image not loaded. Set image first.")
        width = int(self.image.shape[1] * scale_percent / 100)
        height = int(self.image.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)

    def rotate_90_clockwise(self) -> np.ndarray:
        """Rotate the image 90 degrees clockwise."""
        if self.image is None:
            raise ValueError("Image not loaded. Set image first.")
        return cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)

    def get_image(self) -> Optional[np.ndarray]:
        """Get the current image."""
        return self.image

    def set_image(self, image: np.ndarray) -> None:
        """Set the current image."""
        self.image = image

    def show(self, window_name: str = "Image") -> None:
        """Display the image in a window."""
        if self.image is None:
            raise ValueError("Image not loaded. Set image first.")
        cv2.imshow(window_name, self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
