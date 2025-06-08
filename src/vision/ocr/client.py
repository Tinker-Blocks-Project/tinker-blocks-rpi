import requests


async def ocr_text_client(image_path: str) -> list[list[str]]:
    """
    Send an image to the OCR server and get back the 2D grid of text.

    Args:
        image_path: Path to the image file to process

    Returns:
        2D list representing the grid layout of detected text

    Raises:
        requests.RequestException: If the server request fails
        ValueError: If the server returns an error response
    """
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post("http://localhost:8766/process", files=files)

    if response.status_code == 200:
        return response.json()["grid"]
    else:
        error_info = (
            response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else response.text
        )
        raise ValueError(f"OCR server error: {response.status_code} - {error_info}")
