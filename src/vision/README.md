# Vision Module

The vision module handles all computer vision and image processing tasks for the TinkerBlocks system. It captures images of physical programming blocks, performs OCR, and maps text to a grid structure.

## 📁 Module Structure

```
vision/
├── __init__.py           # Module exports
├── image.py              # Image manipulation utilities
├── workflow.py           # OCR grid processing workflow
├── capture/              # Camera capture components
│   ├── __init__.py
│   ├── client.py         # Remote camera client
│   ├── server.py         # Camera server for Raspberry Pi
│   └── local.py          # Local camera capture
├── grid/                 # Grid detection and mapping
│   ├── __init__.py
│   ├── perspective.py    # Perspective transformation
│   ├── square.py         # Grid square representation
│   └── mapper.py         # OCR to grid mapping (OCR2Grid)
└── ocr/                  # OCR processing
    ├── __init__.py
    ├── wrapper.py        # EasyOCR wrapper
    ├── client.py         # OCR client
    └── server.py         # OCR server
```

## 🔧 Key Components

### Image Processing (`image.py`)
- `Image` class for loading, manipulating and saving images
- Supports rotation, grayscale conversion, and OpenCV integration
- Example:
  ```python
  from vision import Image
  
  img = Image.from_file("photo.jpg")
  rotated = img.rotate_90_clockwise()
  gray = rotated.to_grayscale()
  gray.save("processed.jpg")
  ```

### Camera Capture (`capture/`)
- **Local**: Direct camera access via OpenCV
- **Client/Server**: Remote camera access for Raspberry Pi setups
- Configurable via `core.config`

### Grid Detection (`grid/`)
- **PerspectiveGrid**: Applies perspective transformation to detect grid
- **GridSquare**: Represents individual grid cells with boundaries
- **OCR2Grid**: Maps OCR results to grid positions
- Supports 16x10 grid (configurable)

### OCR Processing (`ocr/`)
- **EasyOCR Wrapper**: Primary OCR engine with GPU support
- **Client/Server**: Distributed OCR processing
- Returns bounding boxes and confidence scores

## 🔄 OCR Grid Workflow

The main workflow (`ocr_grid_workflow`) performs these steps:

1. **Capture Image**: Get image from camera or use test image
2. **Process Image**: Rotate 90° clockwise and convert to grayscale
3. **Create Grid**: Apply perspective transformation and detect grid squares
4. **Run OCR**: Extract text using EasyOCR
5. **Map to Grid**: Map detected text to grid positions

### Workflow Usage

```python
from vision.workflow import ocr_grid_workflow

# The workflow returns a 2D list representing the grid
grid_data = await ocr_grid_workflow(send_message, check_cancelled)
# Returns: [["FORWARD", "RIGHT", ...], ["LEFT", "", ...], ...]
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

Default grid size: 16 columns × 10 rows

## 🛠️ Dependencies

- **OpenCV**: Core image processing
- **NumPy**: Array operations
- **EasyOCR**: Text recognition
- **PyTesseract**: Alternative OCR (in scripts)
- **Tabulate**: Grid visualization
- **DepthAI**: OAK-D camera support

## 🔍 Testing & Scripts

See `scripts/` for standalone testing utilities:
- `test_ocr.py`: PyTesseract OCR testing
- `test_number_detection.py`: Number detection experiments

## 🎯 Output

The workflow produces:
1. **Grid Image**: Visualization saved to `output/grid_image.jpg`
2. **Console Output**: Grid printed using tabulate
3. **JSON Format**: Structured grid data
4. **Return Value**: 2D list of commands for further processing 