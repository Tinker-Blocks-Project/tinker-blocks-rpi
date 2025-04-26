from image_processing.ImageOperations import ImageOperations
import cv2
import numpy as np


class Image(ImageOperations):
    def __init__(self, path, scale_percent=100):
        super().__init__(path)
        self.path = path
        self.scale_percent = scale_percent
        self.image = None
        self.read_image()
        self.rotate_90_clockwise()
        self.resize()

    def read_image(self):
        self.image = cv2.imread(self.path)

    def rotate_90_clockwise(self):
        if self.image is None:
            raise ValueError("Image not loaded. Call read_image() first.")
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)

    def resize(self):
        width = int(self.image.shape[1] * self.scale_percent / 100)
        height = int(self.image.shape[0] * self.scale_percent / 100)
        dim = (width, height)
        self.image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)

    def show(self, window_name="Image"):
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_MOUSEMOVE:
                pixel_value = self.image[y, x]
                print(f"Pixel at ({x}, {y}): {pixel_value}")

        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)

        cv2.imshow(window_name, self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def calculate_grid_vectors(self, top_right, top_left, bottom_left):
        # Calculate horizontal vector (right to left)
        horizontal_vector = np.array(top_left) - np.array(top_right)
        horizontal_unit_vector = horizontal_vector / 10  # Divide by 10 squares

        # Calculate vertical vector (top to bottom)
        vertical_vector = np.array(bottom_left) - np.array(top_left)
        vertical_unit_vector = vertical_vector / 16  # Divide by 16 squares

        return horizontal_unit_vector, vertical_unit_vector

    def draw_grid(self, top_right, top_left, bottom_left, bottom_right):
        if self.image is None:
            raise ValueError("Image not loaded. Call read_image() first.")

        # Create a copy of the image to draw on
        grid_image = self.image.copy()

        # Convert points to numpy arrays for easier calculation
        tr = np.array(top_right)
        tl = np.array(top_left)
        bl = np.array(bottom_left)
        br = np.array(bottom_right)

        # Draw horizontal lines
        for i in range(17):  # 16 squares + 1 line
            # Calculate interpolation factor
            t = i / 16.0

            # Calculate start and end points for this horizontal line
            start_point = tuple(map(int, tr + t * (br - tr)))
            end_point = tuple(map(int, tl + t * (bl - tl)))

            # Draw the line
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        # Draw vertical lines
        for i in range(11):  # 10 squares + 1 line
            # Calculate interpolation factor
            t = i / 10.0

            # Calculate start and end points for this vertical line
            start_point = tuple(map(int, tr + t * (tl - tr)))
            end_point = tuple(map(int, br + t * (bl - br)))

            # Draw the line
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        return grid_image

    def draw_perspective_grid(self, top_right, top_left, bottom_left, bottom_right):
        if self.image is None:
            raise ValueError("Image not loaded. Call read_image() first.")

        # Create a copy of the image to draw on
        grid_image = self.image.copy()

        # Define the source points (the four corners of the quadrilateral)
        src_points = np.float32([top_right, top_left, bottom_left, bottom_right])

        # Calculate the width and height of the destination rectangle
        width = max(
            np.linalg.norm(np.array(top_right) - np.array(top_left)),
            np.linalg.norm(np.array(bottom_right) - np.array(bottom_left)),
        )
        height = max(
            np.linalg.norm(np.array(top_left) - np.array(bottom_left)),
            np.linalg.norm(np.array(top_right) - np.array(bottom_right)),
        )

        # Define the destination points (a perfect rectangle)
        dst_points = np.float32(
            [
                [width - 1, 0],  # top right
                [0, 0],  # top left
                [0, height - 1],  # bottom left
                [width - 1, height - 1],  # bottom right
            ]
        )

        # Calculate the perspective transform matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Draw horizontal lines
        for i in range(17):  # 16 squares + 1 line
            y = int(i * height / 16)
            start_point = tuple(
                map(
                    int,
                    cv2.perspectiveTransform(
                        np.array([[[0, y]]], dtype=np.float32), matrix
                    )[0][0],
                )
            )
            end_point = tuple(
                map(
                    int,
                    cv2.perspectiveTransform(
                        np.array([[[width - 1, y]]], dtype=np.float32), matrix
                    )[0][0],
                )
            )
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        # Draw vertical lines
        for i in range(11):  # 10 squares + 1 line
            x = int(i * width / 10)
            start_point = tuple(
                map(
                    int,
                    cv2.perspectiveTransform(
                        np.array([[[x, 0]]], dtype=np.float32), matrix
                    )[0][0],
                )
            )
            end_point = tuple(
                map(
                    int,
                    cv2.perspectiveTransform(
                        np.array([[[x, height - 1]]], dtype=np.float32), matrix
                    )[0][0],
                )
            )
            cv2.line(grid_image, start_point, end_point, (0, 255, 0), 1)

        return grid_image
