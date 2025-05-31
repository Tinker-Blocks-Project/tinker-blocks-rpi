import asyncio
from typing import Any
from core import start_ws_server, broadcast, set_command_processor, ProcessController
from vision.workflow import ocr_grid_workflow
from engine.workflow import engine_workflow

# Global controller instance
controller: ProcessController | None = None


async def handle_run_command(params: dict[str, Any] | None = None):
    """Handle the 'run' command by running workflows."""
    if not controller:
        print("Error: Process controller not initialized")
        return

    if controller.is_running:
        await controller.send_message("Process already running!")
        return

    # Get workflow name
    workflow_name = params.get("workflow", "ocr_grid") if params else "ocr_grid"

    if workflow_name == "ocr_grid":
        # Run OCR grid workflow
        success, grid_data = await controller.run_workflow(
            ocr_grid_workflow, "OCR Grid Processing"
        )

        # Check if should chain to engine workflow
        if success and params and params.get("chain_engine", False):
            await controller.send_message("\n🔗 Chaining to engine workflow...")
            success, engine_result = await controller.run_workflow(
                lambda send_message, check_cancelled: engine_workflow(
                    send_message, check_cancelled, grid_data
                ),
                "Engine Execution",
            )

    elif workflow_name == "engine":
        # Run engine workflow directly
        # Check if grid data is provided or use last result
        grid_data = params.get("grid") if params else None

        if not grid_data and controller.last_result:
            # Try to use last result if it's a grid
            if isinstance(controller.last_result, list):
                grid_data = controller.last_result

        success, result = await controller.run_workflow(
            lambda send_message, check_cancelled: engine_workflow(
                send_message, check_cancelled, grid_data
            ),
            "Engine Execution",
        )

    elif workflow_name == "full":
        # Run full pipeline: OCR -> Engine
        success, grid_data = await controller.run_workflow(
            ocr_grid_workflow, "OCR Grid Processing"
        )

        if success and grid_data:
            await controller.send_message("\n🔗 Proceeding to engine execution...")
            success, engine_result = await controller.run_workflow(
                lambda send_message, check_cancelled: engine_workflow(
                    send_message, check_cancelled, grid_data
                ),
                "Engine Execution",
            )

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
    print("\nAvailable workflows:")
    print("  - ocr_grid: Run OCR grid processing only")
    print("  - engine: Run engine execution (requires grid data)")
    print("  - full: Run complete pipeline (OCR -> Engine)")
    print("\nExample commands:")
    print('  {"command": "run", "params": {"workflow": "full"}}')
    print(
        '  {"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true}}'
    )

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
