from .base import Command, CommandRegistry
from .movement import MoveCommand, TurnCommand
from .control import LoopCommand, WhileCommand, IfCommand, ElseCommand
from .variable import SetCommand
from .drawing import PenUpCommand, PenDownCommand
from .utility import WaitCommand
from .alert import AlertOnCommand, AlertOffCommand

__all__ = [
    "Command",
    "CommandRegistry",
    "MoveCommand",
    "TurnCommand",
    "LoopCommand",
    "WhileCommand",
    "IfCommand",
    "ElseCommand",
    "SetCommand",
    "PenUpCommand",
    "PenDownCommand",
    "WaitCommand",
    "AlertOnCommand",
    "AlertOffCommand",
]

# Register all commands
CommandRegistry.register(MoveCommand)
CommandRegistry.register(TurnCommand)
CommandRegistry.register(LoopCommand)
CommandRegistry.register(WhileCommand)
CommandRegistry.register(IfCommand)
CommandRegistry.register(ElseCommand)
CommandRegistry.register(SetCommand)
CommandRegistry.register(PenUpCommand)
CommandRegistry.register(PenDownCommand)
CommandRegistry.register(WaitCommand)
CommandRegistry.register(AlertOnCommand)
CommandRegistry.register(AlertOffCommand)
