from dataclasses import dataclass
from typing import cast

from .types import GridPosition
from .commands import Command, CommandRegistry, IfCommand, ElseCommand
from .mappings import preprocess_grid


@dataclass
class GridToken:
    """A token from the grid with its position."""

    text: str
    position: GridPosition

    def __repr__(self) -> str:
        return f"Token({self.text}@{self.position.row},{self.position.col})"


class GridParser:
    """Parses a 2D grid into a command tree.

    The grid is read left-to-right, top-to-bottom. Each non-empty cell
    represents a command. Commands are executed sequentially in reading order.

    Indentation for nested blocks is determined by starting a new row
    at a column position greater than 0 (e.g., for loops and conditionals).
    """

    def __init__(self, grid: list[list[str]]):
        """Initialize parser with a 2D grid.

        Args:
            grid: 2D list of strings representing the programming blocks
        """
        # Apply command mappings preprocessing before parsing
        self.grid = preprocess_grid(grid)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.grid else 0

    def parse(self) -> list[Command]:
        """Parse the grid into a list of commands with proper nesting based on indentation.

        Returns:
            List of Command objects representing the program
        """
        commands = []
        stack: list[tuple[int, Command]] = []  # (column, command) for nesting
        in_else_block = False
        else_if_command: IfCommand | None = None

        # Process each row
        for row_idx in range(self.rows):
            if row_idx >= len(self.grid):
                continue

            # Find the first non-empty cell in this row
            first_col = -1
            for col_idx in range(len(self.grid[row_idx])):
                if self.grid[row_idx][col_idx].strip():
                    first_col = col_idx
                    break

            if first_col == -1:  # Empty row
                continue

            # Pop from stack if we're at same or lesser indentation
            # BUT don't pop IF commands if the current command is ELSE at same level
            while stack and stack[-1][0] >= first_col:
                # Special case: don't pop IF if current command is ELSE at same level
                if (
                    self.grid[row_idx][first_col].strip().upper() == "ELSE"
                    and stack[-1][0] == first_col
                    and isinstance(stack[-1][1], IfCommand)
                ):
                    break

                popped = stack.pop()
                # If we're popping an ELSE marker, we're leaving the ELSE block
                if isinstance(popped[1], ElseCommand):
                    in_else_block = False
                    else_if_command = None

            # Parse the command starting from first_col
            command_name = self.grid[row_idx][first_col].strip().upper()
            args = []

            # Collect arguments from subsequent cells in the same row
            for col_idx in range(first_col + 1, len(self.grid[row_idx])):
                arg_text = self.grid[row_idx][col_idx].strip()
                if arg_text:
                    # Stop if we hit another command (but ELSE is not a stopper)
                    if arg_text.upper() != "ELSE" and CommandRegistry.get_command_class(
                        arg_text.upper()
                    ):
                        break
                    args.append(arg_text)

            # Create the command
            command = CommandRegistry.create_command(
                command_name, args, GridPosition(row_idx, first_col)
            )

            if not command:
                raise ValueError(
                    f"Unknown command '{command_name}' at position ({row_idx}, {first_col})"
                )

            # Handle ELSE command specially
            if isinstance(command, ElseCommand):
                # Find the matching IF command
                found_if = False
                for i in range(len(stack) - 1, -1, -1):
                    if isinstance(stack[i][1], IfCommand):
                        else_if_command = cast(IfCommand, stack[i][1])
                        in_else_block = True
                        found_if = True
                        # Push ELSE marker onto stack
                        stack.append((first_col, command))
                        break

                if not found_if:
                    raise ValueError(
                        f"ELSE without matching IF at position ({row_idx}, {first_col})"
                    )
                continue  # Don't add ELSE as a command

            # Add to parent or top level
            if stack and first_col > stack[-1][0]:
                # This is nested under the previous command on the stack
                parent = stack[-1][1]
                if isinstance(parent, ElseCommand):
                    # We're in an ELSE block - add to the IF's else commands
                    if in_else_block and else_if_command:
                        else_if_command.add_else_command(command)
                else:
                    parent.add_nested_command(command)
            elif in_else_block and else_if_command and stack:
                # We're at the same level in an ELSE block - add to the IF's else commands
                else_if_command.add_else_command(command)
            else:
                # Top-level command
                commands.append(command)

            # Push onto stack if it can have nested commands
            if hasattr(command, "nested_commands"):
                stack.append((first_col, command))

        return commands

    def _extract_tokens(self) -> list[GridToken]:
        """Extract all non-empty tokens from the grid."""
        tokens = []

        for row in range(self.rows):
            for col in range(self.cols):
                text = (
                    self.grid[row][col].strip()
                    if row < len(self.grid) and col < len(self.grid[row])
                    else ""
                )
                if text:
                    tokens.append(GridToken(text, GridPosition(row, col)))

        return tokens

    def parse_with_indentation(self) -> list[Command]:
        """Parse the grid with indentation-based nesting.

        This is the more complex parser that handles nested structures.
        For now, we'll use the simple sequential parser for the tests.
        """
        # Extract all non-empty tokens with positions
        tokens = self._extract_tokens()

        # Parse tokens into commands with nesting based on indentation
        commands = self._parse_tokens_with_indentation(tokens)

        return commands

    def _parse_tokens_with_indentation(self, tokens: list[GridToken]) -> list[Command]:
        """Parse tokens into commands with proper nesting based on indentation.

        This method handles complex indentation-based nesting for control structures.
        """
        commands = []
        stack: list[tuple[int, Command]] = []  # (indentation, command)

        # Group tokens by row to determine actual indentation
        rows_dict = {}
        for token in tokens:
            if token.position.row not in rows_dict:
                rows_dict[token.position.row] = []
            rows_dict[token.position.row].append(token)

        # Process each row
        for row_num in sorted(rows_dict.keys()):
            row_tokens = sorted(rows_dict[row_num], key=lambda t: t.position.col)

            # The indentation is determined by the first token in the row
            first_token = row_tokens[0]
            indentation = first_token.position.col

            # Pop commands from stack that have higher or equal indentation
            while stack and stack[-1][0] >= indentation:
                stack.pop()

            # Process each token in the row
            for token in row_tokens:
                command = self._parse_token_command(token)

                if command:
                    # Handle ELSE command specially
                    if isinstance(command, ElseCommand):
                        # Find the matching IF command
                        if stack and isinstance(stack[-1][1], IfCommand):
                            # Skip - ELSE handling would be more complex
                            pass
                        else:
                            raise ValueError(
                                f"ELSE without matching IF at position {token.position}"
                            )
                    else:
                        # Normal command
                        if stack and indentation > 0:
                            # This command is nested under the command on top of stack
                            parent = stack[-1][1]
                            parent.add_nested_command(command)
                        else:
                            # Top-level command
                            commands.append(command)

                        # If this command can have nested commands, push it onto stack
                        if hasattr(command, "nested_commands"):
                            stack.append((indentation, command))

        return commands

    def _parse_token_command(self, token: GridToken) -> Command | None:
        """Parse a single token into a command.

        Each grid cell is a complete command. Commands that need arguments
        get default values (e.g., FORWARD defaults to moving 1 unit).
        """
        if not token:
            return None

        command_name = token.text.upper()

        # Create command using registry with no arguments
        # Commands will use their default behavior when no args provided
        command = CommandRegistry.create_command(
            command_name,
            [],  # No arguments - each cell is a complete command
            token.position,
        )

        if not command:
            raise ValueError(
                f"Unknown command '{command_name}' at position {token.position}"
            )

        return command
