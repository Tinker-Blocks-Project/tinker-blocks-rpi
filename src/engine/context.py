"""Execution context for the TinkerBlocks engine."""

from typing import Protocol, Callable, Awaitable, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field

from .types import Position, Direction, Number, SensorType

if TYPE_CHECKING:
    from .hardware import HardwareInterface


class SensorInterface(Protocol):
    """Interface for sensor readings."""

    async def get_distance(self) -> float:
        """Get ultrasonic distance reading in cm."""
        ...

    async def is_obstacle_detected(self) -> bool:
        """Check if obstacle is within threshold distance."""
        ...

    async def is_black_detected(self) -> bool:
        """Check if IR sensor detects black surface."""
        ...

    async def is_black_lost(self) -> bool:
        """Check if IR sensor lost black surface."""
        ...


class MockSensors:
    """Mock sensor implementation for testing."""

    def __init__(self):
        self.distance = 100.0
        self.black_detected = False
        self.obstacle_threshold = 30.0

    async def get_distance(self) -> float:
        return self.distance

    async def is_obstacle_detected(self) -> bool:
        return self.distance < self.obstacle_threshold

    async def is_black_detected(self) -> bool:
        return self.black_detected

    async def is_black_lost(self) -> bool:
        return not self.black_detected


@dataclass
class ExecutionContext:
    """Context that maintains state during program execution."""

    # Position and orientation (for tracking purposes)
    position: Position = field(default_factory=lambda: Position(0, 0))
    direction: Direction = Direction.FORWARD

    # Variables
    variables: dict[str, Number | bool] = field(default_factory=dict)

    # Drawing state
    pen_down: bool = False
    path: list[Position] = field(default_factory=list)

    # Execution tracking
    steps_executed: int = 0
    max_steps: int = 10000  # Prevent infinite loops

    # Hardware interface for actual control
    hardware: Union["HardwareInterface", None] = None

    # Legacy sensors interface (for backward compatibility)
    sensors: SensorInterface = field(default_factory=MockSensors)

    # Callbacks
    send_message: Callable[[str], Awaitable[None]] | None = None
    check_cancelled: Callable[[], bool] | None = None

    def get_direction_vector(self) -> Position:
        """Get unit vector for current direction."""
        if self.direction == Direction.FORWARD:
            return Position(0, 1)
        elif self.direction == Direction.BACKWARD:
            return Position(0, -1)
        elif self.direction == Direction.LEFT:
            return Position(-1, 0)
        elif self.direction == Direction.RIGHT:
            return Position(1, 0)
        return Position(0, 0)

    async def move(self, distance: float):
        """Move the car by the given distance in current direction."""
        # Use hardware interface if available
        if self.hardware:
            # Convert logical distance to real-world distance in cm
            distance_cm = distance * 10  # 1 logical unit = 10cm
            success = await self.hardware.move_distance(distance_cm)

            if not success and self.send_message:
                await self.send_message(
                    f"⚠️ Hardware movement failed for distance {distance_cm}cm"
                )

        # Update position tracking regardless of hardware success
        # Get direction vector based on current orientation
        if self.direction == Direction.FORWARD:
            dx, dy = 0, 1
        elif self.direction == Direction.RIGHT:
            dx, dy = 1, 0
        elif self.direction == Direction.BACKWARD:
            dx, dy = 0, -1
        elif self.direction == Direction.LEFT:
            dx, dy = -1, 0
        else:
            dx, dy = 0, 0

        # Calculate new position
        new_position = Position(
            self.position.x + dx * distance, self.position.y + dy * distance
        )

        # Track path if pen is down
        if self.pen_down:
            self.path.append(self.position)
            self.path.append(new_position)

        self.position = new_position
        self.steps_executed += 1

    async def turn(self, degrees: float):
        """Turn the car by the given degrees (positive = right, negative = left)."""
        # Use hardware interface if available
        if self.hardware:
            success = await self.hardware.rotate_degrees(degrees)

            if not success and self.send_message:
                await self.send_message(
                    f"⚠️ Hardware rotation failed for {degrees} degrees"
                )

        # Update direction tracking regardless of hardware success
        # Normalize degrees to -360 to 360
        degrees = degrees % 360
        if degrees > 180:
            degrees -= 360

        # Current direction to degrees
        current_degrees = {
            Direction.FORWARD: 0,
            Direction.RIGHT: 90,
            Direction.BACKWARD: 180,
            Direction.LEFT: 270,
        }[self.direction]

        # Calculate new direction
        new_degrees = (current_degrees + degrees) % 360

        # Convert back to Direction
        if new_degrees == 0:
            self.direction = Direction.FORWARD
        elif new_degrees == 90:
            self.direction = Direction.RIGHT
        elif new_degrees == 180:
            self.direction = Direction.BACKWARD
        elif new_degrees == 270:
            self.direction = Direction.LEFT
        else:
            # For non-90 degree turns, pick closest cardinal direction
            if 315 <= new_degrees or new_degrees < 45:
                self.direction = Direction.FORWARD
            elif 45 <= new_degrees < 135:
                self.direction = Direction.RIGHT
            elif 135 <= new_degrees < 225:
                self.direction = Direction.BACKWARD
            else:
                self.direction = Direction.LEFT

        self.steps_executed += 1

    def set_variable(self, name: str, value: Number | bool):
        """Set a variable value."""
        self.variables[name] = value
        self.steps_executed += 1

    def get_variable(self, name: str) -> Number | bool:
        """Get a variable value, defaulting to 0 if not set."""
        return self.variables.get(name, 0)

    async def get_sensor_value(self, sensor_type: SensorType) -> Number | bool:
        """Get sensor reading."""
        # Use hardware interface if available, otherwise fall back to legacy sensors
        if self.hardware:
            if sensor_type == SensorType.DISTANCE:
                return await self.hardware.get_distance_cm()
            elif sensor_type == SensorType.OBSTACLE:
                return await self.hardware.is_obstacle_detected()
            elif sensor_type == SensorType.BLACK_DETECTED:
                return await self.hardware.is_black_detected()
            elif sensor_type == SensorType.BLACK_LOST:
                return not await self.hardware.is_black_detected()
        else:
            # Fall back to legacy sensor interface
            if sensor_type == SensorType.DISTANCE:
                return await self.sensors.get_distance()
            elif sensor_type == SensorType.OBSTACLE:
                return await self.sensors.is_obstacle_detected()
            elif sensor_type == SensorType.BLACK_DETECTED:
                return await self.sensors.is_black_detected()
            elif sensor_type == SensorType.BLACK_LOST:
                return await self.sensors.is_black_lost()
        return 0

    def increment_steps(self):
        """Increment step counter and check for runaway execution."""
        self.steps_executed += 1
        if self.steps_executed > self.max_steps:
            raise RuntimeError(f"Maximum steps ({self.max_steps}) exceeded")

    def get_state_dict(self) -> dict[str, Any]:
        """Get current state as a dictionary."""
        return {
            "position": {"x": self.position.x, "y": self.position.y},
            "direction": self.direction.value,
            "variables": dict(self.variables),
            "pen_down": self.pen_down,
            "steps_executed": self.steps_executed,
            "path": [(p.x, p.y) for p in self.path] if self.path else [],
        }
