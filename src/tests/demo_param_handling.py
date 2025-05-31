"""Test script to verify WebSocket parameter handling."""

import asyncio
import json
import websockets


async def test_websocket_params():
    """Test that parameters are correctly passed through WebSocket."""
    uri = "ws://localhost:8765"

    # Test cases with different parameter structures
    test_cases = [
        {
            "name": "Full workflow with params",
            "message": {"command": "run", "params": {"workflow": "full"}},
        },
        {
            "name": "OCR workflow with chaining",
            "message": {
                "command": "run",
                "params": {"workflow": "ocr_grid", "chain_engine": True},
            },
        },
        {
            "name": "Engine workflow with custom grid",
            "message": {
                "command": "run",
                "params": {
                    "workflow": "engine",
                    "grid": [["FORWARD", "RIGHT"], ["LEFT", "FORWARD"]],
                },
            },
        },
        {"name": "Stop command without params", "message": {"command": "stop"}},
    ]

    print("🧪 Testing WebSocket parameter handling...\n")

    try:
        async with websockets.connect(uri) as websocket:
            for test in test_cases:
                print(f"📤 Test: {test['name']}")
                print(f"   Sending: {json.dumps(test['message'], indent=2)}")

                # Send message
                await websocket.send(json.dumps(test["message"]))

                # Receive responses (wait a bit for multiple messages)
                responses = []
                try:
                    while True:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        responses.append(json.loads(response))
                except asyncio.TimeoutError:
                    pass

                if responses:
                    print("   📥 Responses:")
                    for resp in responses:
                        print(f"      {resp}")
                else:
                    print("   ⚠️  No response received")

                print()

                # Small delay between tests
                await asyncio.sleep(0.1)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the WebSocket server is running:")
        print("  python main.py")


if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket Parameter Handling Test")
    print("=" * 60)
    asyncio.run(test_websocket_params())
