"""
NCDOS Command Prompt
The primary interface to the Ninth Circle

All I/O goes through ROM vectors to screen memory.
This is the DOS layer that manages everything.
"""

import os
from typing import Optional, Dict, List, Callable
from core.memory import MemoryManager
from ncdos.rom import NCDOSRom, OSWRCH, OSRDCH
from ncdos.disk import NCDOSDisk


class NCDOS:
    """
    The NCDOS command prompt system.
    Boots directly to A> prompt like MS-DOS/CP/M.
    """
    
    def __init__(self):
        """Initialize NCDOS with memory, ROM, and disk."""
        # Create the full system
        self.memory = MemoryManager()
        self.rom = NCDOSRom(self.memory)
        self.disk = NCDOSDisk(os.path.join(os.path.dirname(__file__), "ncdos.dsk"))
        
        # Screen management
        self.screen_cursor = 0x0400  # Start of screen memory
        self.memory.screen_cursor = self.screen_cursor
        
        # Input buffer
        self.input_buffer = []
        
        # Current drive
        self.current_drive = 'A'
        
        # Command handlers
        self.commands = self._register_commands()
        
        # ROM modules (to be loaded)
        self.current_rom_module = None
        
    def _register_commands(self) -> Dict[str, Callable]:
        """Register DOS command handlers."""
        return {
            'DIR': self.cmd_dir,
            'CAT': self.cmd_dir,  # Alias
            'TYPE': self.cmd_type,
            'DEL': self.cmd_delete,
            'DELETE': self.cmd_delete,  # Alias
            'COPY': self.cmd_copy,
            'REN': self.cmd_rename,
            'RENAME': self.cmd_rename,  # Alias
            'CLS': self.cmd_cls,
            'CLEAR': self.cmd_cls,  # Alias
            'BASIC': self.cmd_basic,
            'EDIT': self.cmd_edit,
            'HELP': self.cmd_help,
            'EXIT': self.cmd_exit,
            'QUIT': self.cmd_exit,  # Alias
        }
    
    def boot(self):
        """
        Boot NCDOS and start the command prompt.
        """
        # Start ROM services
        self.rom.start()
        
        # Clear screen
        self.clear_screen()
        
        # Display boot message
        self.write_string("NCDOS 1.0 - NinthCircle DOS\n")
        self.write_string("64K RAM System, 160KB Disk\n")
        self.write_string("\n")
        
        # Main command loop
        self.command_loop()
    
    def write_char(self, char: str):
        """
        Write a character through ROM vector.
        
        Args:
            char: Character to write
        """
        if len(char) > 0:
            self.rom.oswrch(ord(char[0]))
    
    def write_string(self, text: str):
        """
        Write a string through ROM vectors.
        
        Args:
            text: String to write
        """
        for char in text:
            if char == '\n':
                # Handle newline - move to start of next line
                current_pos = self.memory.screen_cursor - 0x0400
                current_row = current_pos // 40
                next_row = current_row + 1
                if next_row >= 25:
                    # Scroll screen
                    self.scroll_screen()
                    self.memory.screen_cursor = 0x0400 + (24 * 40)
                else:
                    self.memory.screen_cursor = 0x0400 + (next_row * 40)
            else:
                self.write_char(char)
    
    def read_line(self) -> str:
        """
        Read a line of input through ROM vectors.
        
        Returns:
            Input line
        """
        line = []
        while True:
            # In a real implementation, this would use OSRDCH
            # For now, we'll use regular input
            char = input()
            return char  # Temporary - should build character by character
    
    def clear_screen(self):
        """Clear the screen memory."""
        for addr in range(0x0400, 0x0800):
            self.memory.memory[addr] = 0x20  # Space
        self.memory.screen_cursor = 0x0400
    
    def scroll_screen(self):
        """Scroll screen up one line."""
        # Copy lines 1-24 to lines 0-23
        for row in range(24):
            for col in range(40):
                src_addr = 0x0400 + ((row + 1) * 40) + col
                dst_addr = 0x0400 + (row * 40) + col
                self.memory.memory[dst_addr] = self.memory.memory[src_addr]
        
        # Clear line 24
        for col in range(40):
            self.memory.memory[0x0400 + (24 * 40) + col] = 0x20
    
    def command_loop(self):
        """Main command prompt loop."""
        while True:
            # Display prompt
            prompt = f"{self.current_drive}>"
            self.write_string(prompt)
            
            # Read command
            try:
                command_line = self.read_line()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not command_line.strip():
                continue
            
            # Parse command
            parts = command_line.strip().upper().split()
            if not parts:
                continue
            
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Execute command
            if cmd in self.commands:
                try:
                    self.commands[cmd](args)
                except Exception as e:
                    self.write_string(f"Error: {e}\n")
            else:
                self.write_string(f"Bad command or file name: {cmd}\n")
    
    # Command implementations
    
    def cmd_dir(self, args: List[str]):
        """DIR/CAT - List directory."""
        files = self.disk.list_files()
        
        if not files:
            self.write_string("No files found\n")
            return
        
        self.write_string("\n")
        self.write_string("Directory of A:\n")
        self.write_string("\n")
        
        total_size = 0
        for filename, size in sorted(files):
            # Format: FILENAME EXT    SIZE
            parts = filename.split('.')
            name = parts[0] if parts else filename
            ext = parts[1] if len(parts) > 1 else ""
            
            line = f"{name:<8} {ext:<3} {size:>7}\n"
            self.write_string(line)
            total_size += size
        
        self.write_string(f"\n{len(files)} file(s), {total_size} bytes\n")
        
        # Calculate free space
        free = (40 * 16 * 256) - total_size - (16 * 256)  # Minus system track
        self.write_string(f"{free} bytes free\n")
    
    def cmd_type(self, args: List[str]):
        """TYPE - Display file contents."""
        if not args:
            self.write_string("Syntax: TYPE filename\n")
            return
        
        filename = args[0]
        if '.' not in filename:
            filename += '.TXT'
        
        data = self.disk.load_file(filename)
        if data is None:
            self.write_string(f"File not found: {filename}\n")
            return
        
        try:
            text = data.decode('ascii')
            self.write_string(text)
            if not text.endswith('\n'):
                self.write_string('\n')
        except:
            self.write_string("File is not a text file\n")
    
    def cmd_delete(self, args: List[str]):
        """DEL/DELETE - Delete file."""
        if not args:
            self.write_string("Syntax: DEL filename\n")
            return
        
        filename = args[0]
        if '.' not in filename:
            filename += '.TXT'
        
        if self.disk.delete_file(filename):
            self.write_string(f"Deleted {filename}\n")
        else:
            self.write_string(f"File not found: {filename}\n")
    
    def cmd_copy(self, args: List[str]):
        """COPY - Copy file."""
        if len(args) < 2:
            self.write_string("Syntax: COPY source dest\n")
            return
        
        source = args[0]
        dest = args[1]
        
        # Load source
        data = self.disk.load_file(source)
        if data is None:
            self.write_string(f"File not found: {source}\n")
            return
        
        # Save to dest
        if self.disk.save_file(dest, data):
            self.write_string(f"Copied {source} to {dest}\n")
        else:
            self.write_string(f"Error copying file\n")
    
    def cmd_rename(self, args: List[str]):
        """REN/RENAME - Rename file."""
        if len(args) < 2:
            self.write_string("Syntax: REN oldname newname\n")
            return
        
        old_name = args[0]
        new_name = args[1]
        
        # Load file
        data = self.disk.load_file(old_name)
        if data is None:
            self.write_string(f"File not found: {old_name}\n")
            return
        
        # Delete old
        self.disk.delete_file(old_name)
        
        # Save as new
        if self.disk.save_file(new_name, data):
            self.write_string(f"Renamed {old_name} to {new_name}\n")
        else:
            self.write_string(f"Error renaming file\n")
    
    def cmd_cls(self, args: List[str]):
        """CLS/CLEAR - Clear screen."""
        self.clear_screen()
    
    def cmd_basic(self, args: List[str]):
        """BASIC - Load BASIC ROM."""
        self.write_string("Loading BASIC ROM...\n")
        
        # Stop ROM services temporarily
        self.rom.stop()
        
        # Launch BASIC interpreter
        from core.repl import ZenBasicRepl
        basic = ZenBasicRepl()
        
        # Replace normal I/O with screen vectors
        # TODO: Make BASIC use OSWRCH/OSRDCH
        
        basic.repl()
        
        # Restart ROM services
        self.rom.start()
        self.write_string("\nReturned to NCDOS\n")
    
    def cmd_edit(self, args: List[str]):
        """EDIT - Load editor ROM."""
        filename = args[0] if args else None
        
        if filename:
            self.write_string(f"Loading EDITOR ROM with {filename}...\n")
        else:
            self.write_string("Loading EDITOR ROM...\n")
        
        self.write_string("EDITOR not yet implemented\n")
    
    def cmd_help(self, args: List[str]):
        """HELP - Show available commands."""
        self.write_string("\nNCDOS Commands:\n")
        self.write_string("\n")
        self.write_string("  DIR/CAT         - List files\n")
        self.write_string("  TYPE filename   - Display file\n")
        self.write_string("  DEL filename    - Delete file\n")
        self.write_string("  COPY src dest   - Copy file\n")
        self.write_string("  REN old new     - Rename file\n")
        self.write_string("  CLS             - Clear screen\n")
        self.write_string("  BASIC           - Load BASIC ROM\n")
        self.write_string("  EDIT [file]     - Load Editor ROM\n")
        self.write_string("  HELP            - This message\n")
        self.write_string("  EXIT            - Exit NCDOS\n")
        self.write_string("\n")
    
    def cmd_exit(self, args: List[str]):
        """EXIT/QUIT - Exit NCDOS."""
        self.write_string("Goodbye from the Ninth Circle!\n")
        self.rom.stop()
        exit(0)


def main():
    """Main entry point for NCDOS."""
    dos = NCDOS()
    dos.boot()


if __name__ == "__main__":
    main()
