from typing import Callable, Awaitable, Any
from core.types import LogLevel

from .parser import GridParser
from .executor import Executor
from .hardware import MockHardware, CarHardware


async def engine_workflow(
    send_message: Callable[[str, LogLevel], Awaitable[None]],
    check_cancelled: Callable[[], bool],
    grid_data: list[list[str]] | None = None,
    use_hardware: bool = False,
) -> dict[str, Any]:
    """Process a grid and execute the resulting program.

    Args:
        send_message: Callback for sending status messages
        check_cancelled: Callback for checking if execution should be cancelled
        grid_data: 2D grid of programming blocks
        use_hardware: Whether to use real hardware API or mock hardware

    Returns:
        Dictionary with execution results
    """
    # Validate input
    if not grid_data:
        await send_message("❌ No grid data provided", LogLevel.ERROR)
        return {
            "success": False,
            "error": "No grid data provided",
            "final_state": {
                "steps_executed": 0,
                "position": {"x": 0, "y": 0},
                "direction": "forward",
            },
        }

    # Check if grid is empty
    is_empty = all(all(cell.strip() == "" for cell in row) for row in grid_data)

    if is_empty:
        await send_message("ℹ️ Grid is empty - no commands to execute", LogLevel.INFO)
        return {
            "success": True,
            "error": None,
            "final_state": {
                "steps_executed": 0,
                "position": {"x": 0, "y": 0},
                "direction": "forward",
                "variables": {},
                "pen_down": False,
                "path": [],
            },
        }

    try:
        # Display grid
        await send_message("\n📊 Grid contents:", LogLevel.INFO)
        for i, row in enumerate(grid_data):
            row_str = " | ".join(
                cell if cell else "___" for cell in row[:10]
            )  # Show first 10 cols
            await send_message(f"Row {i:2d}: {row_str}", LogLevel.DEBUG)

        # Parse grid into commands
        await send_message("\n🔍 Parsing grid into commands...", LogLevel.INFO)
        parser = GridParser(grid_data)
        commands = parser.parse()

        await send_message(
            f"✅ Parsed {len(commands)} top-level commands", LogLevel.SUCCESS
        )

        # Display parsed commands
        await send_message("\n📝 Command structure:", LogLevel.INFO)
        for i, cmd in enumerate(commands):
            await send_message(f"  {i+1}. {cmd}", LogLevel.DEBUG)
            _display_nested_commands(cmd, send_message, "    ")

        # Execute commands
        await send_message("\n⚡ Executing commands...", LogLevel.INFO)

        # Initialize hardware interface
        hardware = CarHardware() if use_hardware else MockHardware()
        if use_hardware:
            await send_message("🔗 Using real hardware API", LogLevel.INFO)

        else:
            await send_message("🤖 Using mock hardware", LogLevel.INFO)

        executor = Executor(send_message, check_cancelled, hardware=hardware)
        context = await executor.execute(commands)

        # Get final state
        final_state = context.get_state_dict()

        await send_message("\n✅ Execution complete!", LogLevel.SUCCESS)
        await send_message(
            f"📊 Total steps executed: {final_state['steps_executed']}", LogLevel.INFO
        )
        await send_message(
            f"📍 Final position: ({final_state['position']['x']}, {final_state['position']['y']})",
            LogLevel.INFO,
        )
        await send_message(
            f"🧭 Final direction: {final_state['direction']}", LogLevel.INFO
        )

        if final_state["variables"]:
            await send_message("\n📊 Variables:", LogLevel.INFO)
            for var, value in final_state["variables"].items():
                await send_message(f"  {var} = {value}", LogLevel.DEBUG)

        if final_state["path"]:
            await send_message(
                f"\n✏️ Drew path with {len(final_state['path'])} points", LogLevel.INFO
            )

        return {
            "success": True,
            "error": None,
            "final_state": final_state,
            "commands_parsed": len(commands),
        }

    except Exception as e:
        error_msg = str(e)
        await send_message(f"\n❌ Error: {error_msg}", LogLevel.ERROR)

        # Return error state
        return {
            "success": False,
            "error": error_msg,
            "final_state": {
                "steps_executed": 0,
                "position": {"x": 0, "y": 0},
                "direction": "forward",
            },
        }


def _display_nested_commands(command: Any, send_message_sync: Any, indent: str) -> None:
    """Helper to display nested commands (synchronous)."""
    if hasattr(command, "nested_commands"):
        for nested in command.nested_commands:
            # Note: This is a simplified sync version for display
            # In a real async context, we'd need to make this async
            print(f"{indent}{nested}")
            _display_nested_commands(nested, send_message_sync, indent + "  ")

    # Show ELSE block for IF commands
    if hasattr(command, "else_commands") and command.else_commands:
        print(f"{indent}ELSE:")
        for else_cmd in command.else_commands:
            print(f"{indent}  {else_cmd}")
            _display_nested_commands(else_cmd, send_message_sync, indent + "    ")
