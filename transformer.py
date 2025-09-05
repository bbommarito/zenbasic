from __future__ import annotations
from lark import Transformer, Token
from typing import Dict, Any, List, Tuple, Union, TYPE_CHECKING

from arithmetic import AuthenticArithmetic

if TYPE_CHECKING:
    from repl import ZenBasicRepl

class BasicTransformer(Transformer[Any, Any]):
    def __init__(self, variables: Dict[str, Tuple[Any, str]], turbo: bool = False):
        self.variables = variables
        self.turbo = turbo
        self.repl_instance: Union[ZenBasicRepl, None] = None
        self.arithmetic = AuthenticArithmetic(turbo)

    def let_statement(self, items: List[Any]) -> str:
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
            
            if hasattr(self, 'repl_instance') and self.repl_instance:  # We'll pass this reference
                self.repl_instance.store_variable_in_memory(name, int(value), 'integer')
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
            result = self.arithmetic.add_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) + float(right_val)
            return (result, 'float')

    def sub(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result = self.arithmetic.sub_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) - float(right_val)
            return (result, 'float')

    def mul(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result = self.arithmetic.multiply_by_addition(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) * float(right_val)
            return (result, 'float')

    def div(self, items: List[Any]) -> Tuple[Union[int, float], str]:
        left_val, left_type = items[0]
        right_val, right_type = items[1]

        if left_type == 'integer' and right_type == 'integer':
            result = self.arithmetic.div_by_loop(left_val, right_val)
            return (result, 'integer')
        else:
            result = float(left_val) / float(right_val)
            return (result, 'float')


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
