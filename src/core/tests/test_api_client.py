"""Tests for the CarAPIClient and MockCarAPIClient."""

import pytest

from ..api_client import CarAPIClient, MockCarAPIClient, CarResponse


@pytest.mark.asyncio
async def test_mock_car_api_client_move():
    """Test mock car API client move functionality."""
    mock_client = MockCarAPIClient()

    # Test forward movement
    response = await mock_client.move(speed=100, distance=20.0)
    assert response.success is True
    assert response.result["distance_traveled"] == 20.0
    assert response.result["time_taken"] == 2000  # 20 * 100
    assert response.result["final_yaw"] == 0.0

    # Test backward movement
    response = await mock_client.move(speed=-80, distance=15.0)
    assert response.success is True
    assert response.result["distance_traveled"] == 15.0


@pytest.mark.asyncio
async def test_mock_car_api_client_rotate():
    """Test mock car API client rotation functionality."""
    mock_client = MockCarAPIClient()

    # Test right rotation
    response = await mock_client.rotate(angle=90.0, speed=100)
    assert response.success is True
    assert response.result["angle_turned"] == 90.0
    assert response.result["time_ms"] == 900  # 90 * 10
    assert response.result["direction_changes"] == 0

    # Test left rotation
    response = await mock_client.rotate(angle=-45.0, speed=80)
    assert response.success is True
    assert response.result["angle_turned"] == -45.0
    assert response.result["time_ms"] == 450  # 45 * 10


@pytest.mark.asyncio
async def test_mock_car_api_client_pen_control():
    """Test mock car API client pen control."""
    mock_client = MockCarAPIClient()

    # Test pen down
    response = await mock_client.pen_control(action="down")
    assert response.success is True
    assert response.result == "Pen down"
    assert mock_client.pen_position == "down"

    # Test pen up
    response = await mock_client.pen_control(action="up")
    assert response.success is True
    assert response.result == "Pen up"
    assert mock_client.pen_position == "up"

    # Test pen position
    response = await mock_client.pen_control(action="position", position=128)
    assert response.success is True
    assert response.result == "Pen position"
    assert mock_client.pen_position == "position"


@pytest.mark.asyncio
async def test_mock_car_api_client_sensors():
    """Test mock car API client sensor functionality."""
    mock_client = MockCarAPIClient()

    # Test distance sensor
    response = await mock_client.get_sensor_data(action="distance")
    assert response.success is True
    assert response.result == 50.0  # Default mock distance

    # Test obstacle detection with default threshold
    response = await mock_client.get_sensor_data(action="obstacle")
    assert response.success is True
    assert response.result is False  # 50 > 30 (default threshold)

    # Test obstacle detection with custom threshold
    response = await mock_client.get_sensor_data(action="obstacle", threshold=60.0)
    assert response.success is True
    assert response.result is True  # 50 < 60

    # Test IR sensor (now returns "0"/"1" strings like real ESP32)
    response = await mock_client.get_ir_data()
    assert response.success is True
    assert response.result == "0"  # Default mock value (string "0")

    # Change mock IR value
    mock_client.black_detected = True
    response = await mock_client.get_ir_data()
    assert response.success is True
    assert response.result == "1"  # Black detected (string "1")


@pytest.mark.asyncio
async def test_mock_car_api_client_gyro():
    """Test mock car API client gyroscope functionality."""
    mock_client = MockCarAPIClient()

    # Test gyro data
    response = await mock_client.get_gyro_data(action="data")
    assert response.success is True
    assert isinstance(response.result, dict)
    assert "accelX" in response.result
    assert "yaw" in response.result

    # Test gyro calibration
    response = await mock_client.calibrate_gyro()
    assert response.success is True
    assert response.result == "Gyro calibrated"


@pytest.mark.asyncio
async def test_mock_car_api_client_unknown_endpoint():
    """Test mock car API client with unknown endpoint."""
    mock_client = MockCarAPIClient()

    # Call _post directly with unknown endpoint
    response = await mock_client._post("/api/unknown", {"test": "data"})
    assert response.success is False
    assert "Unknown endpoint" in response.error


@pytest.mark.asyncio
async def test_car_api_client_timeout_error():
    """Test CarAPIClient timeout handling with unreachable endpoint."""
    # Use a blackhole IP that will cause timeout (should be handled gracefully)
    client = CarAPIClient(base_url="http://10.255.255.1", timeout=0.1)
    response = await client.move(speed=100, distance=10.0)

    assert response.success is False
    # Should get timeout or connection error
    assert "timeout" in response.error.lower() or "connection" in response.error.lower()


@pytest.mark.asyncio
async def test_car_api_client_request_error():
    """Test CarAPIClient request error handling with invalid URL."""
    # Use an invalid URL that will cause connection error
    client = CarAPIClient(
        base_url="http://invalid-hostname-that-does-not-exist.local", timeout=0.1
    )
    response = await client.rotate(angle=90.0)

    assert response.success is False
    # Should get some kind of connection error or timeout
    assert "error" in response.error.lower() or "timeout" in response.error.lower()


@pytest.mark.asyncio
async def test_car_api_client_initialization():
    """Test CarAPIClient initialization and basic properties."""
    # Test default initialization
    client = CarAPIClient()
    assert client.base_url == "http://192.168.1.100"
    assert client.timeout == 10.0

    # Test custom initialization
    client = CarAPIClient(base_url="http://custom.com", timeout=5.0)
    assert client.base_url == "http://custom.com"
    assert client.timeout == 5.0

    # Test URL trimming
    client = CarAPIClient(base_url="http://test.com/")
    assert client.base_url == "http://test.com"


@pytest.mark.asyncio
async def test_mock_vs_real_api_client_compatibility():
    """Test that MockCarAPIClient and CarAPIClient have compatible interfaces."""
    # Test that both have the same methods
    mock_client = MockCarAPIClient()
    real_client = CarAPIClient()

    # Check method existence
    assert hasattr(mock_client, "move")
    assert hasattr(real_client, "move")
    assert hasattr(mock_client, "rotate")
    assert hasattr(real_client, "rotate")
    assert hasattr(mock_client, "pen_control")
    assert hasattr(real_client, "pen_control")
    assert hasattr(mock_client, "get_sensor_data")
    assert hasattr(real_client, "get_sensor_data")

    # Test that mock client works correctly (already tested above, but good to have here)
    response = await mock_client.move(speed=100, distance=10.0)
    assert response.success is True
    assert response.result["distance_traveled"] == 10.0


@pytest.mark.asyncio
async def test_data_type_conversion_in_mock():
    """Test that mock client handles type conversion properly."""
    mock_client = MockCarAPIClient()

    # Test with string values that should be converted to numbers
    response = await mock_client._post(
        "/api/move", {"distance": "15.5", "speed": "100"}
    )
    assert response.success is True
    assert response.result["distance_traveled"] == 15.5

    # Test with non-numeric values
    response = await mock_client._post("/api/move", {"distance": "invalid"})
    assert response.success is True
    assert response.result["distance_traveled"] == 1.0  # fallback

    # Test obstacle detection with string threshold
    response = await mock_client._post(
        "/api/sensor", {"action": "obstacle", "threshold": "40.0"}
    )
    assert response.success is True
    assert response.result is False  # 50 > 40


@pytest.mark.asyncio
async def test_car_response_dataclass():
    """Test CarResponse dataclass functionality."""
    # Test with default values
    response = CarResponse(success=True)
    assert response.success is True
    assert response.result is None
    assert response.error == ""

    # Test with all values
    response = CarResponse(success=False, result={"test": "data"}, error="Test error")
    assert response.success is False
    assert response.result == {"test": "data"}
    assert response.error == "Test error"
