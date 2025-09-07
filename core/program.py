"""
Program storage and management for ZenBasic
Handles line-numbered BASIC programs with authentic whitespace preservation
"""
from typing import Dict, List, Optional


class ProgramStore:
    """
    Manages line-numbered BASIC program storage.
    Lines are stored exactly as entered, preserving all formatting crimes.
    """
    
    def __init__(self):
        self.lines: Dict[int, str] = {}  # Line number -> code
    
    def add_line(self, line_num: int, code: str) -> None:
        """
        Store a program line. Empty code deletes the line.
        Preserves all whitespace because we're not monsters.
        """
        if code.strip():
            self.lines[line_num] = code
            print(f"Line {line_num} stored")
        else:
            # Empty line deletes the line number
            if line_num in self.lines:
                del self.lines[line_num]
                print(f"Line {line_num} deleted")
    
    def delete_line(self, line_num: int) -> bool:
        """Delete a specific line number. Returns True if line existed."""
        if line_num in self.lines:
            del self.lines[line_num]
            return True
        return False
    
    def get_line(self, line_num: int) -> Optional[str]:
        """Get the code for a specific line number."""
        return self.lines.get(line_num)
    
    def get_all_lines(self) -> List[tuple[int, str]]:
        """Get all lines sorted by line number."""
        return [(num, self.lines[num]) for num in sorted(self.lines.keys())]
    
    def list_program(self) -> None:
        """Display the current program with formatted line numbers."""
        if not self.lines:
            print("No program in memory")
            return
        
        for line_num in sorted(self.lines.keys()):
            print(f"{line_num:5d} {self.lines[line_num]}")
    
    def clear_program(self) -> None:
        """Clear all program lines."""
        self.lines.clear()
        print("Program cleared")
    
    def save_to_file(self, filename: str) -> None:
        """
        Save program to file, preserving exact formatting.
        Automatically appends .bas extension if missing.
        """
        if not filename.lower().endswith('.bas'):
            filename += '.bas'
        
        try:
            with open(filename, 'w') as f:
                for line_num in sorted(self.lines.keys()):
                    # Write exactly what was stored - line number + preserved content
                    f.write(f"{line_num}{self.lines[line_num]}\n")
            print(f"Program saved to {filename}")
        except IOError as e:
            print(f"Error saving file: {e}")
    
    def load_from_file(self, filename: str) -> None:
        """
        Load program from file.
        TODO: Implement when LOAD command is added.
        """
        # This will parse the file and reconstruct the program
        # maintaining the exact whitespace from the file
        pass
    
    def __len__(self) -> int:
        """Return the number of lines in the program."""
        return len(self.lines)
    
    def __bool__(self) -> bool:
        """Return True if program has any lines."""
        return bool(self.lines)
