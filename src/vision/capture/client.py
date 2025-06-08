import requests
import os
from typing import Optional


def capture_image_client(
    pi_ip: str = "192.168.1.100", save_path: str = "captured_image.jpg"
) -> Optional[str]:
    """
    Capture an image from the Raspberry Pi and save it locally.

    Args:
        pi_ip: IP address of the Raspberry Pi
        save_path: Local path where the image should be saved

    Returns:
        Path to the saved image file, or None if capture failed

    Raises:
        requests.RequestException: If connection to Pi fails
        ValueError: If the server returns an error response
    """
    url = f"http://{pi_ip}:8000/capture"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the image
            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path
        else:
            raise ValueError(
                f"Failed to capture image: {response.status_code} - {response.text}"
            )

    except requests.exceptions.RequestException as e:
        raise requests.RequestException(
            f"Error connecting to Raspberry Pi at {pi_ip}: {e}"
        )

    return None
