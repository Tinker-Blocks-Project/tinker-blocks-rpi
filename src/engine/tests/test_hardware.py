"""Tests for the hardware interface module."""

import pytest
from unittest.mock import Mock, AsyncMock

from ..hardware import CarHardware, MockHardware
from core import MockCarAPIClient, CarResponse


@pytest.mark.asyncio
async def test_mock_hardware_movement():
    """Test MockHardware movement tracking."""
    hardware = MockHardware()

    # Test forward movement
    success = await hardware.move_distance(10.5)
    assert success is True
    assert hardware.total_distance_moved == 10.5
    assert hardware.movement_history == [10.5]

    # Test backward movement
    success = await hardware.move_distance(-5.0)
    assert success is True
    assert hardware.total_distance_moved == 5.5  # 10.5 - 5.0
    assert hardware.movement_history == [10.5, -5.0]


@pytest.mark.asyncio
async def test_mock_hardware_rotation():
    """Test MockHardware rotation tracking."""
    hardware = MockHardware()

    # Test right rotation
    success = await hardware.rotate_degrees(90.0)
    assert success is True
    assert hardware.total_degrees_rotated == 90.0
    assert hardware.rotation_history == [90.0]

    # Test left rotation
    success = await hardware.rotate_degrees(-45.0)
    assert success is True
    assert hardware.total_degrees_rotated == 45.0  # 90 - 45
    assert hardware.rotation_history == [90.0, -45.0]


@pytest.mark.asyncio
async def test_mock_hardware_pen_control():
    """Test MockHardware pen control."""
    hardware = MockHardware()

    # Initial state
    assert hardware.pen_is_down is False

    # Test pen down
    success = await hardware.set_pen_down(True)
    assert success is True
    assert hardware.pen_is_down is True

    # Test pen up
    success = await hardware.set_pen_down(False)
    assert success is True
    assert hardware.pen_is_down is False


@pytest.mark.asyncio
async def test_mock_hardware_sensors():
    """Test MockHardware sensor readings."""
    hardware = MockHardware()

    # Test distance sensor
    distance = await hardware.get_distance_cm()
    assert distance == 50.0  # Default value

    # Test obstacle detection
    is_obstacle = await hardware.is_obstacle_detected()
    assert is_obstacle is False  # 50 > 30 (default threshold)

    is_obstacle = await hardware.is_obstacle_detected(threshold_cm=60.0)
    assert is_obstacle is True  # 50 < 60

    # Test black detection
    is_black = await hardware.is_black_detected()
    assert is_black is False  # Default value

    # Change mock values
    hardware.distance_reading = 15.0
    hardware.black_detected = True

    distance = await hardware.get_distance_cm()
    assert distance == 15.0

    is_obstacle = await hardware.is_obstacle_detected()
    assert is_obstacle is True  # 15 < 30

    is_black = await hardware.is_black_detected()
    assert is_black is True


@pytest.mark.asyncio
async def test_mock_hardware_reset():
    """Test MockHardware reset functionality."""
    hardware = MockHardware()

    # Make some changes
    await hardware.move_distance(10.0)
    await hardware.rotate_degrees(45.0)
    await hardware.set_pen_down(True)

    # Check state before reset
    assert hardware.total_distance_moved == 10.0
    assert hardware.total_degrees_rotated == 45.0
    assert hardware.pen_is_down is True
    assert len(hardware.movement_history) == 1
    assert len(hardware.rotation_history) == 1

    # Reset
    hardware.reset()

    # Check state after reset
    assert hardware.total_distance_moved == 0.0
    assert hardware.total_degrees_rotated == 0.0
    assert hardware.pen_is_down is False
    assert len(hardware.movement_history) == 0
    assert len(hardware.rotation_history) == 0


@pytest.mark.asyncio
async def test_car_hardware_successful_movement():
    """Test CarHardware with successful API responses."""
    # Create mock API client
    mock_api = MockCarAPIClient()
    hardware = CarHardware(api_client=mock_api)

    # Test forward movement
    success = await hardware.move_distance(15.0)
    assert success is True

    # Test backward movement
    success = await hardware.move_distance(-10.0)
    assert success is True


@pytest.mark.asyncio
async def test_car_hardware_failed_movement():
    """Test CarHardware with failed API responses."""
    # Create mock API client that returns failure
    mock_api = Mock()
    mock_api.move = AsyncMock(
        return_value=CarResponse(success=False, error="Motor error")
    )

    hardware = CarHardware(api_client=mock_api)

    success = await hardware.move_distance(10.0)
    assert success is False
    mock_api.move.assert_called_once()


@pytest.mark.asyncio
async def test_car_hardware_successful_rotation():
    """Test CarHardware rotation with successful API response."""
    mock_api = MockCarAPIClient()
    hardware = CarHardware(api_client=mock_api)

    # Test rotation
    success = await hardware.rotate_degrees(90.0)
    assert success is True


@pytest.mark.asyncio
async def test_car_hardware_failed_rotation():
    """Test CarHardware rotation with failed API response."""
    mock_api = Mock()
    mock_api.rotate = AsyncMock(
        return_value=CarResponse(success=False, error="Gyro error")
    )

    hardware = CarHardware(api_client=mock_api)

    success = await hardware.rotate_degrees(45.0)
    assert success is False
    mock_api.rotate.assert_called_once_with(angle=45.0, speed=100)


@pytest.mark.asyncio
async def test_car_hardware_pen_control():
    """Test CarHardware pen control."""
    mock_api = MockCarAPIClient()
    hardware = CarHardware(api_client=mock_api)

    # Test pen down
    success = await hardware.set_pen_down(True)
    assert success is True

    # Test pen up
    success = await hardware.set_pen_down(False)
    assert success is True


@pytest.mark.asyncio
async def test_car_hardware_failed_pen_control():
    """Test CarHardware pen control with failure."""
    mock_api = Mock()
    mock_api.pen_control = AsyncMock(
        return_value=CarResponse(success=False, error="Servo error")
    )

    hardware = CarHardware(api_client=mock_api)

    success = await hardware.set_pen_down(True)
    assert success is False
    mock_api.pen_control.assert_called_once_with(action="down")


@pytest.mark.asyncio
async def test_car_hardware_distance_sensor():
    """Test CarHardware distance sensor."""
    mock_api = MockCarAPIClient()
    # Set a specific distance reading
    mock_api.distance_reading = 25.5

    hardware = CarHardware(api_client=mock_api)

    distance = await hardware.get_distance_cm()
    assert distance == 25.5


@pytest.mark.asyncio
async def test_car_hardware_failed_distance_sensor():
    """Test CarHardware distance sensor with failure."""
    mock_api = Mock()
    mock_api.get_sensor_data = AsyncMock(
        return_value=CarResponse(success=False, error="Sensor error")
    )

    hardware = CarHardware(api_client=mock_api)

    distance = await hardware.get_distance_cm()
    assert distance == 999.0  # Fallback value


@pytest.mark.asyncio
async def test_car_hardware_obstacle_detection():
    """Test CarHardware obstacle detection."""
    mock_api = MockCarAPIClient()
    # Set distance that will trigger obstacle detection
    mock_api.distance_reading = 20.0

    hardware = CarHardware(api_client=mock_api)

    # Test with default threshold (30cm)
    is_obstacle = await hardware.is_obstacle_detected()
    assert is_obstacle is True  # 20 < 30

    # Test with custom threshold
    is_obstacle = await hardware.is_obstacle_detected(threshold_cm=15.0)
    assert is_obstacle is False  # 20 > 15


@pytest.mark.asyncio
async def test_car_hardware_failed_obstacle_detection():
    """Test CarHardware obstacle detection with failure."""
    mock_api = Mock()
    mock_api.get_sensor_data = AsyncMock(
        return_value=CarResponse(success=False, error="Sensor error")
    )

    hardware = CarHardware(api_client=mock_api)

    is_obstacle = await hardware.is_obstacle_detected()
    assert is_obstacle is False  # Fallback value


@pytest.mark.asyncio
async def test_car_hardware_black_detection():
    """Test CarHardware black surface detection."""
    mock_api = MockCarAPIClient()
    mock_api.black_detected = True

    hardware = CarHardware(api_client=mock_api)

    is_black = await hardware.is_black_detected()
    assert is_black is True


@pytest.mark.asyncio
async def test_car_hardware_failed_black_detection():
    """Test CarHardware black detection with failure."""
    mock_api = Mock()
    mock_api.get_ir_data = AsyncMock(
        return_value=CarResponse(success=False, error="IR sensor error")
    )

    hardware = CarHardware(api_client=mock_api)

    is_black = await hardware.is_black_detected()
    assert is_black is False  # Fallback value


@pytest.mark.asyncio
async def test_car_hardware_api_client_exception():
    """Test CarHardware handling API client exceptions."""
    mock_api = Mock()
    mock_api.move = AsyncMock(side_effect=Exception("Connection lost"))

    hardware = CarHardware(api_client=mock_api)

    success = await hardware.move_distance(10.0)
    assert success is False


@pytest.mark.asyncio
async def test_car_hardware_invalid_sensor_response():
    """Test CarHardware handling invalid sensor responses."""
    mock_api = Mock()
    # Return non-numeric value for distance
    mock_api.get_sensor_data = AsyncMock(
        return_value=CarResponse(success=True, result="invalid")
    )

    hardware = CarHardware(api_client=mock_api)

    distance = await hardware.get_distance_cm()
    assert distance == 999.0  # Fallback for invalid response

    # Return non-boolean value for obstacle
    mock_api.get_sensor_data = AsyncMock(
        return_value=CarResponse(success=True, result="maybe")
    )
    is_obstacle = await hardware.is_obstacle_detected()
    assert is_obstacle is False  # Fallback for invalid response


@pytest.mark.asyncio
async def test_car_hardware_default_api_client_creation():
    """Test CarHardware creates default API client when none provided."""
    # Test with default config values since patching Pydantic config is complex
    hardware = CarHardware()

    # Should have created an API client with default config values
    assert hardware.api_client is not None
    assert hardware.api_client.base_url == "http://192.168.1.100"
    assert hardware.api_client.timeout == 15.0
