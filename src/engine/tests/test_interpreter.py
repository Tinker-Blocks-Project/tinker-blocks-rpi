"""Tests for the engine interpreter."""

import pytest
from engine import Interpreter, ExecutionState, CommandRegistry
from engine.commands import MoveForwardCommand, TurnRightCommand, TurnLeftCommand


def test_command_registry():
    """Test command registry functionality."""
    registry = CommandRegistry()

    # Test command lookup
    assert registry.get("MOVE_FORWARD") is not None
    assert registry.get("FORWARD") is not None
    assert registry.get("FWD") is not None
    assert registry.get("TURN_RIGHT") is not None
    assert registry.get("RIGHT") is not None
    assert registry.get("TURN_LEFT") is not None
    assert registry.get("LEFT") is not None

    # Test case insensitivity
    assert registry.get("forward") is not None
    assert registry.get("FORWARD") is not None

    # Test unknown command
    assert registry.get("UNKNOWN") is None


def test_execution_state():
    """Test execution state management."""
    state = ExecutionState()

    # Initial state
    assert state.position.x == 0
    assert state.position.y == 0
    assert state.direction == "right"
    assert state.steps_executed == 0

    # Test movement
    state.move(1, 0)
    assert state.position.x == 1
    assert state.position.y == 0

    state.move(0, 1)
    assert state.position.x == 1
    assert state.position.y == 1

    # Test step recording
    state.record_step("FORWARD")
    assert state.steps_executed == 1
    assert len(state.output) == 1
    assert state.output[0].command == "FORWARD"


def test_move_forward_command():
    """Test move forward command execution."""
    state = ExecutionState()
    cmd = MoveForwardCommand()

    # Move right
    state.direction = "right"
    cmd.execute(state)
    assert state.position.x == 1
    assert state.position.y == 0

    # Move down
    state.direction = "down"
    cmd.execute(state)
    assert state.position.x == 1
    assert state.position.y == 1

    # Move left
    state.direction = "left"
    cmd.execute(state)
    assert state.position.x == 0
    assert state.position.y == 1

    # Move up
    state.direction = "up"
    cmd.execute(state)
    assert state.position.x == 0
    assert state.position.y == 0


def test_turn_commands():
    """Test turn right and left commands."""
    state = ExecutionState()
    turn_right = TurnRightCommand()
    turn_left = TurnLeftCommand()

    # Test turn right
    state.direction = "right"
    turn_right.execute(state)
    assert state.direction == "down"

    turn_right.execute(state)
    assert state.direction == "left"

    turn_right.execute(state)
    assert state.direction == "up"

    turn_right.execute(state)
    assert state.direction == "right"

    # Test turn left
    turn_left.execute(state)
    assert state.direction == "up"

    turn_left.execute(state)
    assert state.direction == "left"

    turn_left.execute(state)
    assert state.direction == "down"

    turn_left.execute(state)
    assert state.direction == "right"


@pytest.mark.asyncio
async def test_interpreter_basic_execution():
    """Test interpreter basic execution."""
    interpreter = Interpreter()

    grid = [
        ["FORWARD", "RIGHT", "FORWARD"],
        ["LEFT", "FORWARD", ""],
        ["", "FORWARD", ""],
    ]

    commands_executed = []

    async def on_command(row, col, cmd):
        commands_executed.append((row, col, cmd))

    state = await interpreter.execute_grid(grid, on_command=on_command)

    # Check final state
    # Commands: FORWARD (1,0), RIGHT (facing down), FORWARD (1,1),
    # LEFT (facing right), FORWARD (2,1), FORWARD (3,1)
    assert state.position.x == 3
    assert state.position.y == 1
    assert state.direction == "right"
    assert state.steps_executed == 6

    # Check commands were called
    assert len(commands_executed) == 6
    assert commands_executed[0] == (0, 0, "FORWARD")
    assert commands_executed[1] == (0, 1, "RIGHT")


@pytest.mark.asyncio
async def test_interpreter_cancellation():
    """Test interpreter cancellation."""
    interpreter = Interpreter()

    grid = [["FORWARD", "FORWARD", "FORWARD"], ["FORWARD", "FORWARD", "FORWARD"]]

    commands_executed = []

    async def on_command(row, col, cmd):
        commands_executed.append((row, col, cmd))
        # Cancel after 2 commands
        if len(commands_executed) >= 2:
            interpreter.cancel()

    await interpreter.execute_grid(grid, on_command=on_command)

    # Should have executed only 2 commands before cancellation
    assert len(commands_executed) == 2
    assert interpreter.is_cancelled


@pytest.mark.asyncio
async def test_interpreter_unknown_commands():
    """Test interpreter handling of unknown commands."""
    interpreter = Interpreter()

    grid = [["FORWARD", "UNKNOWN", "RIGHT"], ["INVALID", "LEFT", ""]]

    unknown_commands = []

    async def on_unknown(cmd):
        unknown_commands.append(cmd)

    state = await interpreter.execute_grid(grid, on_unknown_command=on_unknown)

    # Should have recorded unknown commands
    assert len(unknown_commands) == 2
    assert "UNKNOWN" in unknown_commands
    assert "INVALID" in unknown_commands

    # Should have executed valid commands
    assert state.steps_executed == 3  # FORWARD, RIGHT, LEFT
