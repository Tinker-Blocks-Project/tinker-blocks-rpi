import asyncio
from typing import Any
from core import start_ws_server, broadcast, set_command_processor, ProcessController
from vision.workflow import ocr_grid_workflow

# Global controller instance
controller: ProcessController | None = None


async def handle_run_command(params: dict[str, Any] | None = None):
    """Handle the 'run' command by running the OCR grid workflow."""
    if not controller:
        print("Error: Process controller not initialized")
        return

    if controller.is_running:
        await controller.send_message("Process already running!")
        return

    # Run the OCR grid workflow
    workflow_name = params.get("workflow", "ocr_grid") if params else "ocr_grid"

    if workflow_name == "ocr_grid":
        await controller.run_workflow(ocr_grid_workflow, "OCR Grid Processing")
    else:
        await controller.send_message(f"Unknown workflow: {workflow_name}")


async def handle_stop_command():
    """Handle the 'stop' command."""
    if not controller:
        return

    if controller.is_running:
        controller.cancel()
        await controller.send_message("Stopping process...")
    else:
        await controller.send_message("No active process to stop")


async def process_command(command: str, params: dict[str, Any]):
    """Process incoming commands from WebSocket."""
    handlers = {
        "run": lambda: handle_run_command(params),
        "stop": handle_stop_command,
    }

    handler = handlers.get(command)
    if handler:
        await handler()
    elif controller:
        await controller.send_message(f"Unknown command: {command}")


async def main():
    """Initialize and start the application."""
    global controller

    # Create the process controller
    controller = ProcessController(broadcast)

    # Register command processor with WebSocket server
    set_command_processor(process_command)

    print("🚀 Starting WebSocket server...")
    server = await start_ws_server()
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
