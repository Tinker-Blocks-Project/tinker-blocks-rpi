import cv2
import time
import os
from typing import Optional


def capture_image_local(
    save_path: str = "captured_image.jpg",
    camera_index: int = 0,
    warmup_time: float = 2.0,
) -> Optional[str]:
    """
    Capture an image using the local camera.

    Args:
        save_path: Path where the image should be saved
        camera_index: Camera device index (0 for default camera)
        warmup_time: Time to wait for camera warmup in seconds

    Returns:
        Path to the saved image file, or None if capture failed

    Raises:
        RuntimeError: If camera cannot be opened or image capture fails
    """
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera at index {camera_index}")

    try:
        # Warm up the camera
        time.sleep(warmup_time)

        # Capture frame
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the frame
        success = cv2.imwrite(save_path, frame)
        if not success:
            raise RuntimeError(f"Failed to save image to {save_path}")

        return save_path

    finally:
        # Release the camera
        cap.release()
