from turtle import left
from lark import Transformer, Token
from typing import Dict, Any, List, Tuple, Union 
BASIC_GRAMMAR = r"""
    ?start: let_statement

    let_statement: "LET"i IDENTIFIER "=" expression

    expression: expression "+" term   -> add
                | expression "-" term   -> sub
                | term

    term: term "*" factor   -> mul
        | term "/" factor   -> div
        | factor

    factor: NUMBER
           | IDENTIFIER

    IDENTIFIER: /[A-Z][A-Z0-9_]*[%$]?/
    NUMBER: /\d+(\.\d+)?/

    %import common.WS
    %ignore WS
"""

class BasicTransformer(Transformer[Any, Any]):
    def __init__(self, variables: Dict[str, Tuple[Any, str]], turbo: bool = False):
        self.variables = variables
        self.turbo = turbo

    def let_statement(self, items: List[Any]):
        var_name = str(items[0])          
        expression_result = items[1]        

        if isinstance(expression_result, tuple):
            value = expression_result[0] # type: ignore
        else:
            value = expression_result
    
        self.set_variable(var_name, value)
        return f"Variable {var_name} set to {self.variables[var_name][0]}"

    def set_variable(self, name: str, value: Any):
        if name.endswith('%'):
            self.variables[name] = (int(value), 'integer')
        elif name.endswith('$'):
            self.variables[name] = (str(value), 'string')
        else:
            self.variables[name] = (float(value), 'float')

    def get_variable(self, name: str):
        value, var_type = self.variables.get(name, (0, 'float'))
        return value, var_type

    def add(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result = self.add_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) + float(right_val)
            return (result, 'float')

    def sub(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result = self.sub_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) - float(right_val)
            return (result, 'float')

    def mul(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result =  self.multiply_by_addition(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) * float(right_val)
            return (result, 'float')

    def div(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result =  self.div_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) / float(right_val)
            return (result, 'float')

    def div_by_loop(self, a: int, b: int) -> int:
        if b == 0:
            raise ZeroDivisionError("Division by zero")

        if self.turbo:
            # Turbo mode: use division directly
            return a // b

        negative_result = (a < 0) ^ (b < 0)
        a, b = abs(a), abs(b)

        count = 0
        while a >= b:
            a = self.sub_by_loop(a, b)
            count += 1

        return -count if negative_result else count

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

    def factor(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        item: Union[Tuple[Union[int, float], str], str] = items[0]
        if isinstance(item, tuple):
            return item
        else:
            var_name = str(item)
            return self.get_variable(var_name)

    def expression(self, items: List[Any]) -> int:
        return items[0]

    def term(self, items: List[Any]) -> int:
        return items[0]

    def IDENTIFIER(self, token: Token) -> str:
        return str(token)
    
    def NUMBER(self, token: Token) -> Tuple[Any, str]:
        value_str = str(token)
        if '.' in value_str:
            return float(value_str), 'float'
        else:
            return int(value_str), 'integer'
