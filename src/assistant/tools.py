from typing import Callable, Awaitable, List, Optional
from langchain_core.tools import tool
from core.types import LogLevel
from core import ProcessController
from vision.ocr import VLM_OCR
from vision.workflow import ocr_grid_workflow
from engine.workflow import engine_workflow


def create_assistant_tools(
    send_message: Callable[[str, LogLevel], Awaitable[None]],
    controller: ProcessController,
    ocr_engine: VLM_OCR,
):
    """Factory function to create assistant tools with necessary dependencies.

    This can be used by other parts of the system that need the same tools.
    The main assistant workflow creates its own tools internally.

    Args:
        send_message: Function to send messages to the user
        controller: Process controller for managing workflows
        ocr_engine: OCR engine for reading blocks

    Returns:
        List of LangChain tools ready to be used with an agent
    """

    @tool
    async def read_blocks() -> str:
        """Read the current block arrangement on the grid."""
        try:
            await send_message("📸 Reading the blocks on your grid...", LogLevel.INFO)

            success, grid_data = await controller.run_workflow(
                lambda send_message: ocr_grid_workflow(
                    ocr_engine=ocr_engine,
                    send_message=send_message,
                ),
                "Reading Blocks",
            )

            if not success or not grid_data:
                return "❌ I couldn't read the blocks on your grid. Make sure the blocks are clearly visible and try again."

            # Format the grid data
            grid_str = "Here's what I see on your grid:\n\n"
            non_empty_count = 0
            for row_idx, row in enumerate(grid_data.blocks):
                non_empty_cells = [cell for cell in row if cell.strip()]
                if non_empty_cells:
                    grid_str += f"Row {row_idx + 1}: {' | '.join(non_empty_cells)}\n"
                    non_empty_count += len(non_empty_cells)

            grid_str += f"\nTotal non-empty blocks: {non_empty_count}"
            return grid_str

        except Exception as e:
            await send_message(f"❌ Error reading blocks: {str(e)}", LogLevel.ERROR)
            return f"❌ I encountered an error while reading the blocks: {str(e)}"

    @tool
    async def execute_program(
        use_current_grid: bool = True,
        custom_grid: Optional[List[List[str]]] = None,
    ) -> str:
        """Run a program on the robot car to control its movement and actions.

        Args:
            use_current_grid: Run the blocks currently on the grid (True) or run a custom example program (False)
            custom_grid: If not using current grid, provide a sample program as a 2D array

        Example custom_grid structure (maze-solving algorithm):
        [
            ["WHILE", "TRUE"],
            ["", "IF", "OBSTACLE", "OR", "BLACK_ON"],
            ["", "", "TURN", "RIGHT"],
            ["", "", "MOVE"],
            ["", "", "TURN", "LEFT"],
            ["", "ELSE"],
            ["", "", "MOVE"]
        ]

        Grid format notes:
        - Each row is a list of strings representing one row of blocks
        - Empty strings ("") represent indentation/nesting
        - Commands are read left-to-right, top-to-bottom
        - Indentation (empty cells) creates nested blocks for loops/conditions
        """
        try:
            grid_data = None

            if use_current_grid:
                await send_message(
                    "📸 Reading your current blocks first...", LogLevel.INFO
                )

                success, grid_result = await controller.run_workflow(
                    lambda send_message: ocr_grid_workflow(
                        ocr_engine=ocr_engine,
                        send_message=send_message,
                    ),
                    "Reading Current Grid",
                )

                if not success or not grid_result:
                    return "❌ I couldn't read your current blocks. Please make sure they're clearly visible."

                grid_data = grid_result.blocks
                await send_message(
                    "✅ Got your blocks! Now running the program...", LogLevel.INFO
                )

            else:
                if not custom_grid:
                    return "❌ No custom grid provided. Please specify a custom program or use the current grid."
                grid_data = custom_grid
                await send_message("🤖 Running the custom program...", LogLevel.INFO)

            success, result = await controller.run_workflow(
                lambda send_message: engine_workflow(
                    send_message=send_message,
                    grid_data=grid_data,
                    use_hardware=True,
                ),
                "Program Execution",
            )

            if success:
                return "✅ Program executed successfully! Check the logs above to see what the robot did."
            else:
                return "❌ Program execution failed. Check the error messages above for details."

        except Exception as e:
            await send_message(f"❌ Error executing program: {str(e)}", LogLevel.ERROR)
            return f"❌ I encountered an error while running the program: {str(e)}"

    @tool
    async def think(thought: str) -> str:
        """Share your thinking process with the child."""
        try:
            await send_message(f"🤔 **Thinking:** {thought}", LogLevel.ASSISTANT)
            return "✅ Shared my thinking with the child."
        except Exception as e:
            return f"❌ Error sharing thought: {str(e)}"

    @tool
    async def answer(message: str) -> str:
        """Give your final response to the child."""
        try:
            await send_message(f"💡 **Answer:** {message}", LogLevel.ASSISTANT)
            return "✅ Delivered answer to the child."
        except Exception as e:
            return f"❌ Error delivering answer: {str(e)}"

    return [read_blocks, execute_program, think, answer]
