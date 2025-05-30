# TinkerBlocks RPI - Visual Programming Block Recognition System

## Overview

TinkerBlocks RPI is a computer vision system designed to recognize and digitize physical programming blocks arranged on a grid. The system uses a camera (potentially on a Raspberry Pi) to capture images of physical blocks, performs Optical Character Recognition (OCR) to read text on the blocks, and maps them to a 16x10 grid structure.

## 🎯 Purpose

This project appears to be part of a visual programming education system where users can arrange physical blocks on a surface, and the system will:
1. Capture an image of the arranged blocks
2. Detect and read text/numbers on each block using OCR
3. Map the blocks to their positions in a predefined grid
4. Process the arrangement (potentially for code interpretation)

## 🏗️ Architecture

The project follows a clean architecture with proper dependency inversion:

### Core Components

1. **Core Module** (`core/`)
   - **WebSocket Server** (`ws_server.py`): Handles real-time communication with command processor support
   - **Process Controller** (`process_controller.py`): Class-based task execution with cancellation support
   - **Configuration** (`config.py`): Centralized settings
   - **No dependencies on other modules** - defines interfaces only

2. **Vision Module** (`vision/`)
   - **Image Processing** (`image.py`): Image manipulation utilities
   - **Camera Capture** (`capture/`): Camera interaction components
   - **Grid Detection** (`grid/`): Perspective transformation and mapping
   - **OCR Processing** (`ocr/`): Text recognition
   - **Tasks** (`tasks.py`): Individual vision processing tasks

3. **Main Application** (`main.py`)
   - Handles command logic (run, stop, etc.)
   - Composes vision tasks into workflows
   - Registers command processor with WebSocket server
   - Initializes the ProcessController

### ProcessController System

The application uses a simple workflow-based execution system:

```python
# Define a workflow function
async def my_workflow(send_message, check_cancelled):
    await send_message("Starting workflow...")
    
    # Check cancellation at key points
    if check_cancelled():
        return
        
    # Do work...
    await send_message("Workflow complete!")

# Execute the workflow
controller = ProcessController(broadcast)
await controller.run_workflow(my_workflow, "My Workflow")
```

Key features:
- **Simple Workflows**: Single function contains entire workflow logic
- **Cancellation Points**: Check for cancellation where it makes sense
- **Clear Progress**: Send messages to update status
- **Easy to Write**: No complex task composition needed

This design ensures:
- Minimal complexity - just async functions
- Natural flow - write code as you normally would
- Flexible cancellation - check where appropriate
- Easy debugging - all logic in one place

## 📁 Project Structure

```
tinker-blocks-rpi/
├── core/                      # Core application logic
│   ├── __init__.py
│   ├── ws_server.py          # WebSocket server implementation
│   ├── process_controller.py # Process workflow controller
│   └── config.py             # Centralized configuration
├── vision/                    # Computer vision and image processing
│   ├── __init__.py
│   ├── image.py              # Image manipulation utilities
│   ├── capture/              # Camera capture modules
│   │   ├── __init__.py
│   │   ├── client.py         # Remote camera client
│   │   ├── server.py         # Camera server for Raspberry Pi
│   │   └── local.py          # Local camera capture
│   ├── grid/                 # Grid detection and mapping
│   │   ├── __init__.py
│   │   ├── perspective.py    # Perspective transformation
│   │   ├── square.py         # Grid square representation
│   │   └── mapper.py         # OCR to grid mapping (OCR2Grid)
│   └── ocr/                  # OCR processing
│       ├── __init__.py
│       ├── wrapper.py        # EasyOCR wrapper
│       ├── client.py         # OCR client
│       └── server.py         # OCR server
├── scripts/                   # Standalone scripts and utilities
│   ├── test_ocr.py           # PyTesseract OCR testing
│   └── test_number_detection.py  # Number detection testing
├── assets/                    # Image assets and captures
├── output/                    # Processed output files
├── main.py                    # Application entry point
├── pyproject.toml            # Poetry configuration
├── poetry.lock               # Locked dependencies
└── README.md                 # This file
```

## 🛠️ Technologies Used

- **Python 3.13+**
- **OpenCV** - Computer vision and image processing
- **NumPy** - Numerical computing
- **Pydantic** - Data validation and settings management
- **WebSockets** - Real-time communication
- **Flask** - Web framework for camera and OCR servers
- **Requests** - HTTP client library
- **EasyOCR** - Primary OCR engine
- **PyTesseract** - Alternative OCR engine
- **Tabulate** - Grid visualization in terminal
- **DepthAI** - OAK-D camera support
- **asyncio** - Asynchronous programming
- **Poetry** - Dependency management

## 🚀 Getting Started

### Prerequisites

1. Python 3.13 or higher
2. Poetry package manager
3. Access to a camera (local or remote Raspberry Pi)

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd tinker-blocks-rpi
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Configuration

All configuration settings are now centralized in `core/config.py`. You can modify the following settings:

- **Server IPs and Ports**: 
  - WebSocket server: `websocket_host` and `websocket_port`
  - Camera server: `camera_server_ip` and `camera_server_port`
  - OCR server: `ocr_server_ip` and `ocr_server_port`

- **Grid Detection**: 
  - Corner points: `grid_corners` (currently hardcoded for specific setup)
  - Grid dimensions: `grid_rows` and `grid_cols`

- **Directories**:
  - Output directory: `output_dir`
  - Assets directory: `assets_dir`

Example of updating configuration:
```python
from core.config import config

# Update camera server IP
config.camera_server_ip = "192.168.1.100"
```

### Running the Application

1. Start the WebSocket server:
   ```bash
   python main.py
   ```

2. The server will start on `ws://0.0.0.0:8765`

3. Connect a WebSocket client and send commands:
   - `{"command": "run"}` - Run the vision processing workflow
   - `{"command": "stop"}` - Stop the current process

## 🔄 Processing Workflow

The vision processing workflow consists of these tasks:

1. **Capture Image**: Get image from camera or use test image
2. **Process Image**: Rotate 90 degrees and convert to grayscale
3. **Create Grid**: Apply perspective transformation and detect grid
4. **Run OCR**: Extract text from the image using EasyOCR
5. **Map to Grid**: Map detected text to grid positions (16x10)

Each task:
- Can be cancelled between execution
- Reports progress via WebSocket messages
- Shares state with subsequent tasks
- Handles errors gracefully

## 🔧 Troubleshooting

### Poetry Installation Issues

If you encounter the error "No file/folder found for package tinker-blocks-rpi", this has been fixed by setting `package-mode = false` in `pyproject.toml`. The project is an application, not a distributable package.

### Dependency Installation

After updating dependencies, you may need to:
```bash
poetry lock --no-update  # Update lock file with new dependencies
poetry install           # Install all dependencies
```

### System Dependencies

Some dependencies require system packages:
- **PyTesseract**: Requires Tesseract OCR to be installed
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`
- **DepthAI**: May require additional USB permissions on Linux

## 🎮 Use Cases

- **Educational Programming**: Teaching programming concepts using physical blocks
- **Visual Code Creation**: Creating programs by arranging physical blocks
- **Interactive Learning**: Hands-on programming experience for students
- **Block-based Programming**: Similar to Scratch but with physical blocks

## 🔮 Future Enhancements

- **Block Interpreter**: Execute arranged blocks as programs
- **Multiple Workflows**: Support different processing pipelines
- **Real-time Feedback**: Live updates as blocks are arranged
- **Block Types**: Support for different block categories (loops, conditions, etc.)
- **Remote Control**: Web interface for system control

## 📝 Notes

- The system uses hardcoded corner coordinates for grid detection
- Vision tasks share state via a module-level dictionary
- ProcessController supports cancellation between tasks
- WebSocket server uses a command processor pattern
