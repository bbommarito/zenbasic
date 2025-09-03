from lark import Transformer, Token
from typing import Dict, Any, List 
BASIC_GRAMMAR = r"""
    ?start: let_statement

    let_statement: "LET" IDENTIFIER "=" NUMBER

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

    def IDENTIFIER(self, token: Token) -> str:
        return str(token)
    
    def NUMBER(self, token: Token) -> int:
        return int(token)