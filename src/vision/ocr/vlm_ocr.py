import base64
from pydantic import Field, BaseModel
from langchain.chat_models.base import BaseChatModel
from core.config import config
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import cv2
from typing import Annotated
from vision.types import Grid


class Block(BaseModel):
    row: Annotated[
        int, Field(ge=0, le=config.grid_rows - 1), "0-indexed row number of the block"
    ]
    col: Annotated[
        int,
        Field(ge=0, le=config.grid_cols - 1),
        "0-indexed column number of the block",
    ]
    text: Annotated[
        str,
        Field(min_length=1, max_length=10),
        "Exact text of the block without changes",
    ]


class OCRResponse(BaseModel):
    blocks: Annotated[
        list[Block],
        "List of blocks in the grid. Each block with a row, column and text",
    ]


vlm_ocr_system_prompt = f"""
The following is a grid of {config.grid_cols} column by {config.grid_rows} row cells.
Each cell contains an arbitrary text (word, symbol, number, etc.)
Your task is to extract the visible texts and map them to rows and columns.

Return a list of blocks, each block represents a cell, and contains the row, column and text.

The row and column are 0-indexed.
The text is the exact text of the cell.

Do not modify the identation or the content of the text.
"""


class VLM_OCR:
    def __init__(self, chat_model: BaseChatModel):
        self.chat_model = chat_model.with_structured_output(OCRResponse)  # type: ignore

    async def process_image(self, image_path: str) -> Grid:
        """
        Process an image and return a Grid with text mapped to positions.

        Args:
            image_path: Path to the image file to process

        Returns:
            Grid object containing the 2D text layout
        """
        # Load the image with OpenCV
        cv_image = cv2.imread(image_path)
        if cv_image is None:
            raise ValueError(f"Could not load image from path: {image_path}")

        # Encode image to base64
        _, buffer = cv2.imencode(".jpg", cv_image)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Convert the image to a base64 data URL
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        try:
            # Get OCR results from the chat model
            ocr_response: OCRResponse = await self.chat_model.ainvoke(
                ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(content=vlm_ocr_system_prompt),
                        HumanMessage(
                            content=[
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_data_url},
                                }
                            ]
                        ),
                    ]
                ).format_prompt()
            )  # type: ignore

        except Exception as e:
            # Return empty grid on error, let the workflow handle error messaging
            return Grid(
                blocks=[
                    ["" for _ in range(config.grid_cols)]
                    for _ in range(config.grid_rows)
                ]
            )

        # Create empty 2D grid
        grid_blocks = [
            ["" for _ in range(config.grid_cols)] for _ in range(config.grid_rows)
        ]

        # Fill grid with detected text
        for block in ocr_response.blocks:
            if 0 <= block.row < config.grid_rows and 0 <= block.col < config.grid_cols:
                grid_blocks[block.row][block.col] = block.text

        return Grid(blocks=grid_blocks)
