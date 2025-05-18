import asyncio
import websockets
import json
from process_controller import start_process, stop_process, register_send_func

connected_clients = set()
async def send_to_mobile(message: str):
    for client in connected_clients.copy():
        try:
            await client.send(message)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            connected_clients.remove(client)
async def handler(websocket):
    print("✅ Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"📩 Received: {message}")
            try:
                obj = json.loads(message)
                command = obj.get("command")
            except json.JSONDecodeError:
                print("❌ Invalid JSON received")
                continue

            if command == "run":
                await start_process()
            elif command == "stop":
                await stop_process()
            else:
                print(f"❓ Unknown command: {command}")
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        connected_clients.remove(websocket)

def start_ws_server():
    register_send_func(send_to_mobile)
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    return websockets.serve(handler, "192.168.1.18", 8765)
