"""
Authentic arithmetic operations for ZenBasic
Because who needs an ALU when you have loops?
"""

class AuthenticArithmetic:
    """
    Implements arithmetic the way nature intended - by counting.
    Supports turbo mode for when you need 1000 + 1000 to finish before lunch.
    """
    
    def __init__(self, turbo: bool = False):
        self.turbo = turbo
    
    def set_turbo(self, enabled: bool) -> None:
        """Enable or disable turbo mode"""
        self.turbo = enabled
    
    def add_by_loop(self, a: int, b: int) -> int:
        """
        Addition by counting - increment a by 1, b times.
        Or decrement if b is negative, because subtraction is just backwards addition.
        """
        if b == 0:
            return a
        
        if self.turbo:
            # Turbo mode: use the forbidden built-in operator
            return a + b
        
        # Authentic mode: count like it's 1978
        if b > 0:
            for _ in range(b):
                a += 1
        else:
            for _ in range(-b):
                a -= 1
        return a
    
    def sub_by_loop(self, a: int, b: int) -> int:
        """
        Subtraction by adding negative numbers.
        We don't subtract here, we just add with a fake mustache.
        """
        if self.turbo:
            # Turbo mode: use subtraction directly
            return a - b
        
        # Turn subtraction into addition of negative
        return self.add_by_loop(a, -b)
    
    def multiply_by_addition(self, a: int, b: int) -> int:
        """
        Multiplication by repeated addition.
        Loops inside loops, just as Turing intended.
        """
        if a == 0 or b == 0:
            return 0
        
        if self.turbo:
            # Turbo mode: use multiplication directly
            return a * b
        
        # Handle negative numbers
        negative_result = (a < 0) ^ (b < 0)
        a, b = abs(a), abs(b)
        
        # Optimize by using the smaller number as the loop count
        if a > b:
            a, b = b, a
        
        # Add b to itself a times
        result = 0
        for _ in range(a):
            result = self.add_by_loop(result, b)
        
        return -result if negative_result else result
    
    def div_by_loop(self, a: int, b: int) -> int:
        """
        Integer division by repeated subtraction.
        Count how many times we can subtract b from a.
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        
        if self.turbo:
            # Turbo mode: use division directly
            return a // b
        
        # Handle negative numbers
        negative_result = (a < 0) ^ (b < 0)
        a, b = abs(a), abs(b)
        
        # Count how many times b fits into a
        count = 0
        while a >= b:
            a = self.sub_by_loop(a, b)
            count += 1
        
        return -count if negative_result else count
    
    def modulo_by_loop(self, a: int, b: int) -> int:
        """
        Modulo by repeated subtraction.
        What's left after we can't subtract anymore.
        """
        if b == 0:
            raise ZeroDivisionError("Modulo by zero")
        
        if self.turbo:
            # Turbo mode: use modulo directly
            return a % b
        
        # For modulo, we want the remainder
        # So we do division but return what's left
        a_orig = a
        b_orig = b
        a, b = abs(a), abs(b)
        
        while a >= b:
            a = self.sub_by_loop(a, b)
        
        # Handle negative numbers properly for modulo
        if a_orig < 0:
            return -a if a != 0 else 0
        return a
