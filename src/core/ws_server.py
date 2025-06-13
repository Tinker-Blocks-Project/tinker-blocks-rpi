import json
import websockets
from typing import Callable, Awaitable
from .types import LogLevel

connected_clients = set()
_command_processor: Callable[[str, dict], Awaitable[None]] | None = None


def set_command_processor(processor: Callable[[str, dict], Awaitable[None]]):
    """Set the command processor function."""
    global _command_processor
    _command_processor = processor


async def broadcast(message: str, level: LogLevel = LogLevel.INFO):
    """Broadcast a message to all connected clients and optionally print to console.

    Args:
        message: The message to send
        level: Log level - DEBUG goes to CLI only, others go to both UI and CLI
    """
    # Always print to console for CLI visibility
    print(message)

    # Send to UI clients unless it's DEBUG level
    if level != LogLevel.DEBUG:
        # Create list copy to avoid modification during iteration
        for client in list(connected_clients):
            try:
                await client.send(json.dumps({"message": message}))
            except Exception as e:
                print(f"Error sending message to client: {e}")
                connected_clients.discard(client)


async def handler(websocket):
    """Handle WebSocket connections."""
    print("✅ Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message}")
            try:
                data = json.loads(message)
                command = data.get("command")

                if command and _command_processor:
                    # Process command through the registered processor
                    params = data.get("params", {})
                    await _command_processor(command, params)
                else:
                    await websocket.send(
                        json.dumps({"error": "No command processor registered"})
                    )

            except json.JSONDecodeError as e:
                await websocket.send(json.dumps({"error": f"Invalid JSON: {e}"}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.discard(websocket)


def start_ws_server():
    """Start the WebSocket server."""
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    return websockets.serve(handler, "0.0.0.0", 8765)
