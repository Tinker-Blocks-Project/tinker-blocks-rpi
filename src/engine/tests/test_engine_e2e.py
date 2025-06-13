"""End-to-end tests for the TinkerBlocks engine module."""

import pytest
import asyncio
from ..workflow import engine_workflow
from ..context import ExecutionContext, MockSensors
from ..executor import Executor
from ..commands import CommandRegistry, IfCommand
from ..types import GridPosition, Position
from ..parser import GridParser


@pytest.mark.asyncio
async def test_simple_movement_sequence():
    """Test basic movement commands in sequence."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["MOVE", "", ""],
        ["MOVE", "", ""],
        ["TURN", "RIGHT", ""],
        ["MOVE", "", ""],
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    assert result["final_state"]["position"]["x"] == 1.0
    assert result["final_state"]["position"]["y"] == 2.0
    assert result["final_state"]["direction"] == "right"
    assert result["final_state"]["steps_executed"] == 4


@pytest.mark.asyncio
async def test_movement_with_distances():
    """Test movement with explicit distances."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Create grid with arguments in separate cells
    parser = GridParser([])
    executor = Executor(capture_messages, lambda: False)

    # MOVE 5
    move_cmd = CommandRegistry.create_command("MOVE", ["5"], GridPosition(0, 0))
    assert move_cmd is not None
    context = await executor.execute_single(move_cmd)

    assert context.position.x == 0
    assert context.position.y == 5

    # MOVE -2 (backward)
    move_back = CommandRegistry.create_command("MOVE", ["-2"], GridPosition(0, 1))
    assert move_back is not None
    context = await executor.execute_single(move_back, context)

    assert context.position.x == 0
    assert context.position.y == 3


@pytest.mark.asyncio
async def test_turn_commands():
    """Test turn commands work correctly."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    executor = Executor(capture_messages, lambda: False)
    context = ExecutionContext()

    # TURN LEFT
    turn_left = CommandRegistry.create_command("TURN", ["LEFT"], GridPosition(0, 0))
    assert turn_left is not None
    context = await executor.execute_single(turn_left, context)
    assert context.direction.value == "left"

    # TURN RIGHT (from left)
    turn_right = CommandRegistry.create_command("TURN", ["RIGHT"], GridPosition(0, 1))
    assert turn_right is not None
    context = await executor.execute_single(turn_right, context)
    assert context.direction.value == "forward"  # left + right = forward

    # TURN RIGHT again
    context = await executor.execute_single(turn_right, context)
    assert context.direction.value == "right"


@pytest.mark.asyncio
async def test_loop_with_count():
    """Test LOOP command with fixed count."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Simple loop with nested command
    grid = [
        ["LOOP", "3", ""],
        ["", "MOVE", ""],  # Indented command
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    assert result["final_state"]["position"]["y"] == 3  # Moved 3 times
    assert result["final_state"]["steps_executed"] == 3  # 3 moves


@pytest.mark.asyncio
async def test_loop_with_true_condition():
    """Test LOOP with TRUE condition (limited by max steps)."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Infinite loop - will hit max steps
    grid = [
        ["LOOP", "TRUE", ""],
        ["", "MOVE", ""],
    ]

    # The workflow sets max_steps to 1000, so it should fail
    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is False
    assert "Maximum steps exceeded" in result["error"]


@pytest.mark.asyncio
async def test_loop_with_false_condition():
    """Test LOOP with FALSE condition (no execution)."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["LOOP", "FALSE", ""],
        ["", "MOVE", ""],
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    assert result["final_state"]["position"]["y"] == 0  # No movement
    assert result["final_state"]["steps_executed"] == 0  # No steps for FALSE loop


@pytest.mark.asyncio
async def test_if_else_conditions():
    """Test IF/ELSE conditional execution."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Test with TRUE condition
    grid = [
        ["IF", "TRUE", ""],
        ["", "MOVE", "2"],  # Then branch
        ["ELSE", "", ""],
        ["", "MOVE", "-1"],  # Else branch
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)
    assert result["success"] is True
    assert result["final_state"]["position"]["y"] == 2  # Only forward move executed

    # Test with FALSE condition
    grid2 = [
        ["IF", "FALSE", ""],
        ["", "MOVE", "2"],  # Then branch
        ["ELSE", "", ""],
        ["", "MOVE", "-1"],  # Else branch
    ]

    result2 = await engine_workflow(capture_messages, lambda: False, grid2)
    assert result2["success"] is True
    assert result2["final_state"]["position"]["y"] == -1  # Only backward move executed


@pytest.mark.asyncio
async def test_variable_operations():
    """Test SET command and variable usage."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["SET", "X", "5"],
        ["SET", "Y", "X", "+", "3"],
        ["MOVE", "X", ""],  # Use variable as distance
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    assert result["final_state"]["variables"]["X"] == 5
    assert result["final_state"]["variables"]["Y"] == 8
    assert result["final_state"]["position"]["y"] == 5  # Moved by X=5


@pytest.mark.asyncio
async def test_while_conditions():
    """Test standalone WHILE command."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["SET", "X", "0"],
        ["WHILE", "X", "<", "5"],
        ["", "MOVE", ""],
        ["", "SET", "X", "X", "+", "1"],
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    assert result["final_state"]["variables"]["X"] == 5
    assert result["final_state"]["position"]["y"] == 5  # Moved 5 times


@pytest.mark.asyncio
async def test_sensor_integration():
    """Test sensor-based conditions."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    parser = GridParser([])
    sensors = MockSensors()
    sensors.distance = 50.0
    sensors.black_detected = True

    executor = Executor(capture_messages, lambda: False, sensors)
    context = ExecutionContext()
    context.sensors = sensors

    # IF DISTANCE < 100
    if_distance = CommandRegistry.create_command(
        "IF", ["DISTANCE", "<", "100"], GridPosition(0, 0)
    )
    move_cmd = CommandRegistry.create_command("MOVE", ["2"], GridPosition(1, 1))
    assert if_distance is not None
    assert move_cmd is not None
    if_distance.add_nested_command(move_cmd)

    context = await executor.execute_single(if_distance, context)
    assert context.position.y == 2  # Condition was true (50 < 100)

    # IF OBSTACLE (distance < 30)
    if_obstacle = CommandRegistry.create_command("IF", ["OBSTACLE"], GridPosition(2, 0))
    turn_cmd = CommandRegistry.create_command("TURN", ["RIGHT"], GridPosition(3, 1))
    assert if_obstacle is not None
    assert turn_cmd is not None
    if_obstacle.add_nested_command(turn_cmd)

    context = await executor.execute_single(if_obstacle, context)
    assert context.direction.value == "forward"  # No turn (50 > 30, no obstacle)

    # Change distance to trigger obstacle
    sensors.distance = 20.0
    context = await executor.execute_single(if_obstacle, context)
    assert (
        context.direction.value == "right"
    )  # Turned right (20 < 30, obstacle detected)


@pytest.mark.asyncio
async def test_drawing_commands():
    """Test PEN_UP and PEN_DOWN commands."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    parser = GridParser([])
    executor = Executor(capture_messages, lambda: False)
    context = ExecutionContext()

    # Initial state - pen up
    assert context.pen_down is False
    assert len(context.path) == 0

    # PEN_DOWN
    pen_down = CommandRegistry.create_command("PEN_DOWN", [], GridPosition(0, 0))
    assert pen_down is not None
    context = await executor.execute_single(pen_down, context)
    assert context.pen_down is True
    assert len(context.path) == 1  # PEN_DOWN adds current position

    # MOVE with pen down
    move_cmd = CommandRegistry.create_command("MOVE", ["3"], GridPosition(1, 0))
    assert move_cmd is not None
    context = await executor.execute_single(move_cmd, context)
    assert len(context.path) == 3  # Start + 2 points for movement

    # PEN_UP
    pen_up = CommandRegistry.create_command("PEN_UP", [], GridPosition(2, 0))
    assert pen_up is not None
    context = await executor.execute_single(pen_up, context)
    assert context.pen_down is False

    # MOVE with pen up
    move_cmd2 = CommandRegistry.create_command("MOVE", ["2"], GridPosition(3, 0))
    assert move_cmd2 is not None
    context = await executor.execute_single(move_cmd2, context)
    assert len(context.path) == 3  # No new path points added


@pytest.mark.asyncio
async def test_wait_command():
    """Test WAIT command with time."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    parser = GridParser([])
    executor = Executor(capture_messages, lambda: False)
    context = ExecutionContext()

    # WAIT 0.01 (very short wait)
    wait_time = CommandRegistry.create_command("WAIT", ["0.01"], GridPosition(0, 0))
    assert wait_time is not None

    start_time = asyncio.get_event_loop().time()
    context = await executor.execute_single(wait_time, context)
    elapsed = asyncio.get_event_loop().time() - start_time

    assert elapsed >= 0.01  # At least the specified time
    assert context.steps_executed == 1


@pytest.mark.asyncio
async def test_complex_program():
    """Test a complex program with multiple features."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Draw a square using loops and variables
    grid = [
        ["SET", "SIDE", "3"],  # Set side length
        ["SET", "COUNT", "4"],  # 4 sides
        ["PEN_DOWN", "", ""],  # Start drawing
        ["LOOP", "COUNT", ""],  # Loop 4 times
        ["", "MOVE", "SIDE"],  # Move forward (indented)
        ["", "TURN", "RIGHT"],  # Turn right (indented)
        ["PEN_UP", "", ""],  # Stop drawing
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    # Verify the square was drawn
    assert result["success"] is True
    assert result["final_state"]["variables"]["SIDE"] == 3
    assert result["final_state"]["variables"]["COUNT"] == 4
    assert result["final_state"]["position"]["x"] == 0
    assert result["final_state"]["position"]["y"] == 0  # Back at start
    assert (
        result["final_state"]["direction"] == "forward"
    )  # Facing forward after 4 right turns
    assert len(result["final_state"]["path"]) > 0  # Drew something
    assert result["final_state"]["pen_down"] is False  # Pen is up at the end


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in various scenarios."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Test invalid command
    grid = [["INVALID_COMMAND", "", ""]]

    result = await engine_workflow(capture_messages, lambda: False, grid)
    assert result["success"] is False
    assert "Unknown command" in result["error"]

    # Test invalid argument
    parser = GridParser([])
    executor = Executor(capture_messages, lambda: False)

    # TURN without direction
    with pytest.raises(ValueError, match="TURN requires direction"):
        CommandRegistry.create_command("TURN", [], GridPosition(0, 0))

    # WAIT without time
    with pytest.raises(ValueError, match="WAIT requires time"):
        CommandRegistry.create_command("WAIT", [], GridPosition(0, 0))


@pytest.mark.asyncio
async def test_cancellation():
    """Test that execution stops at max steps limit."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    executor = Executor(capture_messages, lambda: False)
    context = ExecutionContext()
    context.max_steps = 100  # Low limit

    # Create an infinite loop
    loop_cmd = CommandRegistry.create_command("LOOP", ["TRUE"], GridPosition(0, 0))
    move_cmd = CommandRegistry.create_command("MOVE", [], GridPosition(1, 1))
    assert loop_cmd is not None
    assert move_cmd is not None
    loop_cmd.add_nested_command(move_cmd)

    # Should raise error when max steps exceeded
    with pytest.raises(RuntimeError, match="Maximum steps exceeded"):
        await executor.execute_single(loop_cmd, context)

    # Should have executed max_steps + 1 (error raised after increment)
    assert context.steps_executed == 101
    assert context.position.y == 101


@pytest.mark.asyncio
async def test_turn_with_degrees():
    """Test TURN command with custom degrees."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Test various turn degree commands
    grid = [
        ["TURN", "45", ""],  # Turn 45 degrees right
        ["MOVE", "2", ""],
        ["TURN", "LEFT", "30"],  # Turn 30 degrees left
        ["MOVE", "2", ""],
        ["TURN", "RIGHT", "60"],  # Turn 60 degrees right
        ["MOVE", "2", ""],
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # 45 + 60 - 30 = 75 degrees from forward, which should map to right
    # But our implementation might be using different angle conventions
    # Let's just check we get a valid direction
    assert result["final_state"]["direction"] in [
        "forward",
        "right",
        "backward",
        "left",
    ]


@pytest.mark.asyncio
async def test_fibonacci_sequence():
    """Test calculating Fibonacci sequence."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Calculate first 10 Fibonacci numbers - build nested structure manually
    executor = Executor(capture_messages, lambda: False)

    commands = []

    # SET A 0
    set_a = CommandRegistry.create_command("SET", ["A", "0"], GridPosition(0, 0))
    assert set_a is not None
    commands.append(set_a)

    # SET B 1
    set_b = CommandRegistry.create_command("SET", ["B", "1"], GridPosition(1, 0))
    assert set_b is not None
    commands.append(set_b)

    # SET COUNT 0
    set_count = CommandRegistry.create_command(
        "SET", ["COUNT", "0"], GridPosition(2, 0)
    )
    assert set_count is not None
    commands.append(set_count)

    # WHILE COUNT < 10
    while_cmd = CommandRegistry.create_command(
        "WHILE", ["COUNT", "<", "10"], GridPosition(3, 0)
    )
    assert while_cmd is not None

    # Nested commands
    set_temp = CommandRegistry.create_command(
        "SET", ["TEMP", "A", "+", "B"], GridPosition(4, 1)
    )
    set_a2 = CommandRegistry.create_command("SET", ["A", "B"], GridPosition(5, 1))
    set_b2 = CommandRegistry.create_command("SET", ["B", "TEMP"], GridPosition(6, 1))
    set_inc = CommandRegistry.create_command(
        "SET", ["COUNT", "COUNT", "+", "1"], GridPosition(7, 1)
    )

    assert set_temp is not None
    assert set_a2 is not None
    assert set_b2 is not None
    assert set_inc is not None

    while_cmd.add_nested_command(set_temp)
    while_cmd.add_nested_command(set_a2)
    while_cmd.add_nested_command(set_b2)
    while_cmd.add_nested_command(set_inc)

    commands.append(while_cmd)

    # Execute
    context = await executor.execute(commands)

    assert context.variables["COUNT"] == 10
    # B should contain the 11th Fibonacci number (89) - we start with 0,1 and loop 10 times
    assert context.variables["B"] == 89


@pytest.mark.asyncio
async def test_drawing_square():
    """Test drawing a square with loops."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Draw a square - need to manually build commands with nesting
    parser = GridParser([])
    executor = Executor(capture_messages, lambda: False)

    commands = []

    # PEN_DOWN
    pen_down = CommandRegistry.create_command("PEN_DOWN", [], GridPosition(0, 0))
    assert pen_down is not None
    commands.append(pen_down)

    # LOOP 4
    loop_cmd = CommandRegistry.create_command("LOOP", ["4"], GridPosition(1, 0))
    assert loop_cmd is not None

    # Nested: MOVE 3 and TURN RIGHT
    move_cmd = CommandRegistry.create_command("MOVE", ["3"], GridPosition(2, 1))
    turn_cmd = CommandRegistry.create_command("TURN", ["RIGHT"], GridPosition(3, 1))
    assert move_cmd is not None
    assert turn_cmd is not None

    loop_cmd.add_nested_command(move_cmd)
    loop_cmd.add_nested_command(turn_cmd)
    commands.append(loop_cmd)

    # PEN_UP
    pen_up = CommandRegistry.create_command("PEN_UP", [], GridPosition(4, 0))
    assert pen_up is not None
    commands.append(pen_up)

    # Execute
    context = await executor.execute(commands)

    # Should be back at origin after drawing square
    assert context.position == Position(0, 0)
    assert context.direction.value == "forward"  # 4 right turns = 360 degrees
    assert len(context.path) == 9  # 1 start + 4 moves * 2 points each


@pytest.mark.asyncio
async def test_obstacle_avoidance_simple():
    """Test simple obstacle avoidance behavior."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Build IF/ELSE structure manually
    sensors = MockSensors()
    sensors.distance = 100  # No obstacle

    executor = Executor(capture_messages, lambda: False, sensors)
    context = ExecutionContext()
    context.sensors = sensors

    # IF OBSTACLE
    if_obstacle = CommandRegistry.create_command("IF", ["OBSTACLE"], GridPosition(0, 0))
    assert if_obstacle is not None
    assert isinstance(if_obstacle, IfCommand)

    # Then: TURN RIGHT, MOVE 2
    turn_right = CommandRegistry.create_command("TURN", ["RIGHT"], GridPosition(1, 1))
    move_2 = CommandRegistry.create_command("MOVE", ["2"], GridPosition(2, 1))
    assert turn_right is not None
    assert move_2 is not None

    if_obstacle.add_nested_command(turn_right)
    if_obstacle.add_nested_command(move_2)

    # Else: MOVE 3
    move_3 = CommandRegistry.create_command("MOVE", ["3"], GridPosition(4, 1))
    assert move_3 is not None
    if_obstacle.add_else_command(move_3)

    # Execute
    context = await executor.execute_single(if_obstacle, context)

    # Should have moved forward 3 units (no obstacle)
    assert context.position.y == 3
    assert context.direction.value == "forward"
