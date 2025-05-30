import asyncio
from typing import Optional, Dict, Any
from core import start_ws_server, initialize_controller, get_controller, Task
from vision.tasks import (
    capture_image_task,
    process_image_task,
    create_grid_task,
    run_ocr_task,
    map_ocr_to_grid_task,
)


async def handle_run_command(params: Optional[Dict[str, Any]] = None):
    """Handle the 'run' command by composing and executing vision tasks."""
    controller = get_controller()
    if not controller:
        print("Error: Process controller not initialized")
        return

    if controller.is_running:
        await controller.send_message("Process already running!")
        return

    # Compose the vision processing pipeline
    tasks = [
        Task(
            name="Capture Image",
            func=capture_image_task,
            args=(controller.send_message,),
        ),
        Task(
            name="Process Image",
            func=process_image_task,
            args=(controller.send_message,),
        ),
        Task(
            name="Create Grid", func=create_grid_task, args=(controller.send_message,)
        ),
        Task(name="Run OCR", func=run_ocr_task, args=(controller.send_message,)),
        Task(
            name="Map OCR to Grid",
            func=map_ocr_to_grid_task,
            args=(controller.send_message,),
        ),
    ]

    # Run the tasks
    await controller.run_tasks(tasks)


async def handle_stop_command():
    """Handle the 'stop' command."""
    controller = get_controller()
    if not controller:
        return

    if controller.is_running:
        controller.cancel()
        await controller.send_message("Stopping process...")
    else:
        await controller.send_message("No active process to stop")


# Command handlers mapping
COMMAND_HANDLERS = {
    "run": handle_run_command,
    "stop": handle_stop_command,
}


async def process_command(command: str, params: Dict[str, Any]):
    """Process incoming commands."""
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        await handler(params) if command == "run" else await handler()
    else:
        controller = get_controller()
        if controller:
            await controller.send_message(f"Unknown command: {command}")


async def main():
    # Initialize the process controller with broadcast function
    from core.ws_server import broadcast

    initialize_controller(broadcast)

    # Register command processor with WebSocket server
    from core import ws_server

    ws_server.set_command_processor(process_command)

    print("🚀 Starting WebSocket server...")
    server = await start_ws_server()
    print("🧩 WebSocket server running on ws://0.0.0.0:8765")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
