"""
Command registry and handlers for ZenBasic
Because if/elif chains are where good code goes to die
"""
from typing import Dict, Callable, Optional, Protocol, Any
import re
import inspect
import os


class ReplProtocol(Protocol):
    """Protocol defining what commands need from the REPL"""
    program_store: Any
    variables: Dict[str, Any]
    memory_manager: Any
    turbo: bool
    running: bool
    disk: Optional[Any]  # NCDOS disk system
    
    def run_program(self) -> None: ...
    def new_program(self) -> None: ...
    def list_variables(self) -> None: ...
    def clear_screen(self) -> None: ...


class CommandRegistry:
    """
    Registry for BASIC commands.
    No more if/elif chains. We're civilized now.
    """
    
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.command_help: Dict[str, str] = {}
        self.register_built_in_commands()
    
    def register(self, name: str, handler: Callable, help_text: str = "") -> None:
        """Register a command handler"""
        self.commands[name.upper()] = handler
        if help_text:
            self.command_help[name.upper()] = help_text
    
    def execute(self, command_line: str, repl: ReplProtocol) -> bool:
        """
        Execute a command if it matches a registered handler.
        Returns True if command was handled, False otherwise.
        """
        command_upper = command_line.strip().upper()
        parts = command_line.strip().split(maxsplit=1)
        command = parts[0].upper() if parts else ""
        
        # Try exact match first
        if command in self.commands:
            handler = self.commands[command]
            # Check if handler accepts command_line argument
            sig = inspect.signature(handler)
            if len(sig.parameters) > 1:
                handler(repl, command_line)
            else:
                handler(repl)
            return True
        
        # Try prefix match for commands that take arguments
        for cmd_name, handler in self.commands.items():
            if command_upper.startswith(cmd_name + " ") or command_upper == cmd_name:
                # Check if handler accepts command_line argument
                sig = inspect.signature(handler)
                if len(sig.parameters) > 1:
                    handler(repl, command_line)
                else:
                    handler(repl)
                return True
        
        return False
    
    def register_built_in_commands(self) -> None:
        """Register all built-in BASIC commands"""
        self.register("LIST", cmd_list, "List the current program")
        self.register("RUN", cmd_run, "Execute the stored program")
        self.register("NEW", cmd_new, "Clear the current program and variables")
        self.register("VARS", cmd_vars, "List all variables and their values")
        self.register("TURBO", cmd_turbo, "YOU GET AN ALU! AND YOU GET AN ALU! EVERYBODY GETS AN ALU!")
        self.register("SLOW", cmd_slow, "ALUs are the Devil's Work")
        self.register("CLS", cmd_cls, "Clear the screen")
        self.register("CLEAR", cmd_clear, "Clear all variables")
        self.register("MEMORY", cmd_memory, "Display memory map and usage")
        self.register("MAP", cmd_memory, "Display memory map (alias for MEMORY)")
        self.register("DUMP", cmd_dump, "Dump memory contents (DUMP [address])")
        self.register("SYMBOLS", cmd_symbols, "Display symbol table")
        self.register("SAVE", cmd_save, "Save program to disk (SAVE filename)")
        self.register("LOAD", cmd_load, "Load program from disk (LOAD filename)")
        self.register("CATALOG", cmd_catalog, "List files on disk")
        self.register("CAT", cmd_catalog, "List files on disk (alias for CATALOG)")
        self.register("DELETE", cmd_delete, "Delete file from disk (DELETE filename)")
        self.register("QUIT", cmd_quit, "Exit the interpreter")
        self.register("EXIT", cmd_quit, "Exit the interpreter (alias for QUIT)")
        self.register("HELP", cmd_help, "Show available commands")


# Command implementations - each is a clean, separate function

def cmd_list(repl: ReplProtocol) -> None:
    """List the current program"""
    repl.program_store.list_program()


def cmd_run(repl: ReplProtocol) -> None:
    """Execute the stored program"""
    repl.run_program()


def cmd_new(repl: ReplProtocol) -> None:
    """Clear program and variables"""
    repl.new_program()


def cmd_vars(repl: ReplProtocol) -> None:
    """List all variables"""
    repl.list_variables()


def cmd_turbo(repl: ReplProtocol) -> None:
    """Enable turbo mode"""
    repl.turbo = True
    print("Turbo mode enabled")


def cmd_slow(repl: ReplProtocol) -> None:
    """Disable turbo mode"""
    repl.turbo = False
    print("Turbo mode disabled")


def cmd_cls(repl: ReplProtocol) -> None:
    """Clear the screen"""
    repl.clear_screen()


def cmd_clear(repl: ReplProtocol) -> None:
    """Clear all variables (BBC BASIC behavior)"""
    repl.memory_manager.clear_variables()
    print("Variables cleared")


def cmd_memory(repl: ReplProtocol) -> None:
    """Display memory map and usage"""
    print(repl.memory_manager.get_memory_map_info())


def cmd_symbols(repl: ReplProtocol) -> None:
    """Display symbol table"""
    repl.memory_manager.dump_symbol_table()


def cmd_dump(repl: ReplProtocol, command_line: str) -> None:
    """Dump memory contents"""
    parts = command_line.split()
    if len(parts) >= 2:
        try:
            # Support hex (0x prefix, & prefix, $ prefix) or decimal
            addr_str = parts[1]
            if addr_str.startswith('0x') or addr_str.startswith('0X'):
                start_addr = int(addr_str, 16)
            elif addr_str.startswith('&'):
                # BBC BASIC style hex
                start_addr = int(addr_str[1:], 16)
            elif addr_str.startswith('$'):
                # 6502 assembly style hex
                start_addr = int(addr_str[1:], 16)
            else:
                start_addr = int(addr_str)
            repl.memory_manager.dump(start_addr)
        except ValueError:
            print(f"Invalid address: {parts[1]}")
    else:
        # Default to variable area
        repl.memory_manager.dump(0x0800)


def cmd_save(repl: ReplProtocol, command_line: str) -> None:
    """Save program to disk using NCDOS"""
    parts = command_line.split(maxsplit=1)
    if len(parts) < 2:
        print("Error: SAVE requires a filename")
        return
    
    filename = parts[1].strip().upper()
    
    # Add .BAS extension if not present
    if '.' not in filename:
        filename += '.BAS'
    
    # Check if we have disk system
    if not hasattr(repl, 'disk') or repl.disk is None:
        # Fall back to regular file save
        print("No disk system - saving to regular file")
        repl.program_store.save_to_file(filename.lower())
        return
    
    # Get program as tokenized bytes or text
    lines = repl.program_store.get_all_lines()
    if not lines:
        print("No program in memory")
        return
    
    # Create program text
    program_text = ""
    for line_num, code in lines:
        program_text += f"{line_num} {code}\n"
    
    # Save to NCDOS disk
    if repl.disk.save_file(filename, program_text.encode('ascii')):
        print(f"Saved {len(program_text)} bytes to {filename}")
    else:
        print(f"Error saving {filename} - disk may be full")


def cmd_quit(repl: ReplProtocol) -> None:
    """Exit the interpreter"""
    repl.running = False
    print("Goodbye!")


def cmd_load(repl: ReplProtocol, command_line: str) -> None:
    """Load program from disk using NCDOS"""
    parts = command_line.split(maxsplit=1)
    if len(parts) < 2:
        print("Error: LOAD requires a filename")
        return
    
    filename = parts[1].strip().upper()
    
    # Add .BAS extension if not present
    if '.' not in filename:
        filename += '.BAS'
    
    # Check if we have disk system
    if not hasattr(repl, 'disk') or repl.disk is None:
        # Fall back to regular file load
        print("No disk system - loading from regular file")
        # Would implement regular file load here
        return
    
    # Load from NCDOS disk
    data = repl.disk.load_file(filename)
    if data is None:
        print(f"File not found: {filename}")
        return
    
    # Clear current program
    repl.new_program()
    
    # Parse and store lines
    try:
        text = data.decode('ascii')
        line_count = 0
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # Process the line through the REPL
                # This will handle line numbering and tokenization
                if hasattr(repl, 'process_line'):
                    repl.process_line(line)
                    line_count += 1
        print(f"Loaded {line_count} lines from {filename}")
    except Exception as e:
        print(f"Error loading program: {e}")


def cmd_catalog(repl: ReplProtocol) -> None:
    """List files on disk"""
    if not hasattr(repl, 'disk') or repl.disk is None:
        print("No disk system available")
        return
    
    files = repl.disk.list_files()
    if not files:
        print("No files on disk")
        return
    
    print("Files on disk:")
    total_size = 0
    for filename, size in sorted(files):
        print(f"  {filename:<12} {size:>6} bytes")
        total_size += size
    
    # Calculate free space
    used_sectors = total_size // 256 + (1 if total_size % 256 else 0)
    total_sectors = 40 * 16  # 40 tracks, 16 sectors per track
    free_sectors = total_sectors - used_sectors - 16  # Minus system tracks
    
    print(f"\nTotal: {len(files)} files, {total_size} bytes")
    print(f"Free: {free_sectors * 256} bytes")


def cmd_delete(repl: ReplProtocol, command_line: str) -> None:
    """Delete file from disk"""
    parts = command_line.split(maxsplit=1)
    if len(parts) < 2:
        print("Error: DELETE requires a filename")
        return
    
    filename = parts[1].strip().upper()
    
    # Add .BAS extension if not present and no extension given
    if '.' not in filename:
        filename += '.BAS'
    
    if not hasattr(repl, 'disk') or repl.disk is None:
        print("No disk system available")
        return
    
    if repl.disk.delete_file(filename):
        print(f"Deleted {filename}")
    else:
        print(f"File not found: {filename}")


def cmd_help(repl: ReplProtocol) -> None:
    """Show available commands"""
    # Get the registry from the repl
    if hasattr(repl, 'command_registry'):
        registry = repl.command_registry
        print("Available commands:")
        
        # Get unique commands (skip aliases)
        shown_handlers = set()
        commands = []
        
        for name, handler in sorted(registry.commands.items()):
            if handler not in shown_handlers:
                shown_handlers.add(handler)
                help_text = registry.command_help.get(name, "")
                commands.append(f"  {name:<10} - {help_text}")
        
        print("\n".join(commands))
    else:
        print("Help not available")
