# Vision Module

The vision module handles all computer vision and image processing tasks for the TinkerBlocks system. It captures images of physical programming blocks, performs AI-powered OCR using Large Language Models, and directly maps text to a grid structure with comprehensive timing and file tracking.

## 📁 Module Structure

```
vision/
├── __init__.py           # Module exports (Image, Grid)
├── types.py              # Core types (Image, Grid) 
├── workflow.py           # OCR grid processing workflow with timing
├── capture/              # Camera capture components
│   ├── __init__.py
│   ├── client.py         # Remote camera client
│   ├── server.py         # Camera server for Raspberry Pi
│   └── local.py          # Local camera capture
├── grid/                 # Grid detection and perspective transformation
│   ├── __init__.py
│   ├── perspective.py    # Perspective transformation with rectification
│   └── square.py         # Grid square representation (legacy)
└── ocr/                  # AI-powered OCR with unified interface
    ├── __init__.py
    ├── protocol.py       # OCRProtocol interface definition
    ├── vlm_ocr.py        # AI-powered OCR with direct grid mapping
    ├── client.py         # OCR client for distributed processing
    └── server.py         # OCR server template
```

## 🔧 Key Components

### Unified OCR Interface (`ocr/protocol.py`)
- `OCRProtocol`: Defines a common interface for all OCR implementations
- Ensures consistent API across different OCR engines
- Supports async processing with direct Grid output

### AI-Powered OCR (`ocr/vlm_ocr.py`)  
- `VLM_OCR`: Uses Large Language Models with vision capabilities (GPT-4V, Claude, etc.)
- Direct grid mapping - no separate coordinate mapping needed
- Structured output with position validation using Pydantic
- Works with any LangChain-compatible vision model
- Clean error handling without debug output

### Image Processing (`types.py`)
- `Image` class for loading, manipulating and saving images
- Supports rotation, grayscale conversion, and OpenCV integration
- `Grid` class for structured 2D text layout representation

### Grid Detection (`grid/perspective.py`)
- **PerspectiveGrid**: Applies perspective transformation to detect and rectify grids
- **`apply_perspective_transform()`**: Creates rectified grid images for better OCR accuracy
- **GridSquare**: Represents individual grid cells (legacy support)

## 🔄 OCR Grid Workflow

The main workflow uses the unified interface and AI-powered OCR with comprehensive file tracking:

### Workflow Steps:
1. **Capture Image**: Get image from camera or use test image  
2. **Process Image**: Rotate 90° clockwise, save rotated original, convert to grayscale
3. **Apply Perspective Transform**: Create rectified grid image using perspective transformation
4. **Run AI OCR**: Extract text and directly map to grid positions using VLM_OCR
5. **Save Results**: Generate JSON output with metadata and timing information
6. **Return Grid**: Structured Grid object with 2D text layout

### File Output Structure:

Each workflow run creates a timestamped folder:

```
output/20250608_221634/
├── rotated_original.jpg     # Original image after 90° rotation
├── grid_overlay.jpg         # Grid visualization on grayscale image  
├── transformed_grid.jpg     # Perspective-corrected image for OCR
└── grid_result.json         # Complete grid data with metadata
```

### Usage Example:

```python
from langchain_openai import ChatOpenAI
from vision.ocr import VLM_OCR
from vision.workflow import ocr_grid_workflow

# Initialize AI-powered OCR
chat_model = ChatOpenAI(model="gpt-4o-mini")
ocr_engine = VLM_OCR(chat_model)

# Run workflow
grid_result = await ocr_grid_workflow(
    ocr_engine=ocr_engine,
    send_message=send_message_func,
)

# Access results
for row in grid_result.blocks:
    print(row)  # List of strings for each row
```

## 📊 Grid Configuration

The grid system uses perspective transformation with corner points defined in `core.config`:

```python
grid_corners = {
    "top_left": (85, 88),
    "top_right": (575, 75), 
    "bottom_left": (90, 420),
    "bottom_right": (580, 415)
}
```

Default grid size: 16 rows × 10 columns

## 🔌 OCR Implementation

### VLM_OCR
- AI-powered with vision models (GPT-4V, Claude, Gemini, etc.)
- Direct grid position mapping with structured output
- High accuracy for structured layouts
- No separate coordinate mapping needed
- Robust error handling

### Custom OCR
Implement the `OCRProtocol` interface:

```python
from vision.ocr import OCRProtocol
from vision.types import Grid

class CustomOCR:
    async def process_image(self, image_path: str) -> Grid:
        # Your OCR implementation
        return Grid(blocks=your_2d_text_array)
```

## 🛠️ Dependencies

- **OpenCV**: Core image processing and computer vision
- **NumPy**: Array operations and numerical processing
- **LangChain**: AI model integration and structured output
- **Pydantic**: Data validation and structured output
- **OpenAI/Anthropic**: AI model providers for vision capabilities

## 🎯 Key Features

1. **Unified Interface**: All OCR engines use the same `OCRProtocol`
2. **AI Integration**: VLM_OCR provides superior accuracy for grid layouts
3. **Direct Mapping**: No separate coordinate mapping step needed
4. **Perspective Rectification**: Grid images are rectified before OCR for better accuracy
5. **Type Safety**: Strong typing with Pydantic models
6. **Clean Architecture**: Professional error handling without debug prints
7. **File Organization**: Timestamped folders with descriptive file names
8. **Performance Monitoring**: Detailed timing for optimization
9. **Comprehensive Output**: Visual and structured data outputs

## 📝 Grid Result JSON Structure

The workflow generates a comprehensive JSON file with metadata:

```json
{
  "timestamp": "20250608_221634",
  "blocks": [
    ["loop", "inf", "", ""],
    ["mov", "right", "", ""],
    ["if", "block", "", ""]
  ],
  "non_empty_cells": 6,
  "grid_dimensions": {
    "rows": 16,
    "cols": 10
  }
}
```

## 🔄 Messaging System

The vision module integrates with the core messaging system:
- All workflow progress sent via `send_message()` function
- Messages appear in both WebSocket clients and console output
- Professional, clean output without debug prints
- Detailed file and timing reporting

## 🚀 Recent Improvements

- **Removed EasyOCR dependencies**: Simplified to AI-only approach
- **Eliminated OCR2Grid mapper**: Direct grid mapping in VLM_OCR
- **Clean messaging**: All output goes through proper message channels
- **File organization**: Timestamped folders instead of prefixed files
- **Performance tracking**: Detailed timing measurements
- **Professional code**: Removed all debug prints and temporary code 