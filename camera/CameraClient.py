import requests
import os

def capture_image_client(pi_ip="192.168.1.18", save_dir="assets", save_name="downloaded_image.jpg"):
    """
    Sends a request to the Raspberry Pi server to capture an image
    and saves it in the specified local assets folder.

    Returns:
        str: Relative path to the saved image (e.g., 'assets/downloaded_image.jpg') or None on failure.
    """
    try:
        url = f"http://{pi_ip}:5000/capture"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            os.makedirs(save_dir, exist_ok=True)  # ensure assets/ exists

            save_path = os.path.join(save_dir, save_name)
            with open(save_path, "wb") as f:
                f.write(response.content)

            print(f"Image saved to {save_path}")
            return save_path
        else:
            print(f"Failed to capture image: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Error connecting to Raspberry Pi: {e}")
        return None
