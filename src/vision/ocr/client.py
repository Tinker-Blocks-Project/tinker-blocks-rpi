import requests
from typing import Any


class EasyOCRClient:
    def __init__(self, host: str) -> None:
        self.host = host

    def process_image(self, image_path: str) -> dict[str, Any] | None:
        url = f"http://{self.host}:5000/process-image"
        files = {"image": open(image_path, "rb")}

        response = requests.post(url, files=files)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error:", response.status_code, response.json())
            return None
