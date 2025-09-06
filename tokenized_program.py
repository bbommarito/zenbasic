"""
Tokenized program storage for ZenBasic
Stores BASIC programs as tokenized bytes in actual memory
Just like 1983!
"""
from typing import Optional, List, Tuple
from tokens import tokenize_line, detokenize


class TokenizedProgramStore:
    """
    Manages tokenized BASIC programs in virtual memory.
    No more Python dictionaries - we're living in 64K now!
    """
    
    def __init__(self, memory_manager):
        self.memory = memory_manager
    
    def add_line(self, line_num: int, code: str) -> None:
        """
        Store a program line, tokenizing it first.
        Empty code deletes the line.
        Whitespace is MURDERED. RIP formatting.
        """
        if code.strip():
            # Strip ALL whitespace except in strings and after REM
            # This is where your beautiful formatting dies
            cleaned = self._strip_whitespace(code)
            
            # Tokenize the line
            tokens = tokenize_line(cleaned)
            
            # Store in memory
            if self.memory.store_program_line(line_num, tokens):
                print(f"Line {line_num} stored")
            else:
                print(f"Out of memory! Cannot store line {line_num}")
        else:
            # Empty line deletes the line number
            if self.memory.delete_program_line(line_num):
                print(f"Line {line_num} deleted")
    
    def _strip_whitespace(self, code: str) -> str:
        """
        Strip unnecessary whitespace while preserving strings and REM comments.
        This is where dreams of readable code go to die.
        But we'll at least keep spaces around operators for readability.
        """
        result = []
        in_string = False
        in_rem = False
        i = 0
        
        while i < len(code):
            char = code[i]
            
            if char == '"' and not in_rem:
                in_string = not in_string
                result.append(char)
            elif in_string or in_rem:
                # Keep everything in strings and after REM
                result.append(char)
            elif char in ' \t':
                # Look ahead and behind to decide if we need this space
                prev_char = result[-1] if result else ''
                next_char = code[i + 1] if i + 1 < len(code) else ''
                
                # Keep space around operators for readability
                if prev_char in '=<>+-*/' or next_char in '=<>+-*/':
                    if result and result[-1] != ' ':
                        result.append(' ')
                # Keep space between keywords/identifiers
                elif prev_char.isalnum() and next_char.isalpha():
                    if result and result[-1] != ' ':
                        result.append(' ')
            else:
                result.append(char)
                # Check if we just completed REM keyword
                if len(result) >= 3:
                    last_three = ''.join(result[-3:])
                    if last_three.upper() == 'REM' and (len(result) == 3 or not result[-4].isalpha()):
                        in_rem = True
            
            i += 1
        
        return ''.join(result).strip()
    
    def delete_line(self, line_num: int) -> bool:
        """Delete a specific line number."""
        return self.memory.delete_program_line(line_num)
    
    def get_line(self, line_num: int) -> Optional[str]:
        """Get the detokenized code for a specific line number."""
        lines = self.memory.get_program_lines()
        for num, tokens in lines:
            if num == line_num:
                return detokenize(tokens)
        return None
    
    def get_all_lines(self) -> List[Tuple[int, str]]:
        """Get all lines detokenized and sorted by line number."""
        lines = self.memory.get_program_lines()
        return [(num, detokenize(tokens)) for num, tokens in lines]
    
    def list_program(self) -> None:
        """Display the current program with formatted line numbers."""
        lines = self.get_all_lines()
        if not lines:
            print("No program in memory")
            return
        
        for line_num, code in lines:
            print(f"{line_num:5d} {code}")
    
    def clear_program(self) -> None:
        """Clear all program lines."""
        self.memory.clear_program()
        print("Program cleared")
    
    def save_to_file(self, filename: str) -> None:
        """
        Save program to file in ASCII format (detokenized).
        """
        if not filename.lower().endswith('.bas'):
            filename += '.bas'
        
        try:
            lines = self.get_all_lines()
            with open(filename, 'w') as f:
                for line_num, code in lines:
                    f.write(f"{line_num} {code}\n")
            print(f"Program saved to {filename}")
        except IOError as e:
            print(f"Error saving file: {e}")
    
    def get_memory_usage(self) -> int:
        """Return number of bytes used by the program."""
        page = self.memory.read_int16(0x0206)  # HEADER_PAGE
        return self.memory.program_top - page
    
    def __len__(self) -> int:
        """Return the number of lines in the program."""
        return len(self.memory.get_program_lines())
    
    def __bool__(self) -> bool:
        """Return True if program has any lines."""
        return len(self) > 0
