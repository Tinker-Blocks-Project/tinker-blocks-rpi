from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""

    # Server settings
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8765

    # Camera settings
    camera_server_ip: str = "192.168.1.18"
    camera_server_port: int = 5000

    # OCR server settings
    ocr_server_ip: str = "192.168.1.102"
    ocr_server_port: int = 5000

    # Car API settings
    car_api_url: str = "http://192.168.88.9"
    car_api_timeout: float = 15.0

    # Grid detection corner points (hardcoded for current setup)
    grid_corners: dict = {
        "top_right": (1054, 104),
        "top_left": (10, 100),
        "bottom_left": (33, 1718),
        "bottom_right": (1014, 1726),
    }

    # Grid dimensions
    grid_rows: int = 16
    grid_cols: int = 10

    # File paths
    output_dir: str = "output"
    assets_dir: str = "assets"


# Global config instance
config = Config()
