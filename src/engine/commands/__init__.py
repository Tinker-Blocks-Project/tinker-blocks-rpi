from .base import Command, CommandRegistry
from .movement import MoveCommand, TurnCommand
from .control import LoopCommand, IfCommand, ElseCommand
from .variable import SetCommand
from .drawing import PenUpCommand, PenDownCommand
from .utility import WaitCommand

__all__ = [
    "Command",
    "CommandRegistry",
    "MoveCommand",
    "TurnCommand",
    "LoopCommand",
    "IfCommand",
    "ElseCommand",
    "SetCommand",
    "PenUpCommand",
    "PenDownCommand",
    "WaitCommand",
]

# Register all commands
CommandRegistry.register(MoveCommand)
CommandRegistry.register(TurnCommand)
CommandRegistry.register(LoopCommand)
CommandRegistry.register(IfCommand)
CommandRegistry.register(ElseCommand)
CommandRegistry.register(SetCommand)
CommandRegistry.register(PenUpCommand)
CommandRegistry.register(PenDownCommand)
CommandRegistry.register(WaitCommand)
