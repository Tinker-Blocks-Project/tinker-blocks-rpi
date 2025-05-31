"""Execution state management for the interpreter."""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class Position:
    """2D position in the grid."""

    x: int = 0
    y: int = 0

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclass
class ExecutionStep:
    """Record of a single execution step."""

    step_number: int
    command: str
    position: Position
    direction: str

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "step": self.step_number,
            "command": self.command,
            "position": {"x": self.position.x, "y": self.position.y},
            "direction": self.direction,
        }


@dataclass
class ExecutionState:
    """State of the interpreter during execution."""

    position: Position = field(default_factory=Position)
    direction: str = "right"  # right, down, left, up
    variables: Dict[str, Any] = field(default_factory=dict)
    output: List[ExecutionStep] = field(default_factory=list)
    steps_executed: int = 0

    def move(self, dx: int, dy: int) -> None:
        """Move the position by the given deltas."""
        self.position.x += dx
        self.position.y += dy

    def record_step(self, command: str) -> None:
        """Record an execution step."""
        self.steps_executed += 1
        step = ExecutionStep(
            step_number=self.steps_executed,
            command=command,
            position=Position(self.position.x, self.position.y),
            direction=self.direction,
        )
        self.output.append(step)

    def to_dict(self) -> dict:
        """Convert state to dictionary for serialization."""
        return {
            "position": {"x": self.position.x, "y": self.position.y},
            "direction": self.direction,
            "variables": self.variables,
            "output": [step.to_dict() for step in self.output],
            "steps_executed": self.steps_executed,
        }
