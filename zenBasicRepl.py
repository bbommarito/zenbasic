import re
from typing import Dict, Optional, Any, Tuple

from lark import Lark, exceptions

from basicTransformer import BASIC_GRAMMAR, BasicTransformer

class ZenBasicRepl:
    def __init__(self):
        self.program_lines: Dict[int, str] = {}  # Line number -> code
        self.variables: Dict[str, Any] = {}      # Variable storage
        self.running = True
        self.parser = Lark(BASIC_GRAMMAR)

    def print_banner(self):
        """Print startup banner like original BBC BASIC"""
        print("ZenBasic")
        print("Ready")
        print()

    def parse_line_number(self, line: str) -> Tuple[Optional[int], str]:
        """Extract line number if present, return (line_num, remaining_code)"""
        line = line.strip()
        if not line:
            return None, ""
            
        # Check if line starts with a number
        match = re.match(r'^(\d+)\s*(.*)', line)
        if match:
            return int(match.group(1)), match.group(2)
        return None, line

    def store_program_line(self, line_num: int, code: str):
        """Store a numbered program line"""
        if code.strip():
            self.program_lines[line_num] = code
            print(f"Line {line_num} stored")
        else:
            # Empty line deletes the line number
            if line_num in self.program_lines:
                del self.program_lines[line_num]
                print(f"Line {line_num} deleted")

    def execute_immediate_command(self, command: str):
        """Execute immediate mode commands (no line number)"""
        command = command.strip().upper()
        
        if command == "LIST":
            self.list_program()
        elif command == "RUN":
            self.run_program()
        elif command == "NEW":
            self.new_program()
        elif command == "VARS":
            self.list_variables()
        elif command == "QUIT" or command == "EXIT":
            self.running = False
            print("Goodbye!")
        else:
            try:
                tree = self.parser.parse(command)
                transformer = BasicTransformer(self.variables)
                result = transformer.transform(tree)
                print(result)
            except exceptions.LarkError as e:
                print(f"Syntax error: {e}")
            except Exception as e:
                print(f"Error: {e}")
    
    def list_program(self):
        """List the current program"""
        if not self.program_lines:
            print("No program in memory")
            return
            
        for line_num in sorted(self.program_lines.keys()):
            print(f"{line_num:5d} {self.program_lines[line_num]}")

    def list_variables(self):
        """List current variables and their values"""
        if not self.variables:
            print("No variables set")
            return
            
        print("Variables:")
        for var_name, value in sorted(self.variables.items()):
            print(f"{var_name} = {value}")
    
    def run_program(self):
        """Run the stored program"""
        if not self.program_lines:
            print("No program to run")
            return
            
        print("Running program...")
        # TODO: Implement actual program execution
        for line_num in sorted(self.program_lines.keys()):
            print(f"[Would execute: {line_num} {self.program_lines[line_num]}]")
        print("Program finished")
    
    def new_program(self):
        """Clear the current program"""
        self.program_lines.clear()
        self.variables.clear()
        print("Program cleared")
    
    def repl(self):
        """Main Read-Eval-Print Loop"""
        self.print_banner()
        
        while self.running:
            try:
                # Read
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Parse for line number
                line_num, code = self.parse_line_number(user_input)
                
                if line_num is not None:
                    # Store numbered line
                    self.store_program_line(line_num, code)
                else:
                    # Execute immediate command
                    self.execute_immediate_command(code)
                    
            except KeyboardInterrupt:
                print("\nUse QUIT to exit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
