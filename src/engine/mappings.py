"""
Global mappings for alternative command and value names.

This module contains mappings that allow users to use alternative names
for commands and values that get replaced with their canonical names
before parsing begins.
"""

# Global mapping dictionary for alternative names
# Key: alternative name (what users might type)
# Value: canonical name (what the parser expects)
COMMAND_MAPPINGS = {
    "mov": "move",
    "pen_on": "pen_down",
    "pen_off": "pen_up",
    "black_on": "black_detected",
    "black_off": "black_lost",
}


def preprocess_grid(grid: list[list[str]]) -> list[list[str]]:
    """
    Preprocess the grid to replace alternative names with canonical names.

    Args:
        grid: 2D list of strings representing the programming blocks

    Returns:
        New grid with mapped strings replaced with canonical names
    """
    if not grid:
        return grid

    # Create a deep copy to avoid modifying the original grid
    processed_grid = []

    for row in grid:
        processed_row = []
        for cell in row:
            if not cell or not cell.strip():
                processed_row.append(cell)
                continue

            # Get the stripped cell content for lookup
            cell_content = cell.strip().lower()

            # Check if this cell content has a mapping
            if cell_content in COMMAND_MAPPINGS:
                # Replace with canonical name, preserving original case style
                canonical = COMMAND_MAPPINGS[cell_content]

                # Preserve the case style of the original:
                # If original was all caps, make canonical all caps
                # If original was title case, make canonical title case
                # Otherwise use canonical as-is
                if cell.strip().isupper():
                    processed_cell = canonical.upper()
                elif cell.strip().istitle():
                    processed_cell = canonical.title()
                else:
                    processed_cell = canonical

                # Preserve any whitespace padding from original cell
                leading_space = len(cell) - len(cell.lstrip())
                trailing_space = len(cell) - len(cell.rstrip())
                processed_cell = (
                    (" " * leading_space) + processed_cell + (" " * trailing_space)
                )

                processed_row.append(processed_cell)
            else:
                # No mapping found, keep original
                processed_row.append(cell)

        processed_grid.append(processed_row)

    return processed_grid


def add_mapping(alternative: str, canonical: str) -> None:
    """
    Add a new mapping at runtime.

    Args:
        alternative: The alternative name users might type
        canonical: The canonical name the parser expects
    """
    COMMAND_MAPPINGS[alternative.lower()] = canonical.lower()


def get_mappings() -> dict[str, str]:
    """
    Get a copy of all current mappings.

    Returns:
        Dictionary of all current mappings
    """
    return COMMAND_MAPPINGS.copy()


def remove_mapping(alternative: str) -> bool:
    """
    Remove a mapping.

    Args:
        alternative: The alternative name to remove

    Returns:
        True if mapping was removed, False if it didn't exist
    """
    alternative_lower = alternative.lower()
    if alternative_lower in COMMAND_MAPPINGS:
        del COMMAND_MAPPINGS[alternative_lower]
        return True
    return False
