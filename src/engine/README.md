# Engine Module

## Overview

The Engine module processes a 2D grid of programming blocks to control a robotic car. The system reads blocks left-to-right, top-to-bottom, with indentation-based block structure similar to Python.

## Architecture

The engine follows the interpreter pattern with these main components:

- **Parser**: Converts 2D grid into command tree with proper nesting
- **Commands**: Each command type handles its own execution logic
- **Values**: Type system for numbers, variables, expressions, and sensors
- **Context**: Tracks execution state (position, direction, variables, pen)
- **Executor**: Runs command tree with cancellation and step limiting

## Grid Interpretation Rules

### 1. Reading Order
- **Horizontal**: Left-to-right within each row
- **Vertical**: Top-to-bottom through rows
- **Grid Size**: Flexible dimensions

### 2. Indentation Rules
- **Base Level**: Commands starting at column 0
- **Nested Level**: Commands indented by starting in column > 0
- **Block Structure**: Indentation defines scope (no END statements needed)
- **ELSE Special Case**: ELSE at same indentation as IF is part of the IF block

### 3. Command Structure
Each row contains one command with its arguments:
```
COMMAND | arg1 | arg2 | arg3 | ...
```
Arguments are collected from subsequent cells until another command is found.

## Command Reference

### Movement Commands

#### MOVE
Moves the car forward or backward.

**Syntax**: 
- `MOVE` - Move forward 999cm (effectively "move until obstacle")
- `MOVE | distance` - Move specified distance in centimeters (negative for backward)

**Examples**:
```
MOVE                    # Move forward 999cm (until obstacle)
MOVE | 5               # Move forward 5cm
MOVE | -3              # Move backward 3cm  
MOVE | X               # Move forward X cm (variable)
```

#### TURN  
Rotates the car.

**Syntax**:
- `TURN | direction` - Turn 90° in direction (LEFT or RIGHT)
- `TURN | degrees` - Turn right by specified degrees
- `TURN | direction | degrees` - Turn in direction by degrees

**Examples**:
```
TURN | LEFT                      # Turn left 90°
TURN | RIGHT                     # Turn right 90°
TURN | 45                        # Turn right 45°
TURN | LEFT | 30                 # Turn left 30°
```

### Control Flow Commands

#### LOOP
Repeats a block of commands a specified number of times.

**Syntax**:
- `LOOP | count` - Loop specified number of times
- `LOOP | TRUE` - Loop forever (until max steps)
- `LOOP | FALSE` - Don't execute loop body

**Examples**:
```
LOOP | 5
    MOVE | 2
    TURN | RIGHT

LOOP | TRUE
    MOVE | 1
    IF | OBSTACLE
        TURN | RIGHT
```

#### WHILE
Repeats a block of commands while a condition is true.

**Syntax**:
- `WHILE | condition` - Loop while condition is true

**Examples**:
```
WHILE | X < 10
    MOVE | 1
    SET | X | X + 1

WHILE | DISTANCE > 15
    MOVE | 1

WHILE | NOT OBSTACLE
    MOVE | 1
    TURN | LEFT | 5
```

#### IF / ELSE
Conditional execution.

**Syntax**: 
- `IF | condition` - Execute if condition is true
- `ELSE` - Execute if previous IF was false

**Examples**:
```
IF | OBSTACLE
    TURN | RIGHT
    MOVE | 2
ELSE
    MOVE | 5

IF | X > 10
    SET | Y | 0

IF | DISTANCE < 15 AND BLACK_DETECTED
    TURN | LEFT
```

### Variable Commands

#### SET
Assigns values to variables.

**Syntax**: `SET | variable | value/expression`

**Parameters**:
- `variable`: Any alphabetic string (X, Y, COUNT, SPEED, etc.)
- `value/expression`: Number, sensor, or arithmetic expression

**Examples**:
```
SET | X | 5
SET | SPEED | 10
SET | Y | DISTANCE
SET | Z | X + 2
SET | COUNT | COUNT + 1
SET | FOUND | DISTANCE < 15
```

### Drawing Commands

#### PEN_DOWN / PEN_UP
Controls drawing.

**Syntax**: `PEN_DOWN` or `PEN_UP`

**Example**:
```
PEN_DOWN
LOOP | 4
    MOVE | 3
    TURN | RIGHT
PEN_UP
```

### Utility Commands

#### WAIT
Pauses execution for a specified time.

**Syntax**:
- `WAIT | seconds` - Wait for specified time

**Examples**:
```
WAIT | 2                        # Wait 2 seconds
WAIT | 0.5                      # Wait half second
```

#### ALERT_ON / ALERT_OFF
Controls the buzzer.

**Syntax**: `ALERT_ON` or `ALERT_OFF`

**Examples**:
```
ALERT_ON                        # Turn alert on
WAIT | 2                        # Wait 2 seconds  
ALERT_OFF                       # Turn alert off

IF | OBSTACLE
    ALERT_ON                    # Sound alert
    TURN | RIGHT
    ALERT_OFF
```

## Value Types

### Numbers
- **Integers**: 1, 5, 10, 45, 90, 180
- **Decimals**: 1.5, 2.7, 0.5
- **Negative**: -1, -5, -10

### Boolean Values
- **TRUE**: Boolean true value
- **FALSE**: Boolean false value

### Variables
- **Names**: Any alphabetic string (X, Y, SPEED, COUNT, etc.)
- **Types**: Store numeric or boolean values
- **Scope**: Global within execution

### Directions
- **LEFT**: Turn/direction indicator
- **RIGHT**: Turn/direction indicator
- **FORWARD**: Direction facing (0°)
- **BACKWARD**: Direction facing (180°)

### Sensor Values
- **DISTANCE**: Ultrasonic sensor reading in cm
- **OBSTACLE**: True if distance < 15cm
- **BLACK_DETECTED**: True if IR sensor detects black
- **BLACK_LOST**: Inverse of BLACK_DETECTED

## Operators

### Arithmetic Operators
- **+**: Addition
- **-**: Subtraction
- **\***: Multiplication
- **/**: Division

### Comparison Operators
- **<**: Less than
- **>**: Greater than  
- **<=**: Less than or equal
- **>=**: Greater than or equal
- **==**: Equal to
- **!=**: Not equal to

### Logical Operators
- **AND**: Both conditions must be true
- **OR**: Either condition must be true
- **NOT**: Inverts the condition

## Expression Evaluation

Expressions are evaluated left-to-right with these rules:
- No operator precedence (use parentheses if needed)
- Variables resolved to their current values
- Sensors polled when referenced
- Boolean results from comparisons can be stored

**Examples**:
```
X + 5                    # Add 5 to X
DISTANCE < 15            # Compare distance to 15
X > 5 AND Y < 10        # Logical AND of two comparisons
NOT OBSTACLE            # Invert obstacle detection
COUNT + 1               # Increment expression
```

## Execution Model

### Context State
The execution context tracks:
- **Position**: (x, y) coordinates
- **Direction**: Current facing (forward, right, backward, left)
- **Variables**: User-defined variable values
- **Pen State**: Up or down for drawing
- **Path**: Drawing path when pen is down
- **Step Count**: Number of commands executed

### Step Limiting
- Default limit: 1000 steps
- Prevents infinite loops
- Each command counts as one step
- Error raised when limit exceeded

### Sensor Interface
Sensors are polled in real-time:
- **get_distance()**: Returns numeric distance in cm
- **is_black_detected()**: Returns boolean for line detection
- Mock implementation available for testing

## Example Programs

### Drawing a Square
```
SET | SIDE | 3
PEN_DOWN
LOOP | 4
    MOVE | SIDE
    TURN | RIGHT
PEN_UP
```

### Obstacle Avoidance
```
WHILE | TRUE
    IF | OBSTACLE
        TURN | RIGHT
        MOVE | 2
        TURN | LEFT
    ELSE
        MOVE | 1
```

### Line Following
```
WHILE | TRUE
    IF | BLACK_DETECTED
        MOVE | 1
    ELSE
        WHILE | NOT BLACK_DETECTED
            TURN | LEFT | 5
```

### Variable Counter
```
SET | COUNT | 0
WHILE | COUNT < 10
    MOVE | 1
    TURN | RIGHT
    SET | COUNT | COUNT + 1
```

### Spiral Pattern
```
SET | DISTANCE | 1
LOOP | 10
    MOVE | DISTANCE
    TURN | RIGHT
    SET | DISTANCE | DISTANCE + 0.5
```

### Sensor-Based Navigation
```
WHILE | TRUE
    WHILE | DISTANCE > 15
        MOVE | 1
    IF | DISTANCE < 10
        MOVE | -2
        TURN | 180
    ELSE
        TURN | RIGHT
```

### Alert System
```
WHILE | TRUE
    IF | OBSTACLE
        ALERT_ON
        WAIT | 0.5
        ALERT_OFF
        WAIT | 0.5
        TURN | RIGHT
    ELSE
        MOVE | 1
```

## Error Handling

### Parse Errors
- Unknown command
- Invalid arguments
- ELSE without IF
- Malformed expressions

### Runtime Errors
- Maximum steps exceeded
- Division by zero
- Invalid sensor readings
- Variable not defined

### Recovery
- Execution stops on error
- Final state returned with error message
- Grid position included in error

## Implementation Details

### Command Registry
- Commands self-register on import
- Each command validates its own arguments
- Factory pattern for command creation

### Parser Algorithm
1. Process grid row by row
2. Track indentation with stack
3. Handle ELSE as special case
4. Build nested command structure

### Value System
- Base Value class with evaluate protocol
- Concrete types: Number, Variable, Sensor, Direction, Boolean
- Expression class for compound evaluations
- Type coercion in operators

### Async Execution
- Commands execute asynchronously
- Cancellation callback checked between steps
- Message callback for progress updates

## Testing

The engine includes comprehensive end-to-end tests covering:
- Basic movement and turning
- Loops with various conditions
- WHILE loops with conditions
- IF/ELSE branching
- Variable operations
- Expression evaluation
- Sensor integration
- Drawing commands
- Alert control
- Error conditions
- Complex programs

Run tests with:
```bash
cd src/engine
python -m pytest tests/test_engine_e2e.py -v
```