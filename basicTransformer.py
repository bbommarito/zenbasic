from lark import Transformer, Token
from typing import Dict, Any, List 
BASIC_GRAMMAR = r"""
    ?start: let_statement

    let_statement: "LET"i IDENTIFIER "=" expression

    expression: expression "+" term   -> add
                | term

    term: NUMBER
        | IDENTIFIER

    IDENTIFIER: /[A-Z][A-Z0-9_]*/
    NUMBER: /\d+/

    %import common.WS
    %ignore WS
"""

class BasicTransformer(Transformer[Any, Any]):
    def __init__(self, variables: Dict[str, int]):
        self.variables = variables

    def let_statement(self, items: List[Any]):
        var_name = str(items[0])
        value = int(items[1])
        self.variables[var_name] = value
        return f"Variable {var_name} set to {value}"

    def add(self, items: List[Any]) -> int:
        left = items[0]
        right = items[1]
        return self.add_by_loop(left, right)
    
    def add_by_loop(self, a: int, b: int) -> int:
        if b == 0:
            return a
        if b > 0:
            for _ in range(b):
                a += 1
        else:
            for _ in range(-b):
                a -= 1
        return a

    def expression(self, items: List[Any]) -> int:
        return items[0]

    def term(self, items: List[Any]) -> int:
        return items[0]

    def IDENTIFIER(self, token: Token) -> str:
        return str(token)
    
    def NUMBER(self, token: Token) -> int:
        return int(token)