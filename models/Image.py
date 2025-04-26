from .ImageOperations import ImageOperations
import cv2
import numpy as np


class Image(ImageOperations):
    def __init__(self, path: str, scale_percent: int = 100):
        self.path = path
        self.scale_percent = scale_percent
        super().__init__(None)  # Initialize with no image
        self.read_image()
        self.rotate_90_clockwise()
        self.resize()

    def read_image(self) -> None:
        """Read the image from the specified path."""
        self.image = cv2.imread(self.path)
        if self.image is None:
            raise ValueError(f"Failed to load image from {self.path}")

    def rotate_90_clockwise(self) -> None:
        """Rotate the image 90 degrees clockwise."""
        self.image = super().rotate_90_clockwise()

    def resize(self) -> None:
        """Resize the image by the specified scale percentage."""
        self.image = super().resize(self.scale_percent)
