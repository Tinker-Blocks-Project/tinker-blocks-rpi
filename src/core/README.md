# Core Module

The core module provides the foundational infrastructure for the TinkerBlocks system. It implements the WebSocket server, process control, and configuration management with zero dependencies on other modules.

## 📁 Module Structure

```
core/
├── __init__.py             # Module exports
├── ws_server.py            # WebSocket server implementation
├── process_controller.py   # Workflow execution controller
└── config.py               # Centralized configuration
```

## 🔧 Key Components

### WebSocket Server (`ws_server.py`)

Real-time bidirectional communication server:
- **Broadcast Support**: Send messages to all connected clients
- **Command Processing**: Extensible command handler registration
- **Connection Management**: Track active connections
- **JSON Protocol**: Command/response messaging

```python
from core import start_ws_server, broadcast, set_command_processor

# Register command handler
async def process_command(command: str, params: dict):
    if command == "run":
        await broadcast("Starting process...")

set_command_processor(process_command)

# Start server
server = await start_ws_server()
```

### Process Controller (`process_controller.py`)

Manages workflow execution with cancellation support:
- **Generic Workflows**: Support for any async function following the protocol
- **Return Values**: Workflows can return data for chaining
- **Cancellation**: Clean cancellation at any point
- **Status Updates**: Real-time progress via send_message callback

```python
from core import ProcessController

# Create controller
controller = ProcessController(broadcast)

# Define a workflow
async def my_workflow(send_message, check_cancelled):
    await send_message("Starting...")
    
    if check_cancelled():
        return None
        
    # Do work and return result
    return {"status": "complete", "data": [1, 2, 3]}

# Run workflow
success, result = await controller.run_workflow(my_workflow, "My Task")
```

### Configuration (`config.py`)

Centralized settings using Pydantic:
- **Server Configuration**: IPs, ports for all services
- **Grid Settings**: Dimensions and corner points
- **Directory Paths**: Output and asset directories
- **Type Safety**: Validated configuration with defaults

```python
from core.config import config

# Access settings
print(config.websocket_port)  # 8765
print(config.grid_rows)       # 10
print(config.grid_cols)       # 16

# Settings are immutable by default
```

## 🏗️ Design Principles

### Dependency Inversion
The core module defines interfaces without depending on implementations:
- Workflow protocol for process execution
- Command processor registration
- Message broadcasting interface

### Clean Architecture
- **No circular dependencies**: Core has zero imports from other modules
- **Protocol-based**: Uses Python protocols for extensibility
- **Async-first**: Built on asyncio for concurrent operations

## 🔄 Workflow Protocol

Workflows follow a simple async function signature:

```python
from typing import Callable, Awaitable, TypeVar

T = TypeVar('T')

async def workflow(
    send_message: Callable[[str], Awaitable[None]],
    check_cancelled: Callable[[], bool]
) -> T:
    """
    Args:
        send_message: Async function to send status updates
        check_cancelled: Function to check if cancelled
    
    Returns:
        Any data to pass to next workflow or None
    """
    pass
```

## 🔌 WebSocket Protocol

Messages follow JSON format:

**Client → Server:**
```json
{
    "command": "run",
    "params": {
        "workflow": "ocr_grid",
        "chain_engine": true
    }
}
```

The `params` field is optional. If omitted, an empty object `{}` is passed to the command handler.

**Server → Client:**
```json
{
    "type": "status",
    "message": "Processing image..."
}
```

### Command Examples

```json
// Simple command without parameters
{"command": "stop"}

// Command with parameters
{"command": "run", "params": {"workflow": "full"}}

// Complex parameters
{
    "command": "run",
    "params": {
        "workflow": "engine",
        "grid": [["FORWARD", "RIGHT"], ["LEFT", "FORWARD"]]
    }
}
```

## 📡 Server Configuration

Default settings in `config.py`:
- **WebSocket**: `ws://0.0.0.0:8765`
- **Camera Server**: `http://raspberrypi.local:5001`
- **OCR Server**: `http://localhost:5002`

## 🧪 Testing

The core module is designed for easy testing:
- Mock send_message for workflow testing
- Simple cancelled flag for cancellation testing
- Isolated components with clear interfaces

## 🔒 Thread Safety

- WebSocket connections are managed per-client
- Broadcast function is thread-safe
- Process controller manages one workflow at a time

## 🎯 Usage Pattern

1. **Import core components**:
   ```python
   from core import ProcessController, broadcast, start_ws_server
   ```

2. **Create workflows** (in other modules):
   ```python
   async def my_workflow(send_message, check_cancelled):
       # Implementation
       pass
   ```

3. **Wire up in main.py**:
   ```python
   controller = ProcessController(broadcast)
   await controller.run_workflow(my_workflow, "Task Name")
   ```

## 🔮 Future Enhancements

- **Workflow Queue**: Support queuing multiple workflows
- **Parallel Execution**: Run independent workflows concurrently
- **Client Authentication**: Secure WebSocket connections
- **Metrics Collection**: Track workflow performance
- **Plugin System**: Dynamic workflow registration 