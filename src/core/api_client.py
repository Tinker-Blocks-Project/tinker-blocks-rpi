"""API client for communicating with the ESP32 car."""

import asyncio
import requests
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CarResponse:
    """Response from the car API."""

    success: bool
    result: Any = None
    error: str = ""


class CarAPIClient:
    """Client for communicating with the ESP32 car API."""

    def __init__(self, base_url: str = "http://192.168.1.100", timeout: float = 10.0):
        """Initialize the API client.

        Args:
            base_url: Base URL of the ESP32 car API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info(
            f"🌐 CarAPIClient initialized with base_url: {self.base_url}, timeout: {self.timeout}s"
        )

    async def _post(
        self, endpoint: str, data: Dict[str, Union[str, int, float, bool]]
    ) -> CarResponse:
        """Make a POST request to the car API.

        Args:
            endpoint: API endpoint (e.g., '/api/move')
            data: JSON data to send

        Returns:
            CarResponse with success status and result/error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"Sending POST to {url} with data: {data}")

            # Run requests in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: requests.post(url, json=data, timeout=self.timeout)
            )

            logger.debug(f"Received response: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                logger.debug(f"Parsed JSON response: {response_data}")

                # Try both "result" and "success_result" keys for backward compatibility
                result = response_data.get("result") or response_data.get(
                    "success_result"
                )

                return CarResponse(
                    success=response_data.get("success", False),
                    result=result,
                    error=response_data.get("error", ""),
                )
            else:
                return CarResponse(
                    success=False, error=f"HTTP {response.status_code}: {response.text}"
                )

        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to {url}")
            return CarResponse(success=False, error="Connection timeout")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error connecting to {url}: {e}")
            return CarResponse(success=False, error=f"Connection error: {e}")

        except Exception as e:
            logger.error(f"Unexpected error calling {url}: {e}")
            return CarResponse(success=False, error=f"Unexpected error: {e}")

    async def move(
        self,
        speed: int = 100,
        distance: Optional[float] = None,
        time_ms: Optional[int] = None,
        check_ultrasonic: bool = True,
        enable_yaw_correction: bool = True,
    ) -> CarResponse:
        """Move the car forward or backward.

        Args:
            speed: Motor speed (0-255, negative for backward)
            distance: Distance to travel in cm (optional)
            time_ms: Time to move in milliseconds (optional)
            check_ultrasonic: Whether to check for obstacles
            enable_yaw_correction: Whether to use gyro for straight movement

        Returns:
            CarResponse with movement result
        """
        data: Dict[str, Union[str, int, float, bool]] = {"speed": speed}

        if distance is not None:
            data["distance"] = distance
        if time_ms is not None:
            data["timeMs"] = time_ms
        if check_ultrasonic:
            data["checkUltrasonic"] = check_ultrasonic
        if not enable_yaw_correction:
            data["enableYawCorrection"] = enable_yaw_correction

        return await self._post("/api/move", data)

    async def rotate(
        self, angle: float, speed: int = 100, absolute: bool = False
    ) -> CarResponse:
        """Rotate the car.

        Args:
            angle: Angle to rotate in degrees (positive = right, negative = left)
            speed: Rotation speed (0-255)
            absolute: Whether angle is absolute or relative

        Returns:
            CarResponse with rotation result
        """
        data: Dict[str, Union[str, int, float, bool]] = {
            "angle": angle,
            "speed": speed,
            "absolute": absolute,
        }

        return await self._post("/api/rotate", data)

    async def pen_control(
        self, action: str, position: Optional[int] = None
    ) -> CarResponse:
        """Control the pen.

        Args:
            action: "up", "down", or "position"
            position: Pen position for "position" action

        Returns:
            CarResponse with pen control result
        """
        data: Dict[str, Union[str, int, float, bool]] = {"action": action}

        if position is not None:
            data["position"] = position

        return await self._post("/api/pen", data)

    async def get_sensor_data(
        self, action: str, threshold: Optional[float] = None
    ) -> CarResponse:
        """Get ultrasonic sensor data.

        Args:
            action: "distance" or "obstacle"
            threshold: Obstacle threshold for "obstacle" action

        Returns:
            CarResponse with sensor data
        """
        data: Dict[str, Union[str, int, float, bool]] = {"action": action}

        if threshold is not None:
            data["threshold"] = threshold

        return await self._post("/api/sensor", data)

    async def get_ir_data(self, action: str = "black_obstacle") -> CarResponse:
        """Get IR sensor data.

        Args:
            action: IR sensor action (currently only "black_obstacle")

        Returns:
            CarResponse with IR sensor data
        """
        data: Dict[str, Union[str, int, float, bool]] = {"action": action}
        return await self._post("/api/ir", data)

    async def get_gyro_data(self, action: str = "data") -> CarResponse:
        """Get gyroscope data.

        Args:
            action: "calibrate", "data", "yaw", or "reference"

        Returns:
            CarResponse with gyro data
        """
        data: Dict[str, Union[str, int, float, bool]] = {"action": action}
        return await self._post("/api/gyro", data)

    async def calibrate_gyro(self) -> CarResponse:
        """Calibrate the gyroscope."""
        return await self.get_gyro_data("calibrate")

    async def buzzer_control(self, action: str) -> CarResponse:
        """Control the buzzer.

        Args:
            action: "on" or "off"

        Returns:
            CarResponse with buzzer control result
        """
        data: Dict[str, Union[str, int, float, bool]] = {"action": action}
        return await self._post("/api/buzzer", data)


class MockCarAPIClient(CarAPIClient):
    """Mock implementation of CarAPIClient for testing."""

    def __init__(self, base_url: str = "mock://car", timeout: float = 1.0):
        super().__init__(base_url, timeout)
        self.distance_reading = 50.0
        self.black_detected = False
        self.pen_position = "up"
        self.buzzer_status = "off"

    async def _post(
        self, endpoint: str, data: Dict[str, Union[str, int, float, bool]]
    ) -> CarResponse:
        """Mock POST request that simulates car responses."""

        # Simulate small delay
        await asyncio.sleep(0.01)

        if endpoint == "/api/move":
            distance = data.get("distance", 1.0)
            # Handle string conversion for testing
            try:
                distance_val = float(distance)
            except (ValueError, TypeError):
                distance_val = 1.0
            return CarResponse(
                success=True,
                result={
                    "distance_traveled": distance_val,
                    "time_taken": int(abs(distance_val) * 100),  # Mock timing
                    "final_yaw": 0.0,
                },
            )

        elif endpoint == "/api/rotate":
            angle = data.get("angle", 0)
            angle_val = float(angle) if isinstance(angle, (int, float)) else 0.0
            return CarResponse(
                success=True,
                result={
                    "angle_turned": angle_val,
                    "time_ms": abs(int(angle_val * 10)),  # Mock timing
                    "direction_changes": 0,
                },
            )

        elif endpoint == "/api/pen":
            action = data.get("action")
            self.pen_position = str(action) if action else "unknown"
            return CarResponse(success=True, result=f"Pen {action}")

        elif endpoint == "/api/sensor":
            action = data.get("action")
            if action == "distance":
                return CarResponse(success=True, result=self.distance_reading)
            elif action == "obstacle":
                threshold = data.get("threshold", 30.0)
                threshold_val = (
                    float(threshold) if isinstance(threshold, (int, float)) else 30.0
                )
                return CarResponse(
                    success=True, result=self.distance_reading < threshold_val
                )

        elif endpoint == "/api/ir":
            return CarResponse(success=True, result=self.black_detected)

        elif endpoint == "/api/gyro":
            action = data.get("action")
            if action == "data":
                return CarResponse(
                    success=True,
                    result={
                        "accelX": 0.01,
                        "accelY": -0.98,
                        "accelZ": 0.02,
                        "gyroX": 0.0,
                        "gyroY": 0.0,
                        "gyroZ": 0.0,
                        "yaw": 0.0,
                    },
                )
            else:
                return CarResponse(success=True, result="Gyro calibrated")

        elif endpoint == "/api/buzzer":
            action = data.get("action")
            if action in ["on", "off"]:
                self.buzzer_status = str(action)
                result = "started" if action == "on" else "stopped"
                return CarResponse(success=True, result=result)
            else:
                return CarResponse(
                    success=False, error=f"Invalid buzzer action: {action}"
                )

        return CarResponse(success=False, error=f"Unknown endpoint: {endpoint}")
