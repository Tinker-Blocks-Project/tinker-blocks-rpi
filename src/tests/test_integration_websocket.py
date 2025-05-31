"""Integration tests for WebSocket server and command processing."""

import asyncio
import json
import pytest
import websockets
from core import start_ws_server, set_command_processor


@pytest.mark.asyncio
async def test_websocket_command_flow():
    """Test complete command flow through WebSocket."""
    received_commands = []

    async def mock_processor(command, params):
        received_commands.append((command, params))

    set_command_processor(mock_processor)

    # Start server
    server = await start_ws_server()

    try:
        # Connect client
        async with websockets.connect("ws://localhost:8765") as ws:
            # Test various commands
            test_commands = [
                {"command": "run", "params": {"workflow": "ocr_grid"}},
                {"command": "stop"},
                {"command": "run", "params": {"workflow": "engine", "grid": [["FWD"]]}},
            ]

            for cmd in test_commands:
                await ws.send(json.dumps(cmd))
                await asyncio.sleep(0.01)  # Small delay

            # Verify commands were processed
            assert len(received_commands) == 3
            assert received_commands[0] == ("run", {"workflow": "ocr_grid"})
            assert received_commands[1] == ("stop", {})
            assert received_commands[2] == (
                "run",
                {"workflow": "engine", "grid": [["FWD"]]},
            )

    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_websocket_broadcast_messages():
    """Test that broadcast messages reach connected clients."""
    from core import broadcast

    messages_received = []

    # Start server
    server = await start_ws_server()

    try:
        # Connect client
        async with websockets.connect("ws://localhost:8765") as ws:
            # Start listening task
            async def listen():
                try:
                    while True:
                        msg = await ws.recv()
                        messages_received.append(json.loads(msg))
                except websockets.exceptions.ConnectionClosed:
                    pass

            listen_task = asyncio.create_task(listen())

            # Send broadcasts
            await broadcast("Test message 1")
            await broadcast("Test message 2")
            await asyncio.sleep(0.1)  # Allow messages to be received

            # Cancel listener
            listen_task.cancel()
            try:
                await listen_task
            except asyncio.CancelledError:
                pass

            # Check messages
            assert len(messages_received) >= 2
            assert messages_received[0]["message"] == "Test message 1"
            assert messages_received[1]["message"] == "Test message 2"

    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_websocket_multiple_clients():
    """Test that multiple clients can connect and receive broadcasts."""
    from core import broadcast

    # Start server
    server = await start_ws_server()

    try:
        # Connect multiple clients
        clients = []
        client_messages = [[] for _ in range(3)]

        for i in range(3):
            ws = await websockets.connect("ws://localhost:8765")
            clients.append(ws)

            # Start listener for each client
            async def listen(client_idx, ws):
                try:
                    while True:
                        msg = await ws.recv()
                        client_messages[client_idx].append(json.loads(msg))
                except websockets.exceptions.ConnectionClosed:
                    pass

            asyncio.create_task(listen(i, ws))

        # Broadcast to all
        await broadcast("Message to all clients")
        await asyncio.sleep(0.1)

        # Verify all clients received the message
        for i in range(3):
            assert len(client_messages[i]) >= 1
            assert client_messages[i][0]["message"] == "Message to all clients"

        # Close clients
        for ws in clients:
            await ws.close()

    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_websocket_error_handling():
    """Test WebSocket error handling for invalid messages."""
    # Start server
    server = await start_ws_server()

    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            # Send invalid JSON
            await ws.send("not valid json")

            # Should receive error response
            response = await ws.recv()
            data = json.loads(response)
            assert data["error"] == "Invalid JSON"

            # Send JSON without command
            await ws.send(json.dumps({"params": {"test": True}}))
            await asyncio.sleep(0.01)  # No error expected, just ignored

    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_websocket_reconnection():
    """Test client reconnection handling."""
    from core import broadcast

    # Start server
    server = await start_ws_server()

    try:
        # First connection
        ws1 = await websockets.connect("ws://localhost:8765")

        # Disconnect
        await ws1.close()

        # Reconnect
        ws2 = await websockets.connect("ws://localhost:8765")

        # Should still receive broadcasts
        messages = []

        async def listen():
            try:
                while True:
                    msg = await ws2.recv()
                    messages.append(json.loads(msg))
            except websockets.exceptions.ConnectionClosed:
                pass

        listen_task = asyncio.create_task(listen())

        await broadcast("After reconnection")
        await asyncio.sleep(0.1)

        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

        assert len(messages) >= 1
        assert messages[0]["message"] == "After reconnection"

        await ws2.close()

    finally:
        server.close()
        await server.wait_closed()
