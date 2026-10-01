import re

from langchain.tools import tool


@tool
def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.
    """

    if not re.fullmatch(
        r"[0-9+\-*/().\s]+",
        expression
    ):
        return "Invalid mathematical expression."

    try:

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        # Remove .0 for whole numbers
        if isinstance(result, float) and result.is_integer():
            return str(int(result))

        return str(result)

    except Exception as e:

        return f"Calculation error: {str(e)}"