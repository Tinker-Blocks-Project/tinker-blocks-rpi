"""Expression evaluation for arithmetic and logical operations."""

from dataclasses import dataclass
from typing import Any

from .base import Value, ValueParser
from ..types import Number, OperatorType
from ..context import ExecutionContext


@dataclass
class Expression(Value):
    """An expression combining values with operators."""

    left: Value
    operator: OperatorType
    right: Value | None = None  # None for unary operators like NOT

    async def evaluate(self, context: ExecutionContext) -> Number | bool:
        """Evaluate the expression."""
        # Evaluate operands
        left_val = await self.left.evaluate(context)
        right_val = await self.right.evaluate(context) if self.right else None

        # Unary operators
        if self.operator == OperatorType.NOT:
            return not bool(left_val)

        # Binary operators require right operand
        if right_val is None:
            raise ValueError(f"Binary operator {self.operator} requires right operand")

        # Arithmetic operators - ensure numeric types
        if self.operator in (
            OperatorType.ADD,
            OperatorType.SUBTRACT,
            OperatorType.MULTIPLY,
            OperatorType.DIVIDE,
        ):
            # Convert to numeric values
            left_num = self._to_number(left_val)
            right_num = self._to_number(right_val)

            if self.operator == OperatorType.ADD:
                return left_num + right_num
            elif self.operator == OperatorType.SUBTRACT:
                return left_num - right_num
            elif self.operator == OperatorType.MULTIPLY:
                return left_num * right_num
            elif self.operator == OperatorType.DIVIDE:
                if right_num == 0:
                    raise ValueError("Division by zero")
                return left_num / right_num

        # Comparison operators - work with numeric values
        elif self.operator in (
            OperatorType.LESS_THAN,
            OperatorType.LESS_EQUAL,
            OperatorType.GREATER_THAN,
            OperatorType.GREATER_EQUAL,
        ):
            left_num = self._to_number(left_val)
            right_num = self._to_number(right_val)

            if self.operator == OperatorType.LESS_THAN:
                return left_num < right_num
            elif self.operator == OperatorType.LESS_EQUAL:
                return left_num <= right_num
            elif self.operator == OperatorType.GREATER_THAN:
                return left_num > right_num
            elif self.operator == OperatorType.GREATER_EQUAL:
                return left_num >= right_num

        # Equality operators - work with any type
        elif self.operator == OperatorType.EQUAL:
            return left_val == right_val
        elif self.operator == OperatorType.NOT_EQUAL:
            return left_val != right_val

        # Logical operators
        elif self.operator == OperatorType.AND:
            return bool(left_val) and bool(right_val)
        elif self.operator == OperatorType.OR:
            return bool(left_val) or bool(right_val)

        raise ValueError(f"Unknown operator: {self.operator}")

    def _to_number(self, value: Any) -> Number:
        """Convert a value to a number."""
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to number")
        else:
            raise ValueError(f"Cannot convert {type(value)} to number")

    def __repr__(self) -> str:
        if self.right:
            return f"Expression({self.left} {self.operator.value} {self.right})"
        return f"Expression({self.operator.value} {self.left})"


class ExpressionParser:
    """Parser for expressions from token lists."""

    @staticmethod
    def parse_tokens(tokens: list[str]) -> Value | None:
        """Parse a list of tokens into an expression or value.

        Handles:
        - Single values: "5", "X", "DISTANCE"
        - Binary expressions: "X + 5", "DISTANCE < 30"
        - Unary expressions: "NOT OBSTACLE"
        - Complex expressions: "X > 5 AND Y < 10"
        """
        if not tokens:
            return None

        # Remove empty tokens
        tokens = [t for t in tokens if t.strip()]
        if not tokens:
            return None

        # Single token - try to parse as value
        if len(tokens) == 1:
            return ValueParser.parse(tokens[0])

        # Look for logical operators (lowest precedence)
        for i, token in enumerate(tokens):
            if token.upper() in ("AND", "OR"):
                left_expr = ExpressionParser.parse_tokens(tokens[:i])
                right_expr = ExpressionParser.parse_tokens(tokens[i + 1 :])
                if left_expr and right_expr:
                    op = OperatorType.AND if token.upper() == "AND" else OperatorType.OR
                    return Expression(left_expr, op, right_expr)

        # Look for comparison operators
        for i, token in enumerate(tokens):
            if token in ("<", "<=", ">", ">=", "=", "!="):
                left_expr = ExpressionParser.parse_tokens(tokens[:i])
                right_expr = ExpressionParser.parse_tokens(tokens[i + 1 :])
                if left_expr and right_expr:
                    op_map = {
                        "<": OperatorType.LESS_THAN,
                        "<=": OperatorType.LESS_EQUAL,
                        ">": OperatorType.GREATER_THAN,
                        ">=": OperatorType.GREATER_EQUAL,
                        "=": OperatorType.EQUAL,
                        "!=": OperatorType.NOT_EQUAL,
                    }
                    return Expression(left_expr, op_map[token], right_expr)

        # Look for arithmetic operators
        for i, token in enumerate(tokens):
            if token in ("+", "-", "*", "/"):
                left_expr = ExpressionParser.parse_tokens(tokens[:i])
                right_expr = ExpressionParser.parse_tokens(tokens[i + 1 :])
                if left_expr and right_expr:
                    op_map = {
                        "+": OperatorType.ADD,
                        "-": OperatorType.SUBTRACT,
                        "*": OperatorType.MULTIPLY,
                        "/": OperatorType.DIVIDE,
                    }
                    return Expression(left_expr, op_map[token], right_expr)

        # Check for unary NOT
        if tokens[0].upper() == "NOT" and len(tokens) > 1:
            operand = ExpressionParser.parse_tokens(tokens[1:])
            if operand:
                return Expression(operand, OperatorType.NOT)

        # Try to parse the whole thing as a value
        return ValueParser.parse(" ".join(tokens))
