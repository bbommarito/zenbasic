"""
Parser module for ZenBasic
Handles grammar loading and parser creation
"""
from pathlib import Path
from lark import Lark, Transformer, Token, exceptions
from lark.exceptions import LarkError
from typing import Any, Optional


class BasicParser:
    """
    Wrapper for the Lark parser.
    Loads grammar from file and provides parsing functionality.
    """
    
    def __init__(self, grammar_file: str = "basic.lark"):
        """Initialize parser with grammar from file"""
        grammar_path = Path(__file__).parent / grammar_file
        
        if not grammar_path.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
        
        with open(grammar_path, 'r') as f:
            grammar_content = f.read()
        
        self.parser = Lark(grammar_content, parser='lalr', debug=False)
    
    def parse(self, text: str):
        """Parse BASIC code and return parse tree"""
        return self.parser.parse(text)
    
    def parse_safe(self, text: str) -> tuple[bool, Any]:
        """
        Safely parse BASIC code.
        Returns (success, result) where result is either parse tree or error message.
        """
        try:
            tree = self.parse(text)
            return True, tree
        except exceptions.LarkError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Error: {e}"


# Export commonly used items for backward compatibility
__all__ = ['BasicParser', 'BASIC_GRAMMAR', 'LarkError', 'exceptions']

# For backward compatibility, export the old BASIC_GRAMMAR constant
# This can be removed once everything is updated
BASIC_GRAMMAR = """
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
    NUMBER: /\\d+(\\.\\d+)?/

    %import common.WS
    %ignore WS
"""
