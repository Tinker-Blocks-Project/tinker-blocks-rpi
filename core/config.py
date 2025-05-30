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

    # Grid detection corner points (hardcoded for current setup)
    grid_corners: dict = {
        "top_right": (1054, 104),
        "top_left": (30, 91),
        "bottom_left": (33, 1712),
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
