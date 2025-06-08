# TinkerBlocks RPI - Visual Programming Block Recognition System

## Overview

TinkerBlocks RPI is a computer vision system that recognizes physical programming blocks and executes them using an interpreter pattern. The system captures images of blocks arranged on a grid, performs AI-powered OCR to read commands, maps them directly to a 16x10 grid, and executes the resulting program with comprehensive timing and file tracking.

## 🎯 Purpose

An educational tool for teaching programming concepts through physical blocks:
1. **Capture**: Camera captures image of arranged blocks
2. **Process**: Image rotation and perspective transformation
3. **Recognize**: AI-powered OCR extracts text/commands from blocks with direct grid mapping
4. **Execute**: Interpreter runs the commands with visual feedback

## 🏗️ Architecture

The project follows clean architecture with three main modules:

### [Core Module](src/core/README.md)
Foundational infrastructure with zero dependencies:
- WebSocket server for real-time communication with CLI output
- Process controller for workflow management
- Centralized configuration

### [Vision Module](src/vision/README.md)
Computer vision and AI-powered image processing:
- Image capture and manipulation with timestamped file organization
- Grid detection with perspective transformation and rectification
- AI-powered OCR processing with direct grid mapping
- Comprehensive timing measurements and file tracking

### [Engine Module](src/engine/README.md)
Interpreter pattern implementation:
- Command definitions and registry
- Execution state management
- Grid command interpretation
- Extensible command system

## 📁 Project Structure

```
tinker-blocks-rpi/
├── src/                 # Source code
│   ├── core/           # Core infrastructure
│   │   ├── tests/      # Core module tests
│   │   └── README.md   # Core documentation
│   ├── vision/         # Computer vision & AI-powered OCR
│   │   ├── capture/    # Camera components
│   │   ├── grid/       # Grid detection & perspective transformation
│   │   ├── ocr/        # AI-powered OCR with unified interface
│   │   ├── tests/      # Vision module tests
│   │   └── README.md   # Vision documentation
│   ├── engine/         # Command interpreter
│   │   ├── tests/      # Engine module tests
│   │   └── README.md   # Engine documentation
│   ├── tests/          # End-to-end and integration tests
│   │   ├── test_e2e_workflows.py
│   │   ├── test_integration_websocket.py
│   │   ├── test_workflow_chaining.py
│   │   ├── test_error_scenarios.py
│   │   └── demo_*.py   # Demo scripts
│   ├── main.py         # Application entry point
│   └── conftest.py     # Pytest configuration
├── assets/              # Image assets
├── output/              # Generated outputs (timestamped folders)
├── pyproject.toml       # Poetry configuration
├── poetry.lock          # Locked dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Poetry package manager
- Camera (local or remote Raspberry Pi)
- API key for LLM for AI-powered OCR

### Installation
```bash
# Clone repository
git clone [repository-url]
cd tinker-blocks-rpi

# Install dependencies
poetry install

# Set up environment variables (for AI OCR)
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"

# Activate environment
poetry shell
```

### Running the Application
```bash
python src/main.py
```

The WebSocket server starts on `ws://0.0.0.0:8765` with real-time console output.

### Available Workflows

Send JSON commands to the WebSocket server:

```json
// Run complete pipeline (OCR → Engine)
{"command": "run", "params": {"workflow": "full"}}

// Run OCR only with AI-powered processing
{"command": "run", "params": {"workflow": "ocr_grid"}}

// Run OCR with automatic engine execution
{"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true}}

// Run engine with custom grid
{"command": "run", "params": {"workflow": "engine", "grid": [["FWD", "RIGHT"], ...]}}

// Stop current process
{"command": "stop"}
```

### Output Structure

Each workflow run creates a timestamped folder with comprehensive output:

```
output/20250608_221634/
├── rotated_original.jpg     # Original image after rotation
├── grid_overlay.jpg         # Grid visualization
├── transformed_grid.jpg     # Perspective-corrected image
└── grid_result.json         # Complete grid data with metadata
```

## 🧪 Testing

The project has comprehensive test coverage organized by module and test type:

### Unit Tests
Located within each module:
- `src/core/tests/` - Core infrastructure tests
- `src/vision/tests/` - Vision processing tests  
- `src/engine/tests/` - Engine interpreter tests

### End-to-End Tests
Located in `src/tests/` directory:
- `test_e2e_workflows.py` - Complete workflow execution tests
- `test_integration_websocket.py` - WebSocket server integration
- `test_workflow_chaining.py` - Workflow data passing and chaining
- `test_error_scenarios.py` - Error handling and edge cases

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=core --cov=vision --cov=engine --cov-report=html

# Run specific test categories
poetry run pytest src/core/tests/              # Core unit tests
poetry run pytest src/vision/tests/            # Vision unit tests  
poetry run pytest src/engine/tests/            # Engine unit tests
poetry run pytest src/tests/                   # E2E and integration tests

# Run specific test file
poetry run pytest src/tests/test_e2e_workflows.py -v

# Run tests matching pattern
poetry run pytest -k "websocket" -v
```

### Demo Scripts
The `src/tests/` directory also contains demo scripts:
- `demo_engine_workflow.py` - Demonstrates engine execution with sample grid
- `demo_param_handling.py` - Tests WebSocket parameter handling
- Other utility scripts for manual testing

## 🔧 Configuration

Edit `core/config.py` for system settings:
- Server IPs and ports
- Grid dimensions and corner coordinates
- Directory paths
- LLM model settings

## 📚 Module Documentation

For detailed information about each module:
- **[Core Module Documentation](src/core/README.md)** - Infrastructure and architecture
- **[Vision Module Documentation](src/vision/README.md)** - AI-powered image processing pipeline
- **[Engine Module Documentation](src/engine/README.md)** - Command interpreter system

## 🛠️ Key Technologies

- **Python 3.13** - Core language
- **OpenCV** - Computer vision and image processing
- **LangChain** - AI model integration for OCR
- **OpenAI GPT-4V/Claude** - Vision-capable AI models
- **WebSockets** - Real-time communication with console output
- **asyncio** - Asynchronous programming
- **Poetry** - Dependency management
- **Pydantic** - Data validation and structured output

## 🎮 Command Reference

The engine supports a comprehensive set of commands for programming:

### Movement Commands
- **`MOVE`** - Move forward 1 unit (default) or specified distance
  - `MOVE` → Move 1 unit forward
  - `MOVE | 5` → Move 5 units forward
  - `MOVE | -3` → Move 3 units backward
  - `MOVE | WHILE | condition` → Move while condition is true

### Rotation Commands
- **`TURN`** - Rotate the car (requires LEFT, RIGHT, or degrees)
  - `TURN | LEFT` → Turn 90° left
  - `TURN | RIGHT` → Turn 90° right
  - `TURN | 45` → Turn 45° right (positive = right, negative = left)
  - `TURN | LEFT | 30` → Turn left by 30°
  - `TURN | RIGHT | 45` → Turn right by 45°
  - `TURN | LEFT | WHILE | condition` → Turn left while condition is true

### Control Flow
- **`LOOP`** - Repeat nested commands
  - `LOOP | 5` → Repeat 5 times
  - `LOOP | TRUE` → Infinite loop (until max steps)
  - `LOOP | FALSE` → No execution
  - `LOOP | WHILE | condition` → Loop while condition is true
  
- **`IF`** - Conditional execution
  - `IF | condition` → Execute nested commands if true
  - Can be followed by `ELSE` block for false case

### Variables
- **`SET`** - Assign values to variables
  - `SET | X | 5` → Set X to 5
  - `SET | Y | X | + | 3` → Set Y to X + 3
  - `SET | FLAG | TRUE` → Set boolean variable
  - `SET | COUNTER | 0` → Variable names can be any alphabetic string

### Drawing
- **`PEN_DOWN`** - Start drawing path
- **`PEN_UP`** - Stop drawing path

### Utility
- **`WAIT`** - Pause execution
  - `WAIT | 2` → Wait 2 seconds
  - `WAIT | 0.5` → Wait 0.5 seconds
  - `WAIT | WHILE | condition` → Wait while condition is true

### Values and Expressions
- **Numbers**: `5`, `3.14`, `-2`
- **Booleans**: `TRUE`, `FALSE`
- **Variables**: Any alphabetic string (e.g., `X`, `COUNT`, `DISTANCE_VAR`)
- **Sensors**: `DISTANCE`, `OBSTACLE`, `BLACK_DETECTED`, `BLACK_LOST`
- **Operators**: `+`, `-`, `*`, `/`, `<`, `>`, `=`, `!=`, `AND`, `OR`, `NOT`

### Grid Layout
Commands are arranged on a 16x10 grid:
- Read left-to-right, top-to-bottom
- Arguments separated by `|` in cells
- Indentation (column > 0) creates nested blocks for loops/conditions

## 🔮 Future Enhancements

- **Visual Output**: Real-time execution visualization
- **Block Designer**: Tool for creating custom blocks
- **Multi-grid Support**: Connect multiple grids for larger programs
- **Web Interface**: Browser-based control panel
- **Hardware Integration**: Direct GPIO control for motors and sensors
- **Program Storage**: Save and load programs
- **Debugging Tools**: Step-through execution, breakpoints
- **Extended Math**: More mathematical operations and functions

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]
