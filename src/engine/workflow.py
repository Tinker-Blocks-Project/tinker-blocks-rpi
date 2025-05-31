"""Engine workflow for executing commands from a grid."""

from typing import Callable, Awaitable, Any
from engine.interpreter import Interpreter


async def engine_workflow(
    send_message: Callable[[str], Awaitable[None]],
    check_cancelled: Callable[[], bool],
    grid: list[list[str]] | None = None,
) -> dict[str, Any]:
    """
    Engine workflow that interprets and executes commands from the grid.

    Args:
        send_message: Function to send status messages
        check_cancelled: Function to check if process was cancelled
        grid: 2D list of commands to execute (optional, can use last result)

    Returns:
        Dictionary containing execution results
    """
    await send_message("Starting engine workflow...")

    # Validate grid input
    if grid is None:
        await send_message("❌ No grid data provided!")
        return {"success": False, "error": "No grid data"}

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    await send_message(f"📊 Processing grid with {rows} rows x {cols} columns")

    # Create interpreter
    interpreter = Interpreter()

    # Define callbacks for command execution
    async def on_command(row: int, col: int, command: str):
        """Callback when a command is executed."""
        await send_message(f"📍 [{row},{col}] Executing: {command}")

    async def on_unknown(command: str):
        """Callback for unknown commands."""
        await send_message(f"⚠️ Unknown command: {command}")

    # Execute grid with cancellation checking
    try:
        # Run interpreter
        final_state = await interpreter.execute_grid(
            grid,
            on_command=on_command,
            on_unknown_command=on_unknown,
        )

        # Check for cancellation periodically
        if check_cancelled():
            interpreter.cancel()
            await send_message("❌ Execution cancelled")
            return {
                "success": False,
                "error": "Cancelled",
                "state": final_state.to_dict(),
            }

        # Get final position and direction for display
        pos = final_state.position
        direction = final_state.direction
        steps = final_state.steps_executed

        # Final results
        await send_message("\n✅ Execution complete!")
        await send_message(f"📊 Total steps executed: {steps}")
        await send_message(f"📍 Final position: {pos}")
        await send_message(f"🧭 Final direction: {direction}")

        return {
            "success": True,
            "final_state": final_state.to_dict(),
            "grid_shape": (rows, cols),
        }

    except Exception as e:
        await send_message(f"❌ Execution error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "state": interpreter.get_state().to_dict() if interpreter else None,
        }
