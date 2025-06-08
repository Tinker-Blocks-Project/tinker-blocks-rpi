import cv2
import numpy as np
from typing import Any, Sequence, Annotated
from numpy.typing import NDArray
from pydantic import BaseModel, Field, ConfigDict


class Grid(BaseModel):
    blocks: Annotated[list[list[str]], "2D list of texts representing the grid"]


class Image(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image: NDArray[Any] = Field(..., description="The image data as a numpy array")

    @classmethod
    def from_file(
        cls,
        path: str,
        scale_percent: int = 100,
    ) -> "Image":
        """Create an Image instance from a file path."""
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Failed to load image from {path}")
        return cls(image=image).resize(scale_percent)

    def show(self, window_name: str = "Image") -> None:
        """Display the image in a window."""
        cv2.imshow(window_name, self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def to_grayscale(self) -> "Image":
        """Convert the image to grayscale."""
        return Image(image=cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY))

    def resize(self, scale_percent: int = 100) -> "Image":
        """Resize the image by the specified scale percentage."""
        # Get dimensions using shape property
        shape: Sequence[int] = self.image.shape
        if len(shape) >= 2:
            height = int(shape[0])
            width = int(shape[1])
        else:
            raise ValueError("Invalid image shape")

        new_width = int(width * scale_percent / 100)
        new_height = int(height * scale_percent / 100)
        dim = (new_width, new_height)
        return Image(image=cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA))

    def rotate_90_clockwise(self) -> "Image":
        """Rotate the image 90 degrees clockwise."""
        return Image(image=cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE))

    def pad_with_white(self, padding: int = 10) -> "Image":
        """Pad the image with white pixels on all sides."""
        # Create a white border around the image
        if len(self.image.shape) == 3:
            # For color images, use a tuple of 255s
            value = (255, 255, 255)
        else:
            # For grayscale images, use a single 255
            value = 255

        # Use numpy's pad function instead of OpenCV's copyMakeBorder
        padded = np.pad(
            self.image,
            ((padding, padding), (padding, padding))
            + ((0, 0),) * (len(self.image.shape) - 2),
            mode="constant",
            constant_values=value,
        )
        return Image(image=padded)

    def crop_top(self, pixels: int) -> "Image":
        """Crop the specified number of pixels from the top of the image."""
        return Image(image=self.image[pixels:, :])

    def crop_bottom(self, pixels: int) -> "Image":
        """Crop the specified number of pixels from the bottom of the image."""
        return Image(image=self.image[:-pixels, :])

    def crop_left(self, pixels: int) -> "Image":
        """Crop the specified number of pixels from the left of the image."""
        return Image(image=self.image[:, pixels:])

    def crop_right(self, pixels: int) -> "Image":
        """Crop the specified number of pixels from the right of the image."""
        return Image(image=self.image[:, :-pixels])

    def save(self, path: str) -> None:
        """Save the image to a file."""
        cv2.imwrite(path, self.image)

    def draw_circle(
        self,
        center: tuple[int, int],
        radius: int,
        color: tuple[int, int, int] = (0, 255, 0),
        thickness: int = -1,
    ) -> "Image":
        """Draw a circle on the image."""
        image_copy = self.image.copy()
        cv2.circle(image_copy, center, radius, color, thickness)
        return Image(image=image_copy)
