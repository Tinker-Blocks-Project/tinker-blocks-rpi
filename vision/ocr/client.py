import requests


class EasyOCRClient:
    def __init__(self, host):
        self.host = host

    def process_image(self, image_path):
        url = f"http://{self.host}:5000/process-image"
        files = {"image": open(image_path, "rb")}

        response = requests.post(url, files=files)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error:", response.status_code, response.json())
