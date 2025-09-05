import re
import subprocess
import os
from typing import Dict, Optional, Any, Tuple

from lark import Lark, exceptions

from basicTransformer import BASIC_GRAMMAR, BasicTransformer

class ZenBasicRepl:
    def __init__(self):
        self.program_lines: Dict[int, str] = {}  # Line number -> code
        self.variables: Dict[str, Tuple[Any, str]] = {}      # Variable storage
        self.running = True
        self.parser = Lark(BASIC_GRAMMAR)
        self.turbo = False
        self.memory = bytearray(65536)
        self.next_var_address = 0x0800  # Start of variable area
        self.var_table: Dict[str, Tuple[int, int]] = {}  # name -> (address, size)

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
        if code.strip():
            self.program_lines[line_num] = code
            print(f"Line {line_num} stored")
        else:
            # Empty line deletes the line number
            if line_num in self.program_lines:
                del self.program_lines[line_num]
                print(f"Line {line_num} deleted")

    def store_variable_in_memory(self, name: str, value: Any, var_type: str) -> None:
        """Store a variable in memory and update the variable table"""
        if var_type == 'integer':
            if name not in self.var_table:
                # Allocate new space
                address = self.next_var_address
                size = 2  # 16-bit integer = 2 bytes
                self.var_table[name] = (address, size)
                self.next_var_address += size
                print(f"Allocated {name} at address ${address:04X}")
            else:
                # Use existing space
                address, size = self.var_table[name]
                
            # Store the value
            self.store_int16(address, int(value))
            print(f"Stored {value} in memory at ${address:04X}")

    def store_int16(self, address: int, value: int) -> None:
        """Store 16-bit integer at address, little endian"""
        value = int(value) & 0xFFFF  # Clamp to 16-bit
        self.memory[address] = value & 0xFF        # Low byte first
        self.memory[address + 1] = (value >> 8) & 0xFF  # High byte second

    def execute_immediate_command(self, command: str):
        """Execute immediate mode commands (no line number)"""
        # Keep original command for things that need it (like filenames)
        original_command = command
        command_upper = command.strip().upper()
        
        if command_upper == "LIST":
            self.list_program()
        elif command_upper == "RUN":
            self.run_program()
        elif command_upper == "NEW":
            self.new_program()
        elif command_upper == "VARS":
            self.list_variables()
        elif command_upper == "TURBO":
            self.turbo = True
            print("Turbo mode enabled")
        elif command_upper == "SLOW":
            self.turbo = False
            print("Turbo mode disabled")
        elif command_upper == "CLS" or command_upper == "CLEAR":
            self.clear_screen()
        elif command_upper.startswith("DUMP"):
            parts = original_command.split()
            if len(parts) >= 2:
                try:
                    start_addr = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                    self.dump_memory(start_addr)
                except ValueError:
                    print("Invalid address")
            else:
                self.dump_memory(0x0800)  # Default to variable area
        elif command_upper.startswith("SAVE"):
            # Use original command to preserve filename case
            parts = original_command.split(maxsplit=1)
            if len(parts) < 2:
                print("Error: SAVE requires a filename")
            else:
                filename = parts[1].strip()
                if not filename.lower().endswith('.bas'):
                    filename += '.bas'

                try:
                    with open(filename, 'w') as f:
                        for line_num in sorted(self.program_lines.keys()):
                            # Write exactly what was stored - line number + preserved content
                            f.write(f"{line_num}{self.program_lines[line_num]}\n")
                    print(f"Program saved to {filename}")
                except IOError as e:
                    print(f"Error saving file: {e}")

        elif command_upper == "QUIT" or command_upper == "EXIT":
            self.running = False
            print("Goodbye!")
        else:
            try:
                # Use original command for parsing to preserve case
                tree = self.parser.parse(original_command)
                transformer = BasicTransformer(self.variables, self.turbo)
                transformer.repl_instance = self
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
            print(f"{var_name} = {value[0]}")
    
    def run_program(self):
        """Run the stored program"""
        if not self.program_lines:
            print("No program to run")
            return
            
        print("Running program...")
        for line_num in sorted(self.program_lines.keys()):
            code = self.program_lines[line_num]
            print(f"Executing line {line_num}: {code}")
            
            # Try to execute the code using our parser
            try:
                tree = self.parser.parse(code)
                transformer = BasicTransformer(self.variables, self.turbo)
                transformer.repl_instance = self
                result = transformer.transform(tree)
                if result:  # Only print if there's a result
                    print(result)
            except Exception as e:
                print(f"Runtime error at line {line_num}: {e}")
                break  # Stop execution on error
    
    def new_program(self):
        """Clear the current program"""
        self.program_lines.clear()
        self.variables.clear()
        print("Program cleared")

    def clear_screen(self):
        subprocess.run(['clear'] if os.name == 'posix' else ['cmd', '/c', 'cls'])

    def dump_memory(self, start_addr: int, length: int = 64) -> None:
        print(f"Memory dump starting at ${start_addr:04X}:")
        for i in range(0, length, 16):
            addr = start_addr + i
            if addr >= 65536:
                break
            
            # Address
            line = f"${addr:04X}: "
            
            # Hex bytes
            for j in range(16):
                if addr + j < 65536:
                    line += f"{self.memory[addr + j]:02X} "
                else:
                    line += "   "
            
            print(line)

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
