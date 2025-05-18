import asyncio
from ws_server import start_ws_server

if __name__ == "__main__":
    print("🚀 Starting WebSocket server...")
    asyncio.run(start_ws_server())
