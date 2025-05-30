from pydantic import BaseModel, Field, ConfigDict
from vision.image import Image


class GridSquare(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    row: int = Field(..., description="Row index of the square in the grid")
    col: int = Field(..., description="Column index of the square in the grid")
    image: Image = Field(..., description="The image data for this square")
    corners: list[tuple[int, int]] = Field(
        ..., description="Corner points of the square"
    )

    def save(self, path: str) -> None:
        """Save the square image to a file."""
        self.image.save(path)

    def draw_corners(self) -> Image:
        """Draw the corners of the square on the image."""
        result = self.image
        for corner in self.corners:
            result = result.draw_circle(corner, 3)
        return result
