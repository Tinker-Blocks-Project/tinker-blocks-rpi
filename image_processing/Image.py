from image_processing.ImageOperations import ImageOperations
import cv2


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
        if self.image is None:
            raise ValueError("Image not loaded. Call read_image() first.")
        width = int(self.image.shape[1] * self.scale_percent / 100)
        height = int(self.image.shape[0] * self.scale_percent / 100)
        dim = (width, height)
        self.image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)

    def show(self, window_name="Image"):
        if self.image is None:
            raise ValueError("Image not loaded. Call read_image() first.")
        cv2.imshow(window_name, self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image
