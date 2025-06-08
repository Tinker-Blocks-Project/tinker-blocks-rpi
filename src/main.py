import asyncio
from typing import Any
from core import start_ws_server, broadcast, set_command_processor, ProcessController
from vision.workflow import ocr_grid_workflow
from engine.workflow import engine_workflow
from vision.ocr import VLM_OCR
from core.chat_model import get_chat_model

# Global controller instance
controller: ProcessController | None = None

ocr_engine = VLM_OCR(chat_model=get_chat_model())


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
            lambda send_message, check_cancelled: ocr_grid_workflow(
                ocr_engine=ocr_engine,
                send_message=send_message,
                check_cancelled=check_cancelled,
            ),
            "OCR Grid Processing",
        )

        if not success:
            await controller.send_message("OCR grid workflow failed")
            return

        # Check if should chain to engine workflow
        if success and params and params.get("chain_engine", False):
            await controller.send_message("\n🔗 Chaining to engine workflow...")
            use_hardware = params.get("use_hardware", False)
            success, _ = await controller.run_workflow(
                lambda send_message, check_cancelled: engine_workflow(
                    send_message=send_message,
                    check_cancelled=check_cancelled,
                    grid_data=grid_data.blocks if grid_data else None,
                    use_hardware=use_hardware,
                ),
                "Engine Execution",
            )

    elif workflow_name == "engine":
        # Run engine workflow directly
        # Check if grid data is provided or use last result
        grid_data = params.get("grid") if params else None
        use_hardware = params.get("use_hardware", False) if params else False

        if not grid_data and controller.last_result:
            # Try to use last result if it's a grid
            if isinstance(controller.last_result, list):
                grid_data = controller.last_result

        success, _ = await controller.run_workflow(
            lambda send_message, check_cancelled: engine_workflow(
                send_message=send_message,
                check_cancelled=check_cancelled,
                grid_data=grid_data,
                use_hardware=use_hardware,
            ),
            "Engine Execution",
        )

    elif workflow_name == "full":
        # Run full pipeline: OCR -> Engine
        success, grid_data = await controller.run_workflow(
            lambda send_message, check_cancelled: ocr_grid_workflow(
                ocr_engine=ocr_engine,
                send_message=send_message,
                check_cancelled=check_cancelled,
            ),
            "OCR Grid Processing",
        )

        if success and grid_data:
            await controller.send_message("\n🔗 Proceeding to engine execution...")
            use_hardware = params.get("use_hardware", False) if params else False
            success, _ = await controller.run_workflow(
                lambda send_message, check_cancelled: engine_workflow(
                    send_message=send_message,
                    check_cancelled=check_cancelled,
                    grid_data=grid_data.blocks,
                    use_hardware=use_hardware,
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
    print('  {"command": "run", "params": {"workflow": "full", "use_hardware": true}}')
    print(
        '  {"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true}}'
    )
    print(
        '  {"command": "run", "params": {"workflow": "engine", "use_hardware": true, "grid": [["MOVE", "10"], ["TURN", "RIGHT"]]}}'
    )

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
