from typing import Protocol, runtime_checkable
from vision.types import Grid


@runtime_checkable
class OCRProtocol(Protocol):
    """Protocol defining the interface for OCR implementations."""

    async def process_image(self, image_path: str) -> Grid:
        """
        Process an image and return a Grid with text mapped to positions.

        Args:
            image_path: Path to the image file to process

        Returns:
            Grid object containing the 2D text layout
        """
        ...
