# TinkerBlocks RPI - Physical Programming Block Recognition & Robot Control

## Overview

TinkerBlocks RPI is a comprehensive system that recognizes physical programming blocks and controls real robots through an interpreter pattern. The system captures images of blocks arranged on a grid, performs AI-powered OCR to read commands, maps them directly to a 16x10 grid, and executes the resulting program either in simulation or on actual hardware via API integration.

## 🎯 Purpose

An educational tool for teaching programming concepts through physical blocks with real robot control:
1. **Capture**: Camera captures image of arranged blocks
2. **Process**: Image rotation and perspective transformation  
3. **Recognize**: AI-powered OCR extracts text/commands from blocks with direct grid mapping
4. **Execute**: Interpreter runs commands either in simulation or controls actual ESP32 car hardware

## 🤖 Hardware Integration

### Real Robot Control
- **ESP32 Car API**: Direct HTTP API integration for movement, rotation, and sensors
- **Movement Control**: Precise distance-based movement with gyroscope correction
- **Sensor Integration**: Ultrasonic distance, IR line detection, obstacle avoidance
- **Drawing Control**: Servo-controlled pen for physical drawing
- **Real-time Feedback**: Live sensor readings and execution status

### Development & Testing  
- **Mock Hardware**: Complete simulation for development and testing
- **Movement Tracking**: Comprehensive logging of all robot actions
- **Error Handling**: Graceful degradation when hardware is unavailable
- **Dual Mode**: Switch between simulation and real hardware seamlessly

## 🏗️ Architecture

The project follows clean architecture with three main modules plus hardware integration:

### [Core Module](src/core/README.md)
Foundational infrastructure and external interfaces:
- WebSocket server for real-time communication with CLI output
- Process controller for workflow management
- **Car API Client**: HTTP client for ESP32 robot communication
- **Enhanced Logging System**: Smart message routing with DEBUG/INFO/SUCCESS/WARNING/ERROR levels
- Centralized configuration and logging

### [Vision Module](src/vision/README.md)
Computer vision and AI-powered image processing:
- Image capture and manipulation with timestamped file organization
- Grid detection with perspective transformation and rectification
- AI-powered OCR processing with direct grid mapping
- Comprehensive timing measurements and file tracking

### [Engine Module](src/engine/README.md)
Interpreter pattern implementation with hardware control:
- Command definitions and registry
- Execution state management with real robot control
- **Hardware Interface**: Abstraction for real vs. mock hardware
- Grid command interpretation with sensor integration
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

# Set up environment variables
# For OCR
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
# For Car API
export CAR_API_URL="your-car-api-url" # from ESP32 car

# Activate environment
poetry shell
```

### Running the Application
```bash
python src/main.py
```

The WebSocket server starts on `ws://0.0.0.0:8765` with real-time console output.

### Available Workflows

Send JSON commands to the WebSocket server (with enhanced logging for debugging):

```json
// Run complete pipeline with real hardware (OCR → Engine → Robot)
{"command": "run", "params": {"workflow": "full", "use_hardware": true}}

// Run complete pipeline in simulation mode
{"command": "run", "params": {"workflow": "full", "use_hardware": false}}

// Run OCR only with AI-powered processing
{"command": "run", "params": {"workflow": "ocr_grid"}}

// Run OCR with automatic engine execution on real hardware
{"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true, "use_hardware": true}}

// Run engine with custom grid on real hardware
{"command": "run", "params": {"workflow": "engine", "use_hardware": true, "grid": [["MOVE", "10"], ["TURN", "RIGHT"]]}}

// Test robot movement directly
{"command": "run", "params": {"workflow": "engine", "use_hardware": true, "grid": [["PEN_DOWN"], ["LOOP", "4"], ["", "MOVE", "5"], ["", "TURN", "RIGHT"], ["PEN_UP"]]}}

// Stop current process
{"command": "stop"}
```

### Configuration

Configure the robot connection in `src/core/config.py`:
```python
# Car API settings  
car_api_url: str = "http://192.168.1.100"  # Your ESP32 IP
car_api_timeout: float = 15.0              # Request timeout
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
# Run all tests (with enhanced logging for debugging)
poetry run pytest

# Run with coverage
poetry run pytest --cov=core --cov=vision --cov=engine --cov-report=html

# Run specific test categories
poetry run pytest src/core/tests/              # Core unit tests
poetry run pytest src/vision/tests/            # Vision unit tests  
poetry run pytest src/engine/tests/            # Engine unit tests
poetry run pytest src/tests/                   # E2E and integration tests

# Run specific test file with verbose debugging
poetry run pytest src/tests/test_e2e_workflows.py -v

# Run tests matching pattern
poetry run pytest -k "websocket" -v
```

### Demo Scripts
The `src/tests/` directory contains comprehensive demo scripts:
- `demo_hardware_api.py` - **Hardware integration showcase** with real vs. mock examples
- `demo_engine_workflow.py` - Demonstrates engine execution with sample grid  
- `demo_param_handling.py` - Tests WebSocket parameter handling
- Other utility scripts for manual testing

#### Hardware Demo
Run the hardware integration demo to see all features:
```bash
python src/tests/demo_hardware_api.py
```

This demonstrates:
- Mock vs. real hardware execution
- Movement tracking and logging
- Sensor-based programming (obstacle avoidance, line following)
- Error handling and graceful degradation
- API configuration examples

## 🔧 Configuration

Edit `core/config.py` for system settings:
- **Robot API**: ESP32 car IP address and timeout settings
- **Server Settings**: WebSocket and camera server IPs and ports  
- **Grid Detection**: Corner coordinates and dimensions
- **AI Models**: LLM model settings for OCR
- **File Paths**: Output and asset directories

### Hardware Setup
1. **ESP32 Car**: Ensure your robot is connected to the same network
2. **IP Configuration**: Update `car_api_url` with your robot's IP address
3. **Network Testing**: Verify connectivity with `ping` or browser test
4. **API Testing**: Use the demo script to test hardware integration

## 📚 Module Documentation

For detailed information about each module:
- **[Core Module Documentation](src/core/README.md)** - Infrastructure and architecture
- **[Vision Module Documentation](src/vision/README.md)** - AI-powered image processing pipeline
- **[Engine Module Documentation](src/engine/README.md)** - Command interpreter system

## 🛠️ Key Technologies

- **Python 3.13** - Core language with modern async features
- **OpenCV** - Computer vision and image processing
- **LangChain** - AI model integration for OCR
- **OpenAI GPT-4V/Claude** - Vision-capable AI models
- **HTTP/REST API** - ESP32 robot communication
- **WebSockets** - Real-time bidirectional communication with smart log routing
- **asyncio** - Asynchronous programming for concurrent operations
- **requests** - HTTP client for robot API integration
- **Poetry** - Dependency management and virtual environments
- **Pydantic** - Data validation and structured output
- **pytest** - Comprehensive testing framework

## 🎮 Command Reference

The engine supports a comprehensive set of commands for programming:

### Movement Commands
- **`MOVE`** - Move forward or backward
  - `MOVE` → Move 999cm forward (effectively "move until obstacle")
  - `MOVE | 5` → Move 5cm forward
  - `MOVE | -3` → Move 3cm backward

### Rotation Commands
- **`TURN`** - Rotate the car (requires LEFT, RIGHT, or degrees)
  - `TURN | LEFT` → Turn 90° left
  - `TURN | RIGHT` → Turn 90° right
  - `TURN | 45` → Turn 45° right (positive = right, negative = left)
  - `TURN | LEFT | 30` → Turn left by 30°
  - `TURN | RIGHT | 45` → Turn right by 45°

### Control Flow
- **`LOOP`** - Repeat nested commands a specified number of times
  - `LOOP | 5` → Repeat 5 times
  - `LOOP | TRUE` → Infinite loop (until max steps)
  - `LOOP | FALSE` → No execution
  
- **`WHILE`** - Repeat nested commands while a condition is true
  - `WHILE | condition` → Loop while condition is true
  
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

- **Visual Output**: Real-time execution visualization and robot tracking
- **Block Designer**: Tool for creating custom programming blocks
- **Multi-robot Support**: Control multiple robots simultaneously
- **Web Interface**: Browser-based control panel with live video feed
- **Advanced Sensors**: Camera vision, GPS, accelerometer integration
- **Program Storage**: Save, load, and share programming sequences
- **Debugging Tools**: Step-through execution, breakpoints, variable inspection
- **Extended Math**: More mathematical operations and functions
- **Cloud Integration**: Remote robot control and collaborative programming
