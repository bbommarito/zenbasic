from lark import Transformer, Token
from typing import Dict, Any, List 
BASIC_GRAMMAR = r"""
    ?start: let_statement

    let_statement: "LET"i IDENTIFIER "=" expression

    expression: expression "+" term   -> add
                | expression "-" term   -> sub
                | term

    term: term "*" factor   -> mul
        | factor

    factor: NUMBER
           | IDENTIFIER

    IDENTIFIER: /[A-Z][A-Z0-9_]*/
    NUMBER: /\d+/

    %import common.WS
    %ignore WS
"""

class BasicTransformer(Transformer[Any, Any]):
    def __init__(self, variables: Dict[str, int], turbo: bool = False):
        self.variables = variables
        self.turbo = turbo

    def let_statement(self, items: List[Any]):
        var_name = str(items[0])
        value = int(items[1])
        self.variables[var_name] = value
        return f"Variable {var_name} set to {value}"

    def add(self, items: List[Any]) -> int:
        left = items[0]
        right = items[1]
        return self.add_by_loop(left, right)

    def sub(self, items: List[Any]) -> int:
        left = items[0]
        right = items[1]
        return self.sub_by_loop(left, right)

    def mul(self, items: List[Any]) -> int:
        left = items[0]
        right = items[1]
        return self.multiply_by_addition(left, right)

    def multiply_by_addition(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0

        if self.turbo:
            # Turbo mode: use multiplication directly
            return a * b

        negative_result = (a < 0) ^ (b < 0)
        a, b = abs(a), abs(b)

        if a > b:
            a, b = b, a

        result = 0
        for _ in range(a):
            result = self.add_by_loop(result, b)

        return -result if negative_result else result


    def sub_by_loop(self, a: int, b: int) -> int:
        if self.turbo:
            # Turbo mode: use subtraction directly
            return a - b

        return self.add_by_loop(a, -b)

    def add_by_loop(self, a: int, b: int) -> int:
        if b == 0:
            return a

        if self.turbo:
            # Turbo mode: use addition directly
            return a + b

        if b > 0:
            for _ in range(b):
                a += 1
        else:
            for _ in range(-b):
                a -= 1
        return a

    def factor(self, items: List[Any]) -> int:
        return items[0]

    def expression(self, items: List[Any]) -> int:
        return items[0]

    def term(self, items: List[Any]) -> int:
        return items[0]

    def IDENTIFIER(self, token: Token) -> str:
        return str(token)
    
    def NUMBER(self, token: Token) -> int:
        return int(token)