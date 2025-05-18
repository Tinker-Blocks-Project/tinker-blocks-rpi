# ws_server.py

import asyncio
import websockets
import json
from main import start_process, stop_process  # Functions you’ll define

clients = set()

async def handler(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            print("Received from mobile:", message)
            try:
                data = json.loads(message)
                if data.get("command") == "run":
                    await start_process(websocket)
                elif data.get("command") == "stop":
                    await stop_process(websocket)
            except Exception as e:
                print("Error processing command:", e)
    finally:
        clients.remove(websocket)

def send_to_mobile(websocket, msg: str):
    asyncio.create_task(websocket.send(msg))

def start_ws_server():
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(handler, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)
    print("WebSocket server started on ws://0.0.0.0:8765")
    loop.run_forever()
