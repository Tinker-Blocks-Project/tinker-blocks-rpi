# ws_server.py
import asyncio
import json
import websockets
from process_controller import start_process, stop_process, register_send_func, get_current_task

connected_clients = set()

async def broadcast(message: str):
    for client in connected_clients.copy():
        try:
            await client.send(json.dumps({"message": message}))
        except:
            connected_clients.remove(client)

async def handler(websocket):
    print("✅ Client connected")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message}")
            try:
                data = json.loads(message)
                if data.get("command") == "run":
                    if get_current_task() and not get_current_task().done():
                        await broadcast("Process already running")
                    else:
                        await start_process()
                elif data.get("command") == "stop":
                    await stop_process()
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

def start_ws_server():
    register_send_func(broadcast)
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    return websockets.serve(handler, "192.168.1.18", 8765)