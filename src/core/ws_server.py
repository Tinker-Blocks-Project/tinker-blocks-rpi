import json
import websockets
from typing import Callable, Awaitable

connected_clients = set()
_command_processor: Callable[[str, dict], Awaitable[None]] | None = None


def set_command_processor(processor: Callable[[str, dict], Awaitable[None]]):
    """Set the command processor function."""
    global _command_processor
    _command_processor = processor


async def broadcast(message: str):
    """Broadcast a message to all connected clients."""
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

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.discard(websocket)


def start_ws_server():
    """Start the WebSocket server."""
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    return websockets.serve(handler, "0.0.0.0", 8765)
