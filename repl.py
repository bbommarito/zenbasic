import re
import subprocess
import os
from typing import Dict, Optional, Any, Tuple

from transformer import BasicTransformer
from parser import BasicParser, exceptions
from memory import MemoryManager
from program import ProgramStore
from commands import CommandRegistry

class ZenBasicRepl:
    def __init__(self):
        self.program_store = ProgramStore()  # Line-numbered program storage
        self.variables: Dict[str, Tuple[Any, str]] = {}      # Variable storage
        self.running = True
        self.parser = BasicParser()
        self.turbo = False
        self.memory_manager = MemoryManager()
        self.command_registry = CommandRegistry()

    def print_banner(self):
        """Print startup banner like original BBC BASIC"""
        print("ZenBasic")
        print("Ready")
        print()

    def parse_line_number(self, line: str) -> Tuple[Optional[int], str]:
        """Extract line number if present, return (line_num, remaining_code)"""
        # Don't strip! We need to check the original line for leading numbers
        if not line.strip():
            return None, ""
            
        # Check if line starts with a number (possibly with leading whitespace)
        # This regex captures EVERYTHING after the digits, including precious whitespace
        match = re.match(r'^\s*(\d+)(.*)', line)
        if match:
            # Return line number and EVERYTHING after it (every space, tab, whatever)
            return int(match.group(1)), match.group(2)
        return None, line

    def store_program_line(self, line_num: int, code: str):
        """Store a numbered program line"""
        print(f"Storing line {line_num}: {code}")
        self.program_store.add_line(line_num, code)

    def store_variable_in_memory(self, name: str, value: Any, var_type: str) -> None:
        """Store a variable in memory using the memory manager"""
        if var_type == 'integer':
            size = 2  # 16-bit integer = 2 bytes
            address = self.memory_manager.allocate_variable(name, size)
            if name not in self.variables:
                print(f"Allocated {name} at address ${address:04X}")
                
            # Store the value
            self.memory_manager.store_int16(address, int(value))
            print(f"Stored {value} in memory at ${address:04X}")


    def execute_immediate_command(self, command: str):
        """Execute immediate mode commands (no line number)"""
        # Try command registry first
        if not self.command_registry.execute(command, self):
            # Not a built-in command, try to parse as BASIC statement
            try:
                tree = self.parser.parse(command)
                transformer = BasicTransformer(self.variables, self.turbo)
                transformer.repl_instance = self
                if self.turbo != transformer.arithmetic.turbo:
                    transformer.arithmetic.set_turbo(self.turbo)
                result = transformer.transform(tree)
                print(result)
            except exceptions.LarkError as e:
                print(f"Syntax error: {e}")
            except Exception as e:
                print(f"Error: {e}")
    

    def list_variables(self):
        """List current variables and their values"""
        if not self.variables:
            print("No variables set")
            return
            
        print("Variables:")
        for var_name, value in sorted(self.variables.items()):
            print(f"{var_name} = {value[0]}")
    
    def run_program(self):
        """Run the stored program"""
        if not self.program_store:
            print("No program to run")
            return
            
        print("Running program...")
        for line_num, code in self.program_store.get_all_lines():
            print(f"Executing line {line_num}: {code}")
            
            # Try to execute the code using our parser
            try:
                tree = self.parser.parse(code)
                transformer = BasicTransformer(self.variables, self.turbo)
                transformer.repl_instance = self
                if self.turbo != transformer.arithmetic.turbo:
                    transformer.arithmetic.set_turbo(self.turbo)
                result = transformer.transform(tree)
                if result:  # Only print if there's a result
                    print(result)
            except Exception as e:
                print(f"Runtime error at line {line_num}: {e}")
                break  # Stop execution on error
    
    def new_program(self):
        """Clear the current program"""
        self.program_store.clear_program()
        self.variables.clear()
        self.memory_manager.clear_variables()

    def clear_screen(self):
        subprocess.run(['clear'] if os.name == 'posix' else ['cmd', '/c', 'cls'])


    def repl(self):
        """Main Read-Eval-Print Loop"""
        self.clear_screen()
        self.print_banner()
        
        while self.running:
            try:
                # Read
                input_line = "(turbo) > " if self.turbo else "> "
                user_input = input(input_line)
                
                # Only check if it's empty, don't strip!
                if not user_input.strip():
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
