"""Integration tests for hardware interface with engine commands."""

import pytest

from ..workflow import engine_workflow
from ..hardware import MockHardware
from ..executor import Executor
from ..commands import CommandRegistry
from ..types import GridPosition


@pytest.mark.asyncio
async def test_engine_workflow_with_mock_hardware():
    """Test complete engine workflow using mock hardware."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Simple movement grid
    grid = [
        ["MOVE", "10", ""],
        ["TURN", "RIGHT", ""],
        ["MOVE", "5", ""],
    ]

    # Execute with mock hardware
    result = await engine_workflow(
        capture_messages,
        grid,
        use_hardware=False,  # Use mock hardware
    )

    assert result["success"] is True
    assert result["final_state"]["position"]["x"] == 5  # Moved right after turn
    assert result["final_state"]["position"]["y"] == 10  # Initial forward move


@pytest.mark.asyncio
async def test_hardware_integration_movement_tracking():
    """Test that hardware interface tracks actual movements."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Create mock hardware
    hardware = MockHardware()
    executor = Executor(capture_messages, hardware=hardware)

    # Execute movement commands
    commands = [
        CommandRegistry.create_command("MOVE", ["15"], GridPosition(0, 0)),
        CommandRegistry.create_command("TURN", ["LEFT"], GridPosition(1, 0)),
        CommandRegistry.create_command("MOVE", ["8"], GridPosition(2, 0)),
    ]

    # Filter out None commands
    valid_commands = [cmd for cmd in commands if cmd is not None]

    await executor.execute(valid_commands)

    # Check hardware movements (distances directly in cm)
    assert hardware.total_distance_moved == 23.0  # (15 + 8) cm
    assert len(hardware.movement_history) == 2
    assert hardware.movement_history[0] == 15.0  # 15cm
    assert hardware.movement_history[1] == 8.0  # 8cm
