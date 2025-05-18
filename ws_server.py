import asyncio
import websockets
from process_controller import start_process, stop_process

connected_clients = set()

async def handler(websocket):
    print("✅ Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"📩 Received: {message}")
            if message == "run":
                await start_process()
            elif message == "stop":
                await stop_process()
            else:
                print("❓ Unknown command:", message)
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        connected_clients.remove(websocket)

async def send_to_mobile(message: str):
    for client in connected_clients.copy():
        try:
            await client.send(message)
        except Exception as e:
            print(f"⚠️ Failed to send message: {e}")

def start_ws_server():
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    return websockets.serve(handler, "192.168.1.18", 8765)
