"""Tests for workflow chaining and data passing between workflows."""

import pytest
from core import ProcessController
from core.types import LogLevel


@pytest.mark.asyncio
async def test_workflow_data_passing():
    """Test that data passes correctly between chained workflows."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # First workflow returns data
    async def workflow1(send_message):
        await send_message("Workflow 1 running", LogLevel.INFO)
        return {"data": [1, 2, 3], "status": "complete"}

    # Second workflow uses data from first
    async def workflow2(send_message, input_data=None):
        await send_message(f"Workflow 2 received: {input_data}", LogLevel.INFO)
        if input_data:
            return {
                "processed": len(input_data.get("data", [])),
                "original": input_data,
            }
        return {"processed": 0}

    # Run first workflow
    success1, result1 = await controller.run_workflow(workflow1, "First")
    assert success1 is True
    assert result1 is not None
    assert result1["status"] == "complete"

    # Run second workflow with result from first
    success2, result2 = await controller.run_workflow(
        lambda send_message: workflow2(send_message, result1), "Second"
    )
    assert success2 is True
    assert result2 is not None
    assert result2["processed"] == 3  # Length of [1,2,3]
    assert result2["original"] == result1


@pytest.mark.asyncio
async def test_controller_last_result():
    """Test that controller stores last result correctly."""

    async def noop_message(msg: str, level):
        pass

    controller = ProcessController(noop_message)

    # Initially no result
    assert controller.last_result is None

    # Run workflow that returns data
    async def data_workflow(send_message):
        return {"test": "data"}

    success, result = await controller.run_workflow(data_workflow, "Test")

    assert success is True
    assert result == {"test": "data"}
    assert controller.last_result == {"test": "data"}


@pytest.mark.asyncio
async def test_conditional_workflow_chaining():
    """Test conditional chaining based on workflow results."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Workflow that can succeed or fail based on input
    async def conditional_workflow(send_message, should_succeed=True):
        if should_succeed:
            await send_message("Success path", LogLevel.INFO)
            return {"status": "success", "value": 42}
        else:
            await send_message("Failure path", LogLevel.INFO)
            raise ValueError("Intentional failure")

    # Success case - should chain
    success1, result1 = await controller.run_workflow(
        lambda send_message: conditional_workflow(send_message, True),
        "Conditional Success",
    )

    if success1 and result1 and result1.get("status") == "success":
        # Chain to next workflow
        async def followup_workflow(send_message):
            await send_message("Following up on success", LogLevel.INFO)
            return {"followup": True}

        success2, result2 = await controller.run_workflow(followup_workflow, "Followup")
        assert success2 is True
        assert result2 is not None
        assert result2["followup"] is True

    # Failure case - should not chain
    success3, result3 = await controller.run_workflow(
        lambda send_message: conditional_workflow(send_message, False),
        "Conditional Failure",
    )

    assert success3 is False
    assert result3 is None
    assert any("Intentional failure" in msg for msg in messages)


@pytest.mark.asyncio
async def test_multi_stage_pipeline():
    """Test a multi-stage processing pipeline."""
    messages = []

    async def capture_messages(msg, level):
        messages.append(msg)

    controller = ProcessController(capture_messages)

    # Stage 1: Generate data
    async def stage1(send_message):
        await send_message("Stage 1: Generating data", LogLevel.INFO)
        return {"numbers": [1, 2, 3, 4, 5]}

    # Stage 2: Transform data
    async def stage2(send_message, input_data):
        await send_message("Stage 2: Transforming data", LogLevel.INFO)
        numbers = input_data.get("numbers", [])
        return {"doubled": [n * 2 for n in numbers]}

    # Stage 3: Aggregate results
    async def stage3(send_message, input_data):
        await send_message("Stage 3: Aggregating results", LogLevel.INFO)
        doubled = input_data.get("doubled", [])
        return {"sum": sum(doubled), "count": len(doubled)}

    # Run pipeline
    s1, r1 = await controller.run_workflow(stage1, "Stage 1")
    assert s1 and r1 is not None and r1["numbers"] == [1, 2, 3, 4, 5]

    s2, r2 = await controller.run_workflow(
        lambda send_message: stage2(send_message, r1), "Stage 2"
    )
    assert s2 and r2 is not None and r2["doubled"] == [2, 4, 6, 8, 10]

    s3, r3 = await controller.run_workflow(
        lambda send_message: stage3(send_message, r2), "Stage 3"
    )
    assert s3 and r3 is not None
    assert r3["sum"] == 30  # 2+4+6+8+10
    assert r3["count"] == 5

    # Verify all stages ran
    assert "Stage 1: Generating data" in messages
    assert "Stage 2: Transforming data" in messages
    assert "Stage 3: Aggregating results" in messages
