"""
Direct Token Executor for ZenBasic
Because we sold our kidneys for a math co-processor in 1983

This executes tokenized BASIC directly from memory bytes,
just like real 8-bit interpreters did. No parsing, no AST,
just raw token interpretation.
"""
from typing import Optional, Tuple, Any
from tokens import TOKENS


class TokenExecutor:
    """
    Executes BASIC tokens directly from bytes.
    Like a real 1983 interpreter, but with a math co-processor
    we're still paying off.
    """
    
    def __init__(self, repl):
        """
        Initialize with reference to REPL for variable/memory access.
        
        Args:
            repl: The ZenBasicRepl instance for accessing memory, variables, etc.
        """
        self.repl = repl
        self.memory = repl.memory_manager
        
    def execute_line(self, tokens: bytes) -> Optional[Any]:
        """
        Execute a line of tokenized BASIC.
        
        Args:
            tokens: Byte array of tokens for one line (without line number/pointers)
            
        Returns:
            Result of execution (if any) or None
            
        Raises:
            Exception if we hit something we can't execute yet (fallback to parser)
        """
        if not tokens:
            return None
            
        # Skip leading spaces
        pos = 0
        while pos < len(tokens) and tokens[pos] == 0x20:  # space
            pos += 1
            
        if pos >= len(tokens):
            return None
            
        # Check the first token
        first_token = tokens[pos]
        
        # Route to appropriate handler based on token
        if first_token == 0xE2:  # LET
            return self.execute_let(tokens, pos + 1)
        elif first_token == 0xEA:  # PRINT
            return self.execute_print(tokens, pos + 1)
        else:
            # We don't handle this yet, raise exception to trigger fallback
            raise NotImplementedError(f"Token {first_token:02X} not implemented in direct executor")
    
    def execute_let(self, tokens: bytes, pos: int) -> Optional[Any]:
        """
        Execute a LET statement.
        Format: LET <var> = <expression>
        Token: E2 [spaces] <var_name> [spaces] = [spaces] <expression>
        
        Args:
            tokens: The token bytes
            pos: Position after the LET token
            
        Returns:
            Result message or None
        """
        # Skip spaces after LET
        while pos < len(tokens) and tokens[pos] == 0x20:
            pos += 1
            
        # Parse variable name (ASCII letters followed by optional % or $)
        var_name, pos = self.parse_variable_name(tokens, pos)
        if not var_name:
            raise SyntaxError("Expected variable name after LET")
            
        # Skip spaces
        while pos < len(tokens) and tokens[pos] == 0x20:
            pos += 1
            
        # Expect = sign
        if pos >= len(tokens) or tokens[pos] != 0x3D:  # '='
            raise SyntaxError(f"Expected '=' after variable name, got {tokens[pos]:02X if pos < len(tokens) else 'EOL'}")
        pos += 1
        
        # Skip spaces after =
        while pos < len(tokens) and tokens[pos] == 0x20:
            pos += 1
            
        # Evaluate the expression
        value, pos = self.evaluate_expression(tokens, pos)
        
        # Determine variable type
        if var_name.endswith('%'):
            # Integer variable
            var_type = 'integer'
            value = int(value)
        elif var_name.endswith('$'):
            # String variable (not supported yet)
            raise NotImplementedError("String variables not yet supported")
        else:
            # Float variable
            var_type = 'float'
            value = float(value)
            
        # Store the variable using REPL's method
        self.repl.store_variable_in_memory(var_name, value, var_type)
        
        return f"Variable {var_name} set to {value}"
    
    def execute_print(self, tokens: bytes, pos: int) -> Optional[Any]:
        """
        Execute a PRINT statement.
        For now, just a placeholder that triggers fallback.
        
        Args:
            tokens: The token bytes
            pos: Position after PRINT token
            
        Returns:
            Printed output
        """
        # TODO: Implement PRINT
        raise NotImplementedError("PRINT not yet implemented in direct executor")
    
    def parse_variable_name(self, tokens: bytes, pos: int) -> Tuple[str, int]:
        """
        Parse a variable name from tokens.
        Variables are ASCII: [A-Z][A-Z0-9]*[%$]?
        
        Args:
            tokens: The token bytes
            pos: Current position
            
        Returns:
            Tuple of (variable_name, new_position)
        """
        if pos >= len(tokens):
            return "", pos
            
        # First character must be A-Z
        if not (0x41 <= tokens[pos] <= 0x5A):  # A-Z
            return "", pos
            
        name = []
        
        # Collect alphanumeric characters
        while pos < len(tokens):
            ch = tokens[pos]
            if 0x41 <= ch <= 0x5A:  # A-Z
                name.append(chr(ch))
                pos += 1
            elif 0x30 <= ch <= 0x39:  # 0-9
                name.append(chr(ch))
                pos += 1
            elif ch == 0x25:  # %
                name.append('%')
                pos += 1
                break
            elif ch == 0x24:  # $
                name.append('$')
                pos += 1
                break
            else:
                break
                
        return ''.join(name), pos
    
    def evaluate_expression(self, tokens: bytes, pos: int) -> Tuple[float, int]:
        """
        Evaluate an expression from tokens.
        For now, handles:
        - Numbers (integer and float)
        - Variables
        - Binary operations (+, -, *, /)
        - Parentheses
        
        Uses our fancy math co-processor (native Python math).
        
        Args:
            tokens: The token bytes
            pos: Current position
            
        Returns:
            Tuple of (computed_value, new_position)
        """
        # Start with parsing a term
        left_value, pos = self.parse_term(tokens, pos)
        
        # Check for operators
        while pos < len(tokens):
            # Skip spaces
            while pos < len(tokens) and tokens[pos] == 0x20:
                pos += 1
                
            if pos >= len(tokens):
                break
                
            op = tokens[pos]
            
            # Check if it's an operator
            if op == 0x2B:  # +
                pos += 1
                right_value, pos = self.parse_term(tokens, pos)
                left_value = left_value + right_value  # Co-processor add!
            elif op == 0x2D:  # -
                pos += 1
                right_value, pos = self.parse_term(tokens, pos)
                left_value = left_value - right_value  # Co-processor subtract!
            elif op == 0x2A:  # *
                pos += 1
                right_value, pos = self.parse_term(tokens, pos)
                left_value = left_value * right_value  # Co-processor multiply!
            elif op == 0x2F:  # /
                pos += 1
                right_value, pos = self.parse_term(tokens, pos)
                if right_value == 0:
                    raise ValueError("Division by zero")
                left_value = left_value / right_value  # Co-processor divide!
            else:
                # Not an operator we recognize, stop parsing
                break
                
        return left_value, pos
    
    def parse_term(self, tokens: bytes, pos: int) -> Tuple[float, int]:
        """
        Parse a term (number, variable, or parenthesized expression).
        
        Args:
            tokens: The token bytes  
            pos: Current position
            
        Returns:
            Tuple of (value, new_position)
        """
        # Skip leading spaces
        while pos < len(tokens) and tokens[pos] == 0x20:
            pos += 1
            
        if pos >= len(tokens):
            raise SyntaxError("Unexpected end of expression")
            
        # Check for parentheses
        if tokens[pos] == 0x28:  # (
            pos += 1
            value, pos = self.evaluate_expression(tokens, pos)
            # Skip spaces
            while pos < len(tokens) and tokens[pos] == 0x20:
                pos += 1
            # Expect closing paren
            if pos >= len(tokens) or tokens[pos] != 0x29:  # )
                raise SyntaxError("Expected closing parenthesis")
            pos += 1
            return value, pos
            
        # Check for negative number
        negative = False
        if tokens[pos] == 0x2D:  # -
            negative = True
            pos += 1
            # Skip spaces after minus
            while pos < len(tokens) and tokens[pos] == 0x20:
                pos += 1
                
        # Try to parse a number
        if pos < len(tokens) and (0x30 <= tokens[pos] <= 0x39):  # 0-9
            value, pos = self.parse_number(tokens, pos)
            if negative:
                value = -value
            return value, pos
            
        # Try to parse a variable
        var_name, new_pos = self.parse_variable_name(tokens, pos)
        if var_name:
            # Look up variable value
            var_info = self.repl.get_variable_value(var_name)
            if var_info is None:
                raise NameError(f"Undefined variable: {var_name}")
            value, _ = var_info
            if negative:
                value = -value
            return float(value), new_pos
            
        raise SyntaxError(f"Expected number or variable at position {pos}")
    
    def parse_number(self, tokens: bytes, pos: int) -> Tuple[float, int]:
        """
        Parse a number (integer or float) from tokens.
        
        Args:
            tokens: The token bytes
            pos: Current position
            
        Returns:
            Tuple of (numeric_value, new_position)
        """
        num_str = []
        has_decimal = False
        
        while pos < len(tokens):
            ch = tokens[pos]
            if 0x30 <= ch <= 0x39:  # 0-9
                num_str.append(chr(ch))
                pos += 1
            elif ch == 0x2E and not has_decimal:  # . (decimal point)
                num_str.append('.')
                has_decimal = True
                pos += 1
            else:
                break
                
        if not num_str:
            raise SyntaxError("Expected number")
            
        return float(''.join(num_str)), pos
