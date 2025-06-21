"""Expression evaluation for arithmetic and logical operations."""

from dataclasses import dataclass
from typing import Any
import logging
from core.types import LogLevel

from .base import Value, ValueParser
from ..types import Number, OperatorType
from ..context import ExecutionContext

logger = logging.getLogger(__name__)


@dataclass
class Expression(Value):
    """An expression combining values with operators."""

    left: Value
    operator: OperatorType
    right: Value | None = None  # None for unary operators like NOT

    async def evaluate(self, context: ExecutionContext) -> Number | bool:
        """Evaluate the expression."""
        if context.send_message:
            await context.send_message(
                f"🧮 Expression.evaluate() starting: {self}", LogLevel.DEBUG
            )

        # Evaluate operands
        left_val = await self.left.evaluate(context)
        if context.send_message:
            await context.send_message(
                f"   ↳ Left operand: {self.left} → {left_val}", LogLevel.DEBUG
            )

        right_val = await self.right.evaluate(context) if self.right else None
        if self.right and context.send_message:
            await context.send_message(
                f"   ↳ Right operand: {self.right} → {right_val}", LogLevel.DEBUG
            )

        # Unary operators
        if self.operator == OperatorType.NOT:
            result = not bool(left_val)
            if context.send_message:
                await context.send_message(
                    f"   ↳ NOT {left_val} = {result}", LogLevel.DEBUG
                )
            return result

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
                result = left_num + right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} + {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.SUBTRACT:
                result = left_num - right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} - {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.MULTIPLY:
                result = left_num * right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} * {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.DIVIDE:
                if right_num == 0:
                    raise ValueError("Division by zero")
                result = left_num / right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} / {right_num} = {result}", LogLevel.DEBUG
                    )
                return result

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
                result = left_num < right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} < {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.LESS_EQUAL:
                result = left_num <= right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} <= {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.GREATER_THAN:
                result = left_num > right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} > {right_num} = {result}", LogLevel.DEBUG
                    )
                return result
            elif self.operator == OperatorType.GREATER_EQUAL:
                result = left_num >= right_num
                if context.send_message:
                    await context.send_message(
                        f"   ↳ {left_num} >= {right_num} = {result}", LogLevel.DEBUG
                    )
                return result

        # Equality operators - work with any type
        elif self.operator == OperatorType.EQUAL:
            result = left_val == right_val
            if context.send_message:
                await context.send_message(
                    f"   ↳ {left_val} = {right_val} → {result}", LogLevel.DEBUG
                )
            return result
        elif self.operator == OperatorType.NOT_EQUAL:
            result = left_val != right_val
            if context.send_message:
                await context.send_message(
                    f"   ↳ {left_val} != {right_val} → {result}", LogLevel.DEBUG
                )
            return result

        # Logical operators
        elif self.operator == OperatorType.AND:
            result = bool(left_val) and bool(right_val)
            if context.send_message:
                await context.send_message(
                    f"   ↳ {left_val} AND {right_val} → {result}", LogLevel.DEBUG
                )
            return result
        elif self.operator == OperatorType.OR:
            result = bool(left_val) or bool(right_val)
            if context.send_message:
                await context.send_message(
                    f"   ↳ {left_val} OR {right_val} → {result}", LogLevel.DEBUG
                )
            return result

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

        logger.debug(f"🧮 ExpressionParser.parse_tokens() input: {tokens}")

        # Debug individual token parsing
        for i, token in enumerate(tokens):
            parsed = ValueParser.parse(token)
            logger.debug(
                f"   Token[{i}]: '{token}' → {parsed} ({type(parsed).__name__ if parsed else 'None'})"
            )

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
            if token in ("<", "<=", ">", ">=", "=", "!=", "=="):
                left_expr = ExpressionParser.parse_tokens(tokens[:i])
                right_expr = ExpressionParser.parse_tokens(tokens[i + 1 :])
                if left_expr and right_expr:
                    op_map = {
                        "<": OperatorType.LESS_THAN,
                        "<=": OperatorType.LESS_EQUAL,
                        ">": OperatorType.GREATER_THAN,
                        ">=": OperatorType.GREATER_EQUAL,
                        "=": OperatorType.EQUAL,
                        "==": OperatorType.EQUAL,
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
        result = ValueParser.parse(" ".join(tokens))

        if result is None:
            logger.warning(f"🧮 ExpressionParser failed to parse tokens: {tokens}")
            logger.warning(
                f"   ↳ Attempted to parse as single value: '{' '.join(tokens)}'"
            )
        else:
            logger.debug(
                f"🧮 ExpressionParser successfully parsed as single value: {result}"
            )

        return result
