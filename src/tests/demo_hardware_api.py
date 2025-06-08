#!/usr/bin/env python3
"""Demo script showing hardware API integration with the engine.

This script demonstrates:
1. Running engine commands with mock hardware
2. Running engine commands with real hardware API
3. Tracking actual movements vs. logical position
4. Error handling for hardware failures
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import engine_workflow, MockHardware, CarHardware
from core import MockCarAPIClient, config


async def demo_mock_hardware():
    """Demonstrate engine execution with mock hardware."""
    print("🤖 Demo: Mock Hardware Integration")
    print("=" * 50)

    messages = []

    async def capture_messages(msg):
        messages.append(msg)
        print(f"  {msg}")

    # Define a simple program
    grid = [
        ["SET", "SIDE", "3"],
        ["PEN_DOWN", "", ""],
        ["LOOP", "4", ""],
        ["", "MOVE", "SIDE"],
        ["", "TURN", "RIGHT"],
        ["PEN_UP", "", ""],
    ]

    print("\n📝 Program: Draw a square with side length 3")
    print("Grid commands:")
    for i, row in enumerate(grid):
        row_str = " | ".join(cell if cell else "___" for cell in row)
        print(f"  Row {i}: {row_str}")

    print("\n⚡ Executing with mock hardware...")
    result = await engine_workflow(
        send_message=capture_messages,
        check_cancelled=lambda: False,
        grid_data=grid,
        use_hardware=False,  # Mock hardware
    )

    print(f"\n✅ Execution result:")
    print(f"  Success: {result['success']}")
    print(f"  Steps executed: {result['final_state']['steps_executed']}")
    print(
        f"  Final position: ({result['final_state']['position']['x']}, {result['final_state']['position']['y']})"
    )
    print(f"  Final direction: {result['final_state']['direction']}")
    print(f"  Path points: {len(result['final_state']['path'])}")


async def demo_hardware_tracking():
    """Demonstrate hardware movement tracking."""
    print("\n\n🔧 Demo: Hardware Movement Tracking")
    print("=" * 50)

    messages = []

    async def capture_messages(msg):
        messages.append(msg)
        if not msg.startswith("Executing") and not msg.startswith("✅"):
            print(f"  {msg}")

    # Create mock hardware to track movements
    hardware = MockHardware()

    # Define movement program
    grid = [
        ["MOVE", "10", ""],  # Move 10 units forward (100cm)
        ["TURN", "RIGHT", ""],  # Turn 90° right
        ["MOVE", "5", ""],  # Move 5 units forward (50cm)
        ["TURN", "LEFT", "45"],  # Turn 45° left
        ["MOVE", "3", ""],  # Move 3 units forward (30cm)
    ]

    print("\n📝 Program: Complex movement sequence")
    print("Expected real-world movements:")
    print("  - Move 100cm forward")
    print("  - Turn 90° right")
    print("  - Move 50cm forward")
    print("  - Turn 45° left")
    print("  - Move 30cm forward")

    # Create a custom executor to get access to hardware
    from engine import Executor

    executor = Executor(capture_messages, lambda: False, hardware=hardware)

    # Parse commands manually to access hardware
    from engine import GridParser

    parser = GridParser(grid)
    commands = parser.parse()

    print("\n⚡ Executing movement sequence...")
    context = await executor.execute(commands)

    print(f"\n📊 Hardware Movement Tracking:")
    print(f"  Total distance moved: {hardware.total_distance_moved}cm")
    print(f"  Total degrees rotated: {hardware.total_degrees_rotated}°")
    print(f"  Movement history: {hardware.movement_history}")
    print(f"  Rotation history: {hardware.rotation_history}")

    print(f"\n📍 Logical Position Tracking:")
    print(f"  Final position: ({context.position.x}, {context.position.y})")
    print(f"  Final direction: {context.direction.value}")
    print(f"  Steps executed: {context.steps_executed}")


async def demo_sensor_integration():
    """Demonstrate sensor integration with hardware."""
    print("\n\n📡 Demo: Sensor Integration")
    print("=" * 50)

    messages = []

    async def capture_messages(msg):
        messages.append(msg)
        if "Hardware" not in msg and "Executing" not in msg:
            print(f"  {msg}")

    # Create mock hardware with specific sensor values
    hardware = MockHardware()
    hardware.distance_reading = 25.0  # Close obstacle
    hardware.black_detected = True  # On black line

    # Program that uses sensors
    grid = [
        ["LOOP", "TRUE", ""],
        ["", "IF", "OBSTACLE"],
        ["", "", "TURN", "RIGHT"],
        ["", "", "MOVE", "2"],
        ["", "ELSE", ""],
        ["", "", "IF", "BLACK_DETECTED"],
        ["", "", "", "MOVE", "1"],
        ["", "", "ELSE", ""],
        ["", "", "", "TURN", "LEFT"],
    ]

    print("\n📝 Program: Obstacle avoidance with line following")
    print("Sensor conditions:")
    print(f"  - Distance reading: {hardware.distance_reading}cm")
    print(f"  - Black line detected: {hardware.black_detected}")
    print(f"  - Obstacle threshold: 30cm")

    # Create executor with limited steps to prevent infinite loop
    from engine import Executor, ExecutionContext

    executor = Executor(capture_messages, lambda: False, hardware=hardware)

    # Parse and execute with step limit
    from engine import GridParser

    parser = GridParser(grid)
    commands = parser.parse()

    print("\n⚡ Executing sensor-based program (limited to 10 steps)...")
    context = ExecutionContext()
    context.hardware = hardware
    context.max_steps = 10  # Limit steps to prevent infinite loop
    context.send_message = capture_messages
    context.check_cancelled = lambda: False

    try:
        for i, command in enumerate(commands):
            if context.steps_executed >= context.max_steps:
                break
            await command.execute(context)
    except RuntimeError as e:
        print(f"  ⚠️ {e}")

    print(f"\n📊 Execution Results:")
    print(f"  Steps executed: {context.steps_executed}")
    print(f"  Final position: ({context.position.x}, {context.position.y})")
    print(f"  Hardware movements: {len(hardware.movement_history)}")
    print(f"  Hardware rotations: {len(hardware.rotation_history)}")


async def demo_real_hardware_api():
    """Demonstrate real hardware API configuration."""
    print("\n\n🔗 Demo: Real Hardware API Configuration")
    print("=" * 50)

    print(f"🔧 Current car API configuration:")
    print(f"  API URL: {config.car_api_url}")
    print(f"  Timeout: {config.car_api_timeout}s")

    print(f"\n📡 To use real hardware, set these environment variables:")
    print(f"  export CAR_API_URL='http://192.168.1.100'")
    print(f"  export CAR_API_TIMEOUT=10.0")

    print(f"\n💻 Example WebSocket commands for real hardware:")
    print(f"  # Run with real hardware")
    commands = [
        '{"command": "run", "params": {"workflow": "engine", "use_hardware": true, "grid": [["MOVE", "10"], ["TURN", "RIGHT"]]}}',
        '{"command": "run", "params": {"workflow": "full", "use_hardware": true}}',
        '{"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true, "use_hardware": true}}',
    ]

    for cmd in commands:
        print(f"  {cmd}")

    # Show API client creation
    print(f"\n🛠️ Hardware API client example:")
    print(f"  from core import CarAPIClient")
    print(f"  from engine import CarHardware")
    print(f"  ")
    print(f"  # Create API client")
    print(
        f"  api_client = CarAPIClient('{config.car_api_url}', timeout={config.car_api_timeout})"
    )
    print(f"  ")
    print(f"  # Create hardware interface")
    print(f"  hardware = CarHardware(api_client)")
    print(f"  ")
    print(f"  # Use with executor")
    print(f"  executor = Executor(send_message, check_cancelled, hardware=hardware)")


async def demo_error_handling():
    """Demonstrate hardware error handling."""
    print("\n\n⚠️ Demo: Hardware Error Handling")
    print("=" * 50)

    messages = []

    async def capture_messages(msg):
        messages.append(msg)
        print(f"  {msg}")

    # Create a failing mock API client
    from core import CarResponse

    class FailingMockAPI:
        async def move(self, **kwargs):
            return CarResponse(success=False, error="Motor controller offline")

        async def rotate(self, **kwargs):
            return CarResponse(success=False, error="Gyroscope calibration failed")

        async def pen_control(self, **kwargs):
            return CarResponse(success=False, error="Servo mechanism jammed")

        async def get_sensor_data(self, **kwargs):
            return CarResponse(success=False, error="Ultrasonic sensor disconnected")

        async def get_ir_data(self, **kwargs):
            return CarResponse(success=False, error="IR sensor malfunction")

    # Create hardware with failing API
    from engine import CarHardware

    failing_api = FailingMockAPI()
    failing_hardware = CarHardware(api_client=failing_api)  # type: ignore

    # Test program
    grid = [
        ["PEN_DOWN", "", ""],
        ["MOVE", "5", ""],
        ["TURN", "RIGHT", ""],
        ["PEN_UP", "", ""],
    ]

    print("\n📝 Program: Simple drawing with failing hardware")
    print("Expected errors:")
    print("  - Pen control failures")
    print("  - Movement failures")
    print("  - Rotation failures")

    # Create executor with failing hardware
    from engine import Executor

    executor = Executor(capture_messages, lambda: False, hardware=failing_hardware)

    # Parse and execute
    from engine import GridParser

    parser = GridParser(grid)
    commands = parser.parse()

    print("\n⚡ Executing with failing hardware...")
    context = await executor.execute(commands)

    print("\n📊 Results despite hardware failures:")
    print(f"  Execution completed: {context.steps_executed > 0}")
    print(f"  Steps executed: {context.steps_executed}")
    print(
        f"  Position tracking still works: ({context.position.x}, {context.position.y})"
    )
    print(f"  Error messages received: {len([m for m in messages if 'failed' in m])}")


async def main():
    """Run all hardware API demos."""
    print("🚀 TinkerBlocks Hardware API Integration Demo")
    print("=" * 60)

    try:
        await demo_mock_hardware()
        await demo_hardware_tracking()
        await demo_sensor_integration()
        await demo_real_hardware_api()
        await demo_error_handling()

        print("\n\n🎉 All demos completed successfully!")
        print("\nNext steps:")
        print("  1. Configure your car's IP address in config")
        print("  2. Test with real hardware using WebSocket commands")
        print("  3. Monitor API responses for debugging")
        print("  4. Use mock hardware for development and testing")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
