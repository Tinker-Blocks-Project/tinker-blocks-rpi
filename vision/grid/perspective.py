import cv2
import numpy as np
from typing import Any, cast
from numpy.typing import NDArray
from pydantic import BaseModel, Field, ConfigDict
from vision.grid.square import GridSquare
from vision.image import Image


class PerspectiveGrid(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    top_right: tuple[int, int] = Field(..., description="Top right corner coordinates")
    top_left: tuple[int, int] = Field(..., description="Top left corner coordinates")
    bottom_left: tuple[int, int] = Field(
        ..., description="Bottom left corner coordinates"
    )
    bottom_right: tuple[int, int] = Field(
        ..., description="Bottom right corner coordinates"
    )
    matrix: NDArray[Any] = Field(..., description="Perspective transform matrix")
    dimensions: tuple[float, float] = Field(
        ..., description="Width and height of the transformed grid"
    )

    def __init__(self, **data):
        # Calculate matrix and dimensions before calling super().__init__
        top_right = np.array(data["top_right"], dtype=np.float32)
        top_left = np.array(data["top_left"], dtype=np.float32)
        bottom_left = np.array(data["bottom_left"], dtype=np.float32)
        bottom_right = np.array(data["bottom_right"], dtype=np.float32)

        # Create source points array
        src_points = np.array(
            [top_right, top_left, bottom_left, bottom_right], dtype=np.float32
        )

        # Calculate width and height using numpy's max
        width = float(
            np.maximum(
                np.linalg.norm(top_right - top_left),
                np.linalg.norm(bottom_right - bottom_left),
            )
        )
        height = float(
            np.maximum(
                np.linalg.norm(top_left - bottom_left),
                np.linalg.norm(top_right - bottom_right),
            )
        )

        # Create destination points array
        dst_points = np.array(
            [
                [width - 1, 0],  # top right
                [0, 0],  # top left
                [0, height - 1],  # bottom left
                [width - 1, height - 1],  # bottom right
            ],
            dtype=np.float32,
        )

        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        dimensions = (width, height)

        # Add matrix and dimensions to data
        data["matrix"] = matrix
        data["dimensions"] = dimensions

        super().__init__(**data)

    def transform_point(self, point: tuple[int, int]) -> tuple[int, int]:
        """Transform a point using the perspective transform matrix."""
        point_homogeneous = np.array([point[0], point[1], 1], dtype=np.float32)
        transformed = np.dot(self.matrix, point_homogeneous)
        result = tuple(map(int, transformed[:2] / transformed[2]))
        return cast(tuple[int, int], result)

    def inverse_transform_point(self, point: tuple[float, float]) -> tuple[int, int]:
        """Transform a point using the inverse perspective transform matrix."""
        point_homogeneous = np.array([point[0], point[1], 1], dtype=np.float32)
        transformed = np.dot(np.linalg.inv(self.matrix), point_homogeneous)
        result = tuple(map(int, transformed[:2] / transformed[2]))
        return cast(tuple[int, int], result)

    def get_grid_squares(
        self,
        image: Image,
        rows: int = 16,
        cols: int = 10,
    ) -> list[GridSquare]:
        """Get all grid squares with their coordinates and images."""
        squares: list[GridSquare] = []
        width, height = self.dimensions
        image_array = image.image

        # Calculate grid cell dimensions
        cell_width = width / cols
        cell_height = height / rows

        # For each grid cell
        for row in range(rows):
            for col in range(cols):
                # Calculate corners in destination space
                dst_corners = [
                    (float(col * cell_width), float(row * cell_height)),  # top left
                    (
                        float((col + 1) * cell_width),
                        float(row * cell_height),
                    ),  # top right
                    (
                        float((col + 1) * cell_width),
                        float((row + 1) * cell_height),
                    ),  # bottom right
                    (
                        float(col * cell_width),
                        float((row + 1) * cell_height),
                    ),  # bottom left
                ]

                # Transform corners back to source space
                src_corners = [
                    self.inverse_transform_point(corner) for corner in dst_corners
                ]

                # Create mask for this square
                mask = np.zeros(image_array.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(src_corners, dtype=np.int32)], (255,))

                # Extract the square
                square_image = cv2.bitwise_and(image_array, image_array, mask=mask)

                # Find the bounding box of non-zero pixels
                non_zero = cv2.findNonZero(mask)
                if non_zero is not None:
                    x, y, w, h = cv2.boundingRect(non_zero)
                    # Crop the image to the bounding box
                    square_image = square_image[y : y + h, x : x + w]

                    # Update corners to be relative to the cropped image

                # Create GridSquare object
                square = GridSquare(
                    row=row,
                    col=col,
                    image=Image(image=square_image),
                    corners=src_corners,
                )
                squares.append(square)

        return squares

    def draw_grid(
        self,
        image: Image,
        rows: int = 16,
        cols: int = 10,
        thickness: int = 2,
        color: tuple[int, int, int] = (0, 255, 0),
    ) -> Image:
        """Draw the grid on the image."""
        image_array = image.image.copy()
        width, height = self.dimensions

        # Draw horizontal lines
        for i in range(rows + 1):
            y = int(i * height / rows)
            # Create points in the destination space
            start_dst = np.array([0, y, 1], dtype=np.float32)
            end_dst = np.array([width - 1, y, 1], dtype=np.float32)

            # Transform back to source space
            start_src = np.dot(np.linalg.inv(self.matrix), start_dst)
            end_src = np.dot(np.linalg.inv(self.matrix), end_dst)

            # Convert to image coordinates
            start_point = tuple(map(int, start_src[:2] / start_src[2]))
            end_point = tuple(map(int, end_src[:2] / end_src[2]))

            # Draw the line
            cv2.line(image_array, start_point, end_point, color, thickness)

        # Draw vertical lines
        for i in range(cols + 1):
            x = int(i * width / cols)
            # Create points in the destination space
            start_dst = np.array([x, 0, 1], dtype=np.float32)
            end_dst = np.array([x, height - 1, 1], dtype=np.float32)

            # Transform back to source space
            start_src = np.dot(np.linalg.inv(self.matrix), start_dst)
            end_src = np.dot(np.linalg.inv(self.matrix), end_dst)

            # Convert to image coordinates
            start_point = tuple(map(int, start_src[:2] / start_src[2]))
            end_point = tuple(map(int, end_src[:2] / end_src[2]))

            # Draw the line
            cv2.line(image_array, start_point, end_point, color, thickness)

        return Image(image=image_array)
