import cv2
import numpy as np
from .GridSquare import GridSquare


class PerspectiveGrid:
    def __init__(self, top_right, top_left, bottom_left, bottom_right):
        self.top_right = np.array(top_right)
        self.top_left = np.array(top_left)
        self.bottom_left = np.array(bottom_left)
        self.bottom_right = np.array(bottom_right)
        self.matrix, self.dimensions = self._create_perspective_transform()

    def _create_perspective_transform(self):
        """Create a perspective transform matrix for the given corners."""
        src_points = np.float32(
            [self.top_right, self.top_left, self.bottom_left, self.bottom_right]
        )
        width = max(
            np.linalg.norm(self.top_right - self.top_left),
            np.linalg.norm(self.bottom_right - self.bottom_left),
        )
        height = max(
            np.linalg.norm(self.top_left - self.bottom_left),
            np.linalg.norm(self.top_right - self.bottom_right),
        )

        dst_points = np.float32(
            [
                [width - 1, 0],  # top right
                [0, 0],  # top left
                [0, height - 1],  # bottom left
                [width - 1, height - 1],  # bottom right
            ]
        )

        return cv2.getPerspectiveTransform(src_points, dst_points), (width, height)

    def transform_point(self, point):
        """Transform a point using the perspective transform matrix."""
        point_homogeneous = np.array([point[0], point[1], 1])
        transformed = np.dot(self.matrix, point_homogeneous)
        return tuple(map(int, transformed[:2] / transformed[2]))

    def inverse_transform_point(self, point):
        """Transform a point using the inverse perspective transform matrix."""
        point_homogeneous = np.array([point[0], point[1], 1])
        transformed = np.dot(np.linalg.inv(self.matrix), point_homogeneous)
        return tuple(map(int, transformed[:2] / transformed[2]))

    def get_grid_squares(self, image, rows=16, cols=10):
        """Get all grid squares with their coordinates and images."""
        squares = []
        width, height = self.dimensions

        # Calculate grid cell dimensions
        cell_width = width / cols
        cell_height = height / rows

        # For each grid cell
        for row in range(rows):
            for col in range(cols):
                # Calculate corners in destination space
                dst_corners = [
                    (col * cell_width, row * cell_height),  # top left
                    ((col + 1) * cell_width, row * cell_height),  # top right
                    ((col + 1) * cell_width, (row + 1) * cell_height),  # bottom right
                    (col * cell_width, (row + 1) * cell_height),  # bottom left
                ]

                # Transform corners back to source space
                src_corners = [
                    self.inverse_transform_point(corner) for corner in dst_corners
                ]

                # Create mask for this square
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(src_corners)], 255)

                # Extract the square
                square_image = cv2.bitwise_and(image, image, mask=mask)

                # Find the bounding box of non-zero pixels
                non_zero = cv2.findNonZero(mask)
                if non_zero is not None:
                    x, y, w, h = cv2.boundingRect(non_zero)
                    # Crop the image to the bounding box
                    square_image = square_image[y : y + h, x : x + w]

                    # Update corners to be relative to the cropped image
                    src_corners = [(cx - x, cy - y) for cx, cy in src_corners]

                # Create GridSquare object
                square = GridSquare(
                    row=row, col=col, image=square_image, corners=src_corners
                )
                squares.append(square)

        return squares

    def draw_grid(self, image, rows=16, cols=10):
        """Draw the grid on the image."""
        grid_image = image.copy()
        width, height = self.dimensions

        # Draw horizontal lines
        for i in range(rows + 1):
            y = int(i * height / rows)
            # Create points in the destination space
            start_dst = np.array([0, y, 1])
            end_dst = np.array([width - 1, y, 1])

            # Transform back to source space
            start_src = np.dot(np.linalg.inv(self.matrix), start_dst)
            end_src = np.dot(np.linalg.inv(self.matrix), end_dst)

            # Convert to image coordinates
            start_point = tuple(map(int, start_src[:2] / start_src[2]))
            end_point = tuple(map(int, end_src[:2] / end_src[2]))

            # Draw the line
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        # Draw vertical lines
        for i in range(cols + 1):
            x = int(i * width / cols)
            # Create points in the destination space
            start_dst = np.array([x, 0, 1])
            end_dst = np.array([x, height - 1, 1])

            # Transform back to source space
            start_src = np.dot(np.linalg.inv(self.matrix), start_dst)
            end_src = np.dot(np.linalg.inv(self.matrix), end_dst)

            # Convert to image coordinates
            start_point = tuple(map(int, start_src[:2] / start_src[2]))
            end_point = tuple(map(int, end_src[:2] / end_src[2]))

            # Draw the line
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        return grid_image
