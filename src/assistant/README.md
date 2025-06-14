# Assistant Module

The assistant module provides an AI-powered programming tutor for children using the TinkerBlocks system. It integrates LangGraph's react agent with custom tools to help children learn programming concepts through interactive guidance with their physical programming blocks and robot control.

## 📁 Module Structure

```
assistant/
├── __init__.py           # Module exports (assistant_workflow, create_assistant_tools)
├── workflow.py           # Main assistant workflow with LangGraph integration
├── tools.py              # Reusable tools factory for AI agent
├── prompt.py             # AI assistant system prompt and educational guidelines
└── README.md             # This file
```

## 🔧 Key Components

### AI Assistant Workflow (`workflow.py`)
- **`assistant_workflow()`**: Main workflow function that processes child messages
- **LangGraph Integration**: Uses `create_react_agent` for intelligent tool selection
- **Educational Focus**: Designed specifically for teaching programming to children
- **Real Robot Control**: Integrates with vision and engine modules for complete pipeline

### Tools Factory (`tools.py`)
- **`create_assistant_tools()`**: Factory function that creates LangChain tools with dependencies
- **Reusable Design**: Can be used by other parts of the system
- **Context-Aware**: Tools have access to send_message, controller, and ocr_engine

### Educational Prompt (`prompt.py`)
- **`assistant_system_prompt`**: Comprehensive system prompt for the AI tutor
- **Command Reference**: Complete guide to all TinkerBlocks programming commands
- **Teaching Guidelines**: Educational best practices for working with children
- **Progressive Learning**: Structured approach from basic to advanced concepts

## 🛠️ Available Tools

### **read_blocks**
Reads and understands the current block arrangement on the grid using OCR.
- Captures image of physical blocks
- Uses AI-powered vision to extract commands
- Formats results for educational explanation

### **execute_program**
Runs programs on the robot car to demonstrate concepts.
- Supports current grid or custom examples
- Real hardware execution for authentic experience
- Educational feedback on program results

### **think**
Shares the AI's thinking process with the child.
- Makes problem-solving transparent
- Teaches logical reasoning
- Builds programming intuition

### **answer**
Delivers final responses and educational guidance.
- Child-friendly explanations
- Encouraging and positive tone
- Builds on previous thinking process

## 🔄 Assistant Workflow

The workflow follows the standard protocol and integrates seamlessly with the existing system:

### Workflow Steps:
1. **Greeting**: Welcome the child and acknowledge their message
2. **Tool Creation**: Use factory to create tools with proper dependencies
3. **Agent Creation**: Build LangGraph react agent with chat model and tools
4. **Processing**: Let AI agent intelligently use tools to help the child
5. **Completion**: Provide encouraging completion message

### Usage Example:

```python
from assistant.workflow import assistant_workflow
from core import ProcessController
from vision.ocr import VLM_OCR

# Run assistant workflow
success, result = await controller.run_workflow(
    lambda send_message: assistant_workflow(
        send_message=send_message,
        user_message="How do I make my robot draw a square?",
        controller=controller,
        ocr_engine=ocr_engine,
    ),
    "AI Assistant",
)
```

## 🎯 Educational Features

### **Transparent Learning**
- **Think-Aloud Protocol**: AI shows its reasoning process
- **Step-by-Step Guidance**: Breaks down complex problems
- **Visual Demonstrations**: Uses real robot movement to teach concepts

### **Progressive Difficulty**
- **Basic Movement**: MOVE and TURN commands
- **Repetition**: LOOP for repeated actions  
- **Decision Making**: IF statements with sensors
- **Variables**: SET command for memory
- **Complex Logic**: WHILE loops and conditions

### **Encouraging Approach**
- **Mistake-Friendly**: Treats errors as learning opportunities
- **Celebrates Success**: Positive reinforcement for achievements
- **Patient Guidance**: Age-appropriate explanations
- **Interactive Learning**: Asks questions to check understanding

## 📡 Integration with System

### **Vision Module Integration**
- Uses OCR workflow to read physical blocks
- Processes grid data for AI understanding
- Handles image capture and processing errors gracefully

### **Engine Module Integration**  
- Executes programs on real robot hardware
- Demonstrates programming concepts through movement
- Provides real-time feedback on program execution

### **Core Module Integration**
- Uses ProcessController for workflow management
- Leverages LogLevel.ASSISTANT for proper message routing
- Integrates with WebSocket system for real-time communication

## 🧠 AI Model Integration

### **LangGraph React Agent**
- **Tool Selection**: Intelligently chooses appropriate tools
- **Chain of Thought**: Maintains context across tool calls
- **Error Handling**: Graceful degradation when tools fail

### **Chat Model Support**
- **Multi-Provider**: Works with OpenAI, Anthropic, and other providers
- **Configurable**: Uses `get_chat_model()` from core module
- **Educational Tuning**: System prompt optimized for teaching children

## 🎮 Command Examples

Children can interact with the assistant through WebSocket messages:

```json
{
    "command": "run", 
    "params": {
        "workflow": "assistant", 
        "message": "How do I make my robot draw a square?"
    }
}
```

```json
{
    "command": "run", 
    "params": {
        "workflow": "assistant", 
        "message": "My robot isn't moving, can you help debug my code?"
    }
}
```

```json
{
    "command": "run", 
    "params": {
        "workflow": "assistant", 
        "message": "Can you show me how to use loops?"
    }
}
```

## 📚 Programming Concepts Taught

### **Core Concepts**
- **Sequence**: Commands execute in order
- **Repetition**: LOOP for repeated actions
- **Selection**: IF/ELSE for decision making
- **Variables**: SET for storing values

### **Robot Programming**
- **Movement Control**: MOVE and TURN commands
- **Sensor Integration**: DISTANCE, OBSTACLE, BLACK_ON/OFF
- **Drawing**: PEN_ON/OFF for creative projects
- **Timing**: WAIT for program pacing

### **Advanced Topics**
- **Conditional Loops**: WHILE with sensor conditions
- **Mathematical Operations**: Arithmetic and comparison
- **Logical Operations**: AND, OR, NOT for complex conditions
- **Program Structure**: Indentation and nesting

## 🛡️ Error Handling

### **Graceful Degradation**
- **Tool Failures**: Continue with available tools
- **Network Issues**: Inform child and suggest alternatives
- **Hardware Problems**: Switch to simulation explanations

### **Educational Error Messages**
- **Child-Friendly**: Simple, encouraging language
- **Actionable**: Clear steps to resolve issues
- **Learning-Focused**: Turn errors into teaching moments