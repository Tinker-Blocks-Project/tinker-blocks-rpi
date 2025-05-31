"""Tests for WebSocket server parameter handling."""

import json
import pytest
from unittest.mock import AsyncMock, patch
from core.ws_server import handler, set_command_processor


@pytest.mark.asyncio
async def test_command_processor_receives_params_only():
    """Test that command processor receives only params, not entire data."""
    # Mock command processor
    mock_processor = AsyncMock()
    set_command_processor(mock_processor)

    # Mock websocket
    mock_websocket = AsyncMock()
    mock_websocket.__aiter__.return_value = [
        json.dumps(
            {"command": "run", "params": {"workflow": "full", "chain_engine": True}}
        )
    ]

    # Patch connected_clients to avoid side effects
    with patch("core.ws_server.connected_clients", set()):
        await handler(mock_websocket)

    # Verify processor was called with correct arguments
    mock_processor.assert_called_once_with(
        "run",  # command
        {  # params only, not entire data
            "workflow": "full",
            "chain_engine": True,
        },
    )


@pytest.mark.asyncio
async def test_command_processor_handles_missing_params():
    """Test that command processor receives empty dict when params missing."""
    mock_processor = AsyncMock()
    set_command_processor(mock_processor)

    mock_websocket = AsyncMock()
    mock_websocket.__aiter__.return_value = [
        json.dumps(
            {
                "command": "stop"
                # No params field
            }
        )
    ]

    with patch("core.ws_server.connected_clients", set()):
        await handler(mock_websocket)

    # Should receive empty dict for params
    mock_processor.assert_called_once_with("stop", {})


@pytest.mark.asyncio
async def test_invalid_json_sends_error():
    """Test that invalid JSON sends error response."""
    mock_websocket = AsyncMock()
    mock_websocket.__aiter__.return_value = ["not valid json"]

    with patch("core.ws_server.connected_clients", set()):
        await handler(mock_websocket)

    # Should send error response
    mock_websocket.send.assert_called_with(json.dumps({"error": "Invalid JSON"}))
