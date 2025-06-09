"""Test complex nested IF-ELSE structures to ensure parser and execution work correctly."""

import pytest
from ..workflow import engine_workflow
from ..context import ExecutionContext, MockSensors
from ..executor import Executor
from ..commands import CommandRegistry, IfCommand
from ..types import GridPosition
from ..parser import GridParser


@pytest.mark.asyncio
async def test_triple_nested_if_else_all_true():
    """Test 3 nested IF-ELSE with all conditions TRUE."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Outer IF TRUE -> Middle IF TRUE -> Inner IF TRUE
    grid = [
        ["SET", "A", "10"],  # Row 0: A = 10
        ["SET", "B", "5"],  # Row 1: B = 5
        ["SET", "C", "3"],  # Row 2: C = 3
        ["IF", "A", ">", "5"],  # Row 3: Outer IF (10 > 5 = TRUE)
        ["", "MOVE", "1"],  # Row 4:   Move 1 (outer then)
        ["", "IF", "B", ">", "3"],  # Row 5:   Middle IF (5 > 3 = TRUE)
        ["", "", "MOVE", "2"],  # Row 6:     Move 2 (middle then)
        ["", "", "IF", "C", ">", "2"],  # Row 7:     Inner IF (3 > 2 = TRUE)
        ["", "", "", "MOVE", "3"],  # Row 8:       Move 3 (inner then)
        ["", "", "ELSE"],  # Row 9:     Inner ELSE
        ["", "", "", "MOVE", "-3"],  # Row 10:      Move -3 (inner else)
        ["", "ELSE"],  # Row 11:   Middle ELSE
        ["", "", "MOVE", "-2"],  # Row 12:     Move -2 (middle else)
        ["ELSE"],  # Row 13: Outer ELSE
        ["", "MOVE", "-1"],  # Row 14:   Move -1 (outer else)
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Path: Outer TRUE -> Middle TRUE -> Inner TRUE
    # Expected moves: 1 + 2 + 3 = 6
    assert result["final_state"]["position"]["y"] == 6
    assert result["final_state"]["variables"]["A"] == 10
    assert result["final_state"]["variables"]["B"] == 5
    assert result["final_state"]["variables"]["C"] == 3


@pytest.mark.asyncio
async def test_triple_nested_if_else_outer_false():
    """Test 3 nested IF-ELSE with outer condition FALSE."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Outer IF FALSE -> should only execute outer ELSE
    grid = [
        ["SET", "A", "2"],  # Row 0: A = 2
        ["SET", "B", "5"],  # Row 1: B = 5
        ["SET", "C", "3"],  # Row 2: C = 3
        ["IF", "A", ">", "5"],  # Row 3: Outer IF (2 > 5 = FALSE)
        ["", "MOVE", "1"],  # Row 4:   Move 1 (outer then) - NOT EXECUTED
        ["", "IF", "B", ">", "3"],  # Row 5:   Middle IF - NOT EXECUTED
        ["", "", "MOVE", "2"],  # Row 6:     Move 2 - NOT EXECUTED
        ["", "", "IF", "C", ">", "2"],  # Row 7:     Inner IF - NOT EXECUTED
        ["", "", "", "MOVE", "3"],  # Row 8:       Move 3 - NOT EXECUTED
        ["", "", "ELSE"],  # Row 9:     Inner ELSE - NOT EXECUTED
        ["", "", "", "MOVE", "-3"],  # Row 10:      Move -3 - NOT EXECUTED
        ["", "ELSE"],  # Row 11:   Middle ELSE - NOT EXECUTED
        ["", "", "MOVE", "-2"],  # Row 12:     Move -2 - NOT EXECUTED
        ["ELSE"],  # Row 13: Outer ELSE
        ["", "MOVE", "-1"],  # Row 14:   Move -1 (outer else) - EXECUTED
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Path: Outer FALSE -> Outer ELSE only
    # Expected moves: -1
    assert result["final_state"]["position"]["y"] == -1
    assert result["final_state"]["variables"]["A"] == 2


@pytest.mark.asyncio
async def test_triple_nested_if_else_middle_false():
    """Test 3 nested IF-ELSE with outer TRUE, middle FALSE."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Outer IF TRUE -> Middle IF FALSE -> Middle ELSE
    grid = [
        ["SET", "A", "10"],  # Row 0: A = 10
        ["SET", "B", "2"],  # Row 1: B = 2
        ["SET", "C", "3"],  # Row 2: C = 3
        ["IF", "A", ">", "5"],  # Row 3: Outer IF (10 > 5 = TRUE)
        ["", "MOVE", "1"],  # Row 4:   Move 1 (outer then)
        ["", "IF", "B", ">", "3"],  # Row 5:   Middle IF (2 > 3 = FALSE)
        ["", "", "MOVE", "2"],  # Row 6:     Move 2 (middle then) - NOT EXECUTED
        ["", "", "IF", "C", ">", "2"],  # Row 7:     Inner IF - NOT EXECUTED
        ["", "", "", "MOVE", "3"],  # Row 8:       Move 3 - NOT EXECUTED
        ["", "", "ELSE"],  # Row 9:     Inner ELSE - NOT EXECUTED
        ["", "", "", "MOVE", "-3"],  # Row 10:      Move -3 - NOT EXECUTED
        ["", "ELSE"],  # Row 11:   Middle ELSE
        ["", "", "MOVE", "-2"],  # Row 12:     Move -2 (middle else)
        ["ELSE"],  # Row 13: Outer ELSE - NOT EXECUTED
        ["", "MOVE", "-1"],  # Row 14:   Move -1 - NOT EXECUTED
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Path: Outer TRUE -> Middle FALSE -> Middle ELSE
    # Expected moves: 1 + (-2) = -1
    assert result["final_state"]["position"]["y"] == -1
    assert result["final_state"]["variables"]["B"] == 2


@pytest.mark.asyncio
async def test_triple_nested_if_else_inner_false():
    """Test 3 nested IF-ELSE with outer TRUE, middle TRUE, inner FALSE."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Outer IF TRUE -> Middle IF TRUE -> Inner IF FALSE -> Inner ELSE
    grid = [
        ["SET", "A", "10"],  # Row 0: A = 10
        ["SET", "B", "5"],  # Row 1: B = 5
        ["SET", "C", "1"],  # Row 2: C = 1
        ["IF", "A", ">", "5"],  # Row 3: Outer IF (10 > 5 = TRUE)
        ["", "MOVE", "1"],  # Row 4:   Move 1 (outer then)
        ["", "IF", "B", ">", "3"],  # Row 5:   Middle IF (5 > 3 = TRUE)
        ["", "", "MOVE", "2"],  # Row 6:     Move 2 (middle then)
        ["", "", "IF", "C", ">", "2"],  # Row 7:     Inner IF (1 > 2 = FALSE)
        ["", "", "", "MOVE", "3"],  # Row 8:       Move 3 (inner then) - NOT EXECUTED
        ["", "", "ELSE"],  # Row 9:     Inner ELSE
        ["", "", "", "MOVE", "-3"],  # Row 10:      Move -3 (inner else)
        ["", "ELSE"],  # Row 11:   Middle ELSE - NOT EXECUTED
        ["", "", "MOVE", "-2"],  # Row 12:     Move -2 - NOT EXECUTED
        ["ELSE"],  # Row 13: Outer ELSE - NOT EXECUTED
        ["", "MOVE", "-1"],  # Row 14:   Move -1 - NOT EXECUTED
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Path: Outer TRUE -> Middle TRUE -> Inner FALSE -> Inner ELSE
    # Expected moves: 1 + 2 + (-3) = 0
    assert result["final_state"]["position"]["y"] == 0
    assert result["final_state"]["variables"]["C"] == 1


@pytest.mark.asyncio
async def test_triple_nested_if_else_with_variables():
    """Test 3 nested IF-ELSE with variable modifications in each branch."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Test that variables are properly modified in the correct branches
    grid = [
        ["SET", "RESULT", "0"],  # Row 0: RESULT = 0
        ["SET", "A", "10"],  # Row 1: A = 10
        ["SET", "B", "5"],  # Row 2: B = 5
        ["SET", "C", "3"],  # Row 3: C = 3
        ["IF", "A", ">", "5"],  # Row 4: Outer IF (10 > 5 = TRUE)
        ["", "SET", "RESULT", "RESULT", "+", "100"],  # Row 5:   RESULT += 100
        ["", "IF", "B", ">", "3"],  # Row 6:   Middle IF (5 > 3 = TRUE)
        ["", "", "SET", "RESULT", "RESULT", "+", "10"],  # Row 7:     RESULT += 10
        ["", "", "IF", "C", ">", "2"],  # Row 8:     Inner IF (3 > 2 = TRUE)
        ["", "", "", "SET", "RESULT", "RESULT", "+", "1"],  # Row 9:       RESULT += 1
        ["", "", "ELSE"],  # Row 10:    Inner ELSE
        ["", "", "", "SET", "RESULT", "RESULT", "-", "1"],  # Row 11:      RESULT -= 1
        ["", "ELSE"],  # Row 12:   Middle ELSE
        ["", "", "SET", "RESULT", "RESULT", "-", "10"],  # Row 13:     RESULT -= 10
        ["ELSE"],  # Row 14: Outer ELSE
        ["", "SET", "RESULT", "RESULT", "-", "100"],  # Row 15:   RESULT -= 100
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Path: Outer TRUE -> Middle TRUE -> Inner TRUE
    # Expected RESULT: 0 + 100 + 10 + 1 = 111
    assert result["final_state"]["variables"]["RESULT"] == 111


@pytest.mark.asyncio
async def test_triple_nested_if_else_parse_structure():
    """Test that the parser correctly structures 3 nested IF-ELSE commands."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["IF", "TRUE"],  # Row 0: Outer IF
        ["", "MOVE", "1"],  # Row 1:   Outer then
        ["", "IF", "TRUE"],  # Row 2:   Middle IF
        ["", "", "MOVE", "2"],  # Row 3:     Middle then
        ["", "", "IF", "TRUE"],  # Row 4:     Inner IF
        ["", "", "", "MOVE", "3"],  # Row 5:       Inner then
        ["", "", "ELSE"],  # Row 6:     Inner ELSE
        ["", "", "", "MOVE", "-3"],  # Row 7:       Inner else
        ["", "ELSE"],  # Row 8:   Middle ELSE
        ["", "", "MOVE", "-2"],  # Row 9:     Middle else
        ["ELSE"],  # Row 10: Outer ELSE
        ["", "MOVE", "-1"],  # Row 11:   Outer else
    ]

    # Parse and examine the structure
    parser = GridParser(grid)
    commands = parser.parse()

    # Should have one top-level command (outer IF)
    assert len(commands) == 1
    outer_if = commands[0]
    assert isinstance(outer_if, IfCommand)

    # Outer IF should have 2 nested commands: MOVE and middle IF
    assert len(outer_if.nested_commands) == 2
    assert str(outer_if.nested_commands[0]) == "MoveCommand(NumberValue(1))"

    middle_if = outer_if.nested_commands[1]
    assert isinstance(middle_if, IfCommand)

    # Middle IF should have 2 nested commands: MOVE and inner IF
    assert len(middle_if.nested_commands) == 2
    assert str(middle_if.nested_commands[0]) == "MoveCommand(NumberValue(2))"

    inner_if = middle_if.nested_commands[1]
    assert isinstance(inner_if, IfCommand)

    # Inner IF should have 1 nested command: MOVE 3
    assert len(inner_if.nested_commands) == 1
    assert str(inner_if.nested_commands[0]) == "MoveCommand(NumberValue(3))"

    # Check ELSE commands
    assert len(outer_if.else_commands) == 1  # Outer ELSE has MOVE -1
    assert len(middle_if.else_commands) == 1  # Middle ELSE has MOVE -2
    assert len(inner_if.else_commands) == 1  # Inner ELSE has MOVE -3

    # Execute to verify behavior
    result = await engine_workflow(capture_messages, lambda: False, grid)
    assert result["success"] is True
    # All TRUE: 1 + 2 + 3 = 6
    assert result["final_state"]["position"]["y"] == 6


@pytest.mark.asyncio
async def test_triple_nested_if_else_with_sensors():
    """Test 3 nested IF-ELSE using sensor values."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    # Build commands manually to control sensor values
    sensors = MockSensors()
    sensors.distance = 15.0  # Will trigger obstacle detection (< 30)
    sensors.black_detected = True

    executor = Executor(capture_messages, lambda: False, sensors)
    context = ExecutionContext()
    context.sensors = sensors

    # IF DISTANCE < 30 -> IF BLACK_DETECTED -> IF DISTANCE < 20
    outer_if = CommandRegistry.create_command(
        "IF", ["DISTANCE", "<", "30"], GridPosition(0, 0)
    )
    assert outer_if is not None

    # Outer then branch
    move_1 = CommandRegistry.create_command("MOVE", ["1"], GridPosition(1, 1))
    assert move_1 is not None
    outer_if.add_nested_command(move_1)

    # Middle IF: BLACK_DETECTED
    middle_if = CommandRegistry.create_command(
        "IF", ["BLACK_DETECTED"], GridPosition(2, 1)
    )
    assert middle_if is not None
    assert isinstance(middle_if, IfCommand)
    outer_if.add_nested_command(middle_if)

    # Middle then branch
    move_2 = CommandRegistry.create_command("MOVE", ["2"], GridPosition(3, 2))
    assert move_2 is not None
    middle_if.add_nested_command(move_2)

    # Inner IF: DISTANCE < 20
    inner_if = CommandRegistry.create_command(
        "IF", ["DISTANCE", "<", "20"], GridPosition(4, 2)
    )
    assert inner_if is not None
    assert isinstance(inner_if, IfCommand)
    middle_if.add_nested_command(inner_if)

    # Inner then branch
    move_3 = CommandRegistry.create_command("MOVE", ["3"], GridPosition(5, 3))
    assert move_3 is not None
    inner_if.add_nested_command(move_3)

    # Inner else branch
    move_neg3 = CommandRegistry.create_command("MOVE", ["-3"], GridPosition(6, 3))
    assert move_neg3 is not None
    inner_if.add_else_command(move_neg3)

    # Middle else branch
    move_neg2 = CommandRegistry.create_command("MOVE", ["-2"], GridPosition(7, 2))
    assert move_neg2 is not None
    middle_if.add_else_command(move_neg2)

    # Outer else branch
    move_neg1 = CommandRegistry.create_command("MOVE", ["-1"], GridPosition(8, 1))
    assert move_neg1 is not None
    assert isinstance(outer_if, IfCommand)
    outer_if.add_else_command(move_neg1)

    # Execute
    context = await executor.execute_single(outer_if, context)

    # Expected path: distance=15 < 30 (TRUE) -> black_detected=TRUE -> distance=15 < 20 (TRUE)
    # Should execute: 1 + 2 + 3 = 6
    assert context.position.y == 6


@pytest.mark.asyncio
async def test_complex_nested_structure_with_loops():
    """Test nested IF-ELSE combined with loops."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    grid = [
        ["SET", "COUNT", "0"],  # Row 0: COUNT = 0
        ["IF", "TRUE"],  # Row 1: Outer IF
        ["", "LOOP", "2"],  # Row 2:   Loop 2 times
        ["", "", "IF", "COUNT", "<", "1"],  # Row 3:     Inner IF
        ["", "", "", "MOVE", "1"],  # Row 4:       Move 1
        ["", "", "", "SET", "COUNT", "COUNT", "+", "1"],  # Row 5:  COUNT++
        ["", "", "ELSE"],  # Row 6:     Inner ELSE
        ["", "", "", "MOVE", "2"],  # Row 7:       Move 2
        ["ELSE"],  # Row 8: Outer ELSE
        ["", "MOVE", "-5"],  # Row 9:   Move -5
    ]

    result = await engine_workflow(capture_messages, lambda: False, grid)

    assert result["success"] is True
    # Loop iteration 1: COUNT=0 < 1 (TRUE) -> MOVE 1, COUNT=1
    # Loop iteration 2: COUNT=1 < 1 (FALSE) -> MOVE 2
    # Total: 1 + 2 = 3
    assert result["final_state"]["position"]["y"] == 3
    assert result["final_state"]["variables"]["COUNT"] == 1
