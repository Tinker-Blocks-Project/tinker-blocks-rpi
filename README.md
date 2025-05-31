# TinkerBlocks RPI - Visual Programming Block Recognition System

## Overview

TinkerBlocks RPI is a computer vision system that recognizes physical programming blocks and executes them using an interpreter pattern. The system captures images of blocks arranged on a grid, performs OCR to read commands, maps them to a 16x10 grid, and executes the resulting program.

## 🎯 Purpose

An educational tool for teaching programming concepts through physical blocks:
1. **Capture**: Camera captures image of arranged blocks
2. **Recognize**: OCR extracts text/commands from blocks
3. **Map**: Commands are mapped to grid positions
4. **Execute**: Interpreter runs the commands with visual feedback

## 🏗️ Architecture

The project follows clean architecture with three main modules:

### [Core Module](src/core/README.md)
Foundational infrastructure with zero dependencies:
- WebSocket server for real-time communication
- Process controller for workflow management
- Centralized configuration

### [Vision Module](src/vision/README.md)
Computer vision and image processing:
- Image capture and manipulation
- Grid detection with perspective transformation
- OCR processing to extract text
- Mapping text to grid positions

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
│   ├── vision/         # Computer vision
│   │   ├── capture/    # Camera components
│   │   ├── grid/       # Grid detection
│   │   ├── ocr/        # OCR processing
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
├── output/              # Generated outputs
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

### Installation
```bash
# Clone repository
git clone [repository-url]
cd tinker-blocks-rpi

# Install dependencies
poetry install

# Activate environment
poetry shell
```

### Running the Application
```bash
python src/main.py
```

The WebSocket server starts on `ws://0.0.0.0:8765`

### Available Workflows

Send JSON commands to the WebSocket server:

```json
// Run complete pipeline (OCR → Engine)
{"command": "run", "params": {"workflow": "full"}}

// Run OCR only
{"command": "run", "params": {"workflow": "ocr_grid"}}

// Run OCR with automatic engine execution
{"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true}}

// Run engine with custom grid
{"command": "run", "params": {"workflow": "engine", "grid": [["FWD", "RIGHT"], ...]}}

// Stop current process
{"command": "stop"}
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
- Grid dimensions and corners
- Directory paths

## 📚 Module Documentation

For detailed information about each module:
- **[Core Module Documentation](src/core/README.md)** - Infrastructure and architecture
- **[Vision Module Documentation](src/vision/README.md)** - Image processing pipeline
- **[Engine Module Documentation](src/engine/README.md)** - Command interpreter system

## 🛠️ Key Technologies

- **Python 3.13** - Core language
- **OpenCV** - Computer vision
- **EasyOCR** - Text recognition
- **WebSockets** - Real-time communication
- **asyncio** - Asynchronous programming
- **Poetry** - Dependency management
- **Pydantic** - Configuration validation

## 🎮 Command Reference

Built-in commands recognized by the engine:
- **Movement**: `FORWARD`, `FWD`, `MOVE_FORWARD`
- **Rotation**: `RIGHT`, `LEFT`, `TURN_RIGHT`, `TURN_LEFT`

Commands are case-insensitive and support aliases.

## 🔮 Future Enhancements

- **Advanced Commands**: Loops, conditionals, variables
- **Visual Output**: Real-time execution visualization
- **Block Designer**: Tool for creating custom blocks
- **Multi-grid Support**: Connect multiple grids
- **Web Interface**: Browser-based control panel

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]
