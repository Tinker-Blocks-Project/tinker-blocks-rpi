"""Tests for asyncio-based cancellation system."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from engine.commands.movement import MoveCommand
from engine.commands.utility import WaitCommand
from engine.context import ExecutionContext
from engine.executor import Executor

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestAsyncIOCancellation:
    """Test pure asyncio task cancellation."""

    async def test_wait_command_cancellation(self):
        """Test that WAIT command can be cancelled during sleep."""
        # Create WAIT command for 5 seconds
        wait_cmd = WaitCommand()
        wait_cmd.parse_args(["5"])

        # Create context
        context = ExecutionContext()
        context.send_message = AsyncMock()

        # Create task and cancel it quickly
        task = asyncio.create_task(wait_cmd.execute(context))

        # Wait a bit then cancel
        await asyncio.sleep(0.05)
        task.cancel()

        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_executor_cancellation(self):
        """Test that executor command execution can be cancelled."""
        # Create commands
        commands = []

        # Add WAIT command
        wait_cmd = WaitCommand()
        wait_cmd.parse_args(["5"])
        commands.append(wait_cmd)

        # Add MOVE command (should not execute)
        move_cmd = MoveCommand()
        move_cmd.parse_args(["10"])
        commands.append(move_cmd)

        # Create executor
        executor = Executor(AsyncMock())

        # Create task and cancel it during first command
        task = asyncio.create_task(executor.execute(commands))

        # Wait a bit then cancel
        await asyncio.sleep(0.05)
        task.cancel()

        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_cancellation_timing(self):
        """Test that cancellation happens quickly."""
        # Create WAIT for 5 seconds
        wait_cmd = WaitCommand()
        wait_cmd.parse_args(["5"])

        context = ExecutionContext()
        context.send_message = AsyncMock()

        # Time the cancellation
        start_time = asyncio.get_event_loop().time()

        task = asyncio.create_task(wait_cmd.execute(context))

        # Cancel after 0.1 seconds
        await asyncio.sleep(0.1)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        # Should be cancelled quickly, not wait the full 5 seconds
        assert elapsed < 1.0, f"Cancellation took too long: {elapsed}s"

    async def test_normal_completion_no_cancellation(self):
        """Test that commands complete normally when not cancelled."""
        # Create short WAIT command
        wait_cmd = WaitCommand()
        wait_cmd.parse_args(["0.1"])

        context = ExecutionContext()
        context.send_message = AsyncMock()

        # Should complete normally
        await wait_cmd.execute(context)

        # Should have incremented steps
        assert context.steps_executed > 0

    async def test_multiple_commands_cancellation(self):
        """Test cancelling a sequence of commands."""
        # Create multiple WAIT commands
        commands = []
        for i in range(3):
            wait_cmd = WaitCommand()
            wait_cmd.parse_args(["2"])  # 2 seconds each
            commands.append(wait_cmd)

        # Create executor
        executor = Executor(AsyncMock())

        # Create task and cancel it during execution
        task = asyncio.create_task(executor.execute(commands))

        # Wait a bit then cancel
        await asyncio.sleep(0.1)
        task.cancel()

        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_concurrent_cancellation_safe(self):
        """Test that concurrent cancellation doesn't cause issues."""
        # Create WAIT command
        wait_cmd = WaitCommand()
        wait_cmd.parse_args(["2"])

        context = ExecutionContext()
        context.send_message = AsyncMock()

        # Create task
        task = asyncio.create_task(wait_cmd.execute(context))

        # Wait a bit
        await asyncio.sleep(0.05)

        # Cancel multiple times (should be safe)
        task.cancel()
        task.cancel()
        task.cancel()

        # Should still only raise one CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    pytest.main([__file__])
