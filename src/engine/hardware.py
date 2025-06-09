"""Hardware interface for communicating with the physical car."""

from typing import Protocol, Optional
import logging

from core import CarAPIClient, config

logger = logging.getLogger(__name__)


class HardwareInterface(Protocol):
    """Protocol for hardware interface implementations."""

    async def move_distance(self, distance_cm: float) -> bool:
        """Move the car by a specific distance in cm.

        Args:
            distance_cm: Distance to move (positive = forward, negative = backward)

        Returns:
            True if movement was successful
        """
        ...

    async def rotate_degrees(self, degrees: float) -> bool:
        """Rotate the car by specific degrees.

        Args:
            degrees: Degrees to rotate (positive = right, negative = left)

        Returns:
            True if rotation was successful
        """
        ...

    async def set_pen_down(self, down: bool) -> bool:
        """Set pen position.

        Args:
            down: True to lower pen, False to raise it

        Returns:
            True if pen control was successful
        """
        ...

    async def get_distance_cm(self) -> float:
        """Get ultrasonic sensor distance reading in cm.

        Returns:
            Distance in cm, or large value if no obstacle
        """
        ...

    async def is_obstacle_detected(self, threshold_cm: float = 30.0) -> bool:
        """Check if obstacle is detected within threshold.

        Args:
            threshold_cm: Distance threshold for obstacle detection

        Returns:
            True if obstacle is detected
        """
        ...

    async def is_black_detected(self) -> bool:
        """Check if IR sensor detects black surface.

        Returns:
            True if black surface is detected
        """
        ...


class CarHardware:
    """Real hardware implementation using CarAPIClient."""

    def __init__(self, api_client: Optional[CarAPIClient] = None):
        """Initialize hardware interface.

        Args:
            api_client: Car API client instance, or None to create default
        """
        self.api_client = api_client or CarAPIClient(
            base_url=config.car_api_url, timeout=config.car_api_timeout
        )

    async def _safe_api_call(self, api_call, operation_name: str, *args, **kwargs):
        """Safely execute an API call with logging and error handling."""
        try:
            logger.info(f"🔧 {operation_name}")
            logger.debug(f"   ↳ API call args: {args}")
            logger.debug(f"   ↳ API call kwargs: {kwargs}")

            response = await api_call(*args, **kwargs)

            logger.debug(
                f"   ↳ Raw API response: success={response.success}, result={response.result}, error='{response.error}'"
            )

            if response.success:
                logger.debug(
                    f"✅ {operation_name} successful: {response.result} (type: {type(response.result).__name__})"
                )
                return response.result, True
            else:
                logger.error(f"❌ {operation_name} failed: {response.error}")
                return None, False

        except Exception as e:
            logger.error(f"💥 Error during {operation_name}: {e}")
            return None, False

    async def move_distance(self, distance_cm: float) -> bool:
        """Move the car by a specific distance in cm."""
        speed = 100 if distance_cm >= 0 else -100
        result, success = await self._safe_api_call(
            self.api_client.move,
            f"Moving car {distance_cm}cm at speed {speed}",
            speed=speed,
            distance=abs(distance_cm),
            enable_yaw_correction=True,
        )
        return success

    async def rotate_degrees(self, degrees: float) -> bool:
        """Rotate the car by specific degrees."""
        result, success = await self._safe_api_call(
            self.api_client.rotate,
            f"Rotating car {degrees} degrees",
            angle=degrees,
            speed=100,
        )
        return success

    async def set_pen_down(self, down: bool) -> bool:
        """Set pen position."""
        action = "down" if down else "up"
        result, success = await self._safe_api_call(
            self.api_client.pen_control,
            f"Setting pen {action}",
            action=action,
        )
        return success

    async def get_distance_cm(self) -> float:
        """Get ultrasonic sensor distance reading in cm."""
        result, success = await self._safe_api_call(
            self.api_client.get_sensor_data,
            "Reading distance sensor",
            action="distance",
        )

        logger.debug(
            f"📏 Distance sensor - success: {success}, result: {result}, type: {type(result).__name__}"
        )

        if success and isinstance(result, (int, float)):
            distance = float(result)
            logger.debug(f"📏 Distance sensor returning: {distance}cm")
            return distance
        elif success:
            # Try to convert string to float (in case ESP32 returns string)
            try:
                distance = float(result)
                logger.debug(
                    f"📏 Distance sensor (converted from string): {distance}cm"
                )
                return distance
            except (ValueError, TypeError):
                logger.warning(
                    f"📏 Distance sensor - could not convert result '{result}' to float, using fallback"
                )
        else:
            logger.warning(f"📏 Distance sensor - API call failed, using fallback")

        logger.warning(f"📏 Distance sensor returning fallback value: 999.0cm")
        return 999.0

    async def is_obstacle_detected(self, threshold_cm: float = 30.0) -> bool:
        """Check if obstacle is detected within threshold."""
        result, success = await self._safe_api_call(
            self.api_client.get_sensor_data,
            f"Checking obstacle (threshold: {threshold_cm}cm)",
            action="obstacle",
            threshold=threshold_cm,
        )

        logger.debug(
            f"🚧 Obstacle sensor - success: {success}, result: {result}, type: {type(result).__name__}"
        )

        if success and isinstance(result, bool):
            logger.debug(f"🚧 Obstacle sensor returning: {result}")
            return result
        else:
            logger.warning(f"🚧 Obstacle sensor - invalid result, returning False")
            return False

    async def is_black_detected(self) -> bool:
        """Check if IR sensor detects black surface."""
        result, success = await self._safe_api_call(
            self.api_client.get_ir_data,
            "Reading IR sensor",
            action="black_obstacle",
        )

        logger.debug(
            f"⚫ IR sensor - success: {success}, result: {result}, type: {type(result).__name__}"
        )

        if success and isinstance(result, bool):
            logger.debug(f"⚫ IR sensor returning: {result}")
            return result
        else:
            logger.warning(f"⚫ IR sensor - invalid result, returning False")
            return False


class MockHardware:
    """Mock hardware implementation for testing."""

    def __init__(self):
        """Initialize mock hardware with default sensor values."""
        self.distance_reading = 50.0
        self.black_detected = False
        self.pen_is_down = False

        # Track actual movements for testing
        self.total_distance_moved = 0.0
        self.total_degrees_rotated = 0.0
        self.movement_history = []
        self.rotation_history = []

    async def move_distance(self, distance_cm: float) -> bool:
        """Mock movement - just track the distance."""
        logger.info(f"[MOCK] Moving {distance_cm}cm")
        self.total_distance_moved += distance_cm
        self.movement_history.append(distance_cm)
        return True

    async def rotate_degrees(self, degrees: float) -> bool:
        """Mock rotation - just track the degrees."""
        logger.info(f"[MOCK] Rotating {degrees} degrees")
        self.total_degrees_rotated += degrees
        self.rotation_history.append(degrees)
        return True

    async def set_pen_down(self, down: bool) -> bool:
        """Mock pen control."""
        logger.info(f"[MOCK] Setting pen {'down' if down else 'up'}")
        self.pen_is_down = down
        return True

    async def get_distance_cm(self) -> float:
        """Return mock distance reading."""
        return self.distance_reading

    async def is_obstacle_detected(self, threshold_cm: float = 30.0) -> bool:
        """Return mock obstacle detection."""
        return self.distance_reading < threshold_cm

    async def is_black_detected(self) -> bool:
        """Return mock black detection."""
        return self.black_detected

    def reset(self):
        """Reset mock hardware state for testing."""
        self.total_distance_moved = 0.0
        self.total_degrees_rotated = 0.0
        self.movement_history.clear()
        self.rotation_history.clear()
        self.pen_is_down = False
