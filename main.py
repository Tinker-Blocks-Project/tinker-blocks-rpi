import asyncio
from ws_server import start_ws_server

async def main():
    print("🚀 Starting WebSocket server...")
    server = await start_ws_server()  # Await the coroutine
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")
    
    await server.wait_closed()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
