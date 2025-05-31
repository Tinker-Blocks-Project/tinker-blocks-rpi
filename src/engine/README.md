# Engine Module

The engine module implements an interpreter pattern for executing commands from the grid of programming blocks. It processes the 2D array of commands produced by the vision module and simulates their execution.

## 📁 Module Structure

```
engine/
├── __init__.py         # Module exports
├── commands.py         # Command definitions and registry
├── state.py            # Execution state management
├── interpreter.py      # Main interpreter implementation
└── workflow.py         # Engine workflow integration
```

## 🔧 Key Components

### Command System (`commands.py`)

The engine uses an extensible command system with:
- **Command Protocol**: Interface for all executable commands
- **Built-in Commands**:
  - `MoveForwardCommand`: Move in current direction
  - `TurnRightCommand`: Turn 90° clockwise
  - `TurnLeftCommand`: Turn 90° counter-clockwise
- **CommandRegistry**: Maps command names to implementations with aliases

Example command implementation:
```python
class MoveForwardCommand:
    name = "MOVE_FORWARD"
    
    def execute(self, state: ExecutionState) -> None:
        directions = {
            "right": (1, 0),
            "down": (0, 1),
            "left": (-1, 0),
            "up": (0, -1),
        }
        dx, dy = directions[state.direction]
        state.move(dx, dy)
```

### Execution State (`state.py`)

Manages the interpreter's state during execution:
- **Position**: Current (x, y) coordinates
- **Direction**: Current facing (right, down, left, up)
- **Variables**: Storage for future variable support
- **Output**: History of executed steps
- **Steps Count**: Total commands executed

```python
@dataclass
class ExecutionState:
    position: Position
    direction: str = "right"
    variables: Dict[str, Any]
    output: List[ExecutionStep]
    steps_executed: int
```

### Interpreter (`interpreter.py`)

The main interpreter that processes command grids:
- Executes commands sequentially from the grid
- Supports async callbacks for progress updates
- Handles cancellation gracefully
- Records execution history

```python
interpreter = Interpreter()
final_state = await interpreter.execute_grid(
    grid,
    on_command=lambda r, c, cmd: print(f"Executing {cmd} at [{r},{c}]"),
    on_unknown_command=lambda cmd: print(f"Unknown: {cmd}")
)
```

### Engine Workflow (`workflow.py`)

Integration with the ProcessController system:
- Accepts grid data from vision workflow or parameters
- Provides real-time status updates via WebSocket
- Returns execution results in structured format

## 🎮 Command Aliases

The engine recognizes multiple variations of commands:
- **Forward Movement**: `MOVE_FORWARD`, `FORWARD`, `FWD`
- **Turn Right**: `TURN_RIGHT`, `RIGHT`
- **Turn Left**: `TURN_LEFT`, `LEFT`

## 🔄 Execution Flow

1. **Initialize**: Create interpreter with empty state
2. **Process Grid**: Iterate through each cell row by row
3. **Execute Commands**: Look up and execute each command
4. **Update State**: Track position, direction, and history
5. **Return Results**: Final state with execution summary

## 📊 Example Execution

Given this grid:
```
[["FORWARD", "FORWARD", "RIGHT",  ""],
 ["FORWARD", "LEFT",    "FORWARD", ""],
 ["",        "FORWARD", "RIGHT",   "FWD"],
 ["",        "",        "FORWARD", ""]]
```

The interpreter will:
1. Start at (0, 0) facing right
2. Execute commands sequentially
3. End at position (4, 3) facing down
4. Record 10 total steps

## 🔗 Integration with Vision

The engine workflow can be chained with vision:

```python
# Run OCR first, then engine
{"command": "run", "params": {"workflow": "full"}}

# Run OCR with automatic chaining
{"command": "run", "params": {"workflow": "ocr_grid", "chain_engine": true}}

# Run engine with provided grid
{"command": "run", "params": {"workflow": "engine", "grid": [["FWD", "RIGHT"], ...]}}
```

## 🚀 Extending the Engine

To add new commands:

1. Create a command class implementing the protocol:
```python
class JumpCommand:
    name = "JUMP"
    
    def execute(self, state: ExecutionState) -> None:
        # Jump forward 2 spaces
        dx, dy = get_direction_delta(state.direction)
        state.move(dx * 2, dy * 2)
```

2. Register it in the CommandRegistry:
```python
registry = CommandRegistry()
registry.register(JumpCommand())
registry.register_alias("JP", registry.get("JUMP"))
```

## 🧪 Testing

See `scripts/test_engine_workflow.py` for a standalone test that demonstrates the engine processing a sample grid.

## 🔮 Future Enhancements

- **Conditional Commands**: IF/ELSE blocks
- **Loop Commands**: FOR/WHILE loops
- **Variable Support**: Store and use values
- **Function Definitions**: Reusable command sequences
- **Visual Output**: Generate movement visualization
- **Error Recovery**: Handle invalid command sequences 