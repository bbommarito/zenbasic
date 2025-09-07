"""
NCDOS Command Prompt (ROM-based Version)
All I/O goes through ROM/BIOS vectors

This is the authentic way - just like real 8-bit computers
where DOS calls BIOS routines for all hardware access.
"""

import os
import sys
import threading
import time
from typing import Optional, Dict, List, Callable
from core.memory import MemoryManager
from ncdos.disk import NCDOSDisk


class NCDOSWithROM:
    """
    NCDOS that uses ROM/BIOS for all I/O.
    All output goes to screen memory, all input through keyboard buffer.
    """
    
    def __init__(self):
        """Initialize NCDOS with full ROM/BIOS system."""
        # Create memory manager (includes screen memory at $0400-$07FF)
        self.memory = MemoryManager()
        
        # Initialize disk drives (A: and B:)
        self.drives = {
            'A': NCDOSDisk(os.path.join(os.path.dirname(__file__), "drive_a.dsk")),
            'B': NCDOSDisk(os.path.join(os.path.dirname(__file__), "drive_b.dsk"))
        }
        self.current_drive = 'A'
        
        # Screen refresh thread
        self.screen_thread = None
        self.running = True
        
        # Keyboard input buffer
        self.keyboard_buffer = []
        self.input_line = ""
        
        # Command registry
        self.commands = self._register_commands()
        
    def _register_commands(self) -> Dict[str, Callable]:
        """Register DOS command handlers."""
        return {
            'DIR': self.cmd_dir,
            'CAT': self.cmd_dir,
            'TYPE': self.cmd_type,
            'DEL': self.cmd_delete,
            'DELETE': self.cmd_delete,
            'COPY': self.cmd_copy,
            'REN': self.cmd_rename,
            'RENAME': self.cmd_rename,
            'CLS': self.cmd_cls,
            'CLEAR': self.cmd_cls,
            'FORMAT': self.cmd_format,
            'A:': self.cmd_drive_a,
            'B:': self.cmd_drive_b,
            'DRIVE': self.cmd_drive_status,
            'BASIC': self.cmd_basic,
            'EDIT': self.cmd_edit,
            'HELP': self.cmd_help,
            'EXIT': self.cmd_exit,
            'QUIT': self.cmd_exit,
        }
    
    def boot(self):
        """Boot NCDOS with ROM/BIOS services."""
        # Clear screen memory
        self.memory.clear_screen()
        
        # Start screen refresh service
        self.screen_thread = threading.Thread(target=self._screen_service, daemon=True)
        self.screen_thread.start()
        
        # Start keyboard service
        self.keyboard_thread = threading.Thread(target=self._keyboard_service, daemon=True)
        self.keyboard_thread.start()
        
        # Display boot message through screen memory
        self.write_string("NCDOS 1.0 - NinthCircle DOS\n")
        self.write_string("64K RAM System\n")
        self.write_string(f"Drive A: {'Present' if self.drives['A'] else 'Empty'}\n")
        self.write_string(f"Drive B: {'Present' if self.drives['B'] else 'Empty'}\n")
        self.write_string("\n")
        
        # Main command loop
        self.command_loop()
    
    def _screen_service(self):
        """
        Background thread that monitors screen memory and updates display.
        This is the "ROM" that refreshes the screen from memory.
        """
        last_screen = ""
        
        while self.running:
            try:
                # Get current screen content from memory
                screen_text = self.memory.get_screen_text()
                
                # Only update if changed
                if screen_text != last_screen:
                    # Clear physical screen
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    # Draw border
                    print("╔" + "═" * 40 + "╗")
                    
                    # Draw screen content
                    lines = screen_text.split('\n')
                    for i in range(25):
                        if i < len(lines):
                            line = lines[i][:40].ljust(40)
                        else:
                            line = " " * 40
                        print("║" + line + "║")
                    
                    print("╚" + "═" * 40 + "╝")
                    print(f"[Drive {self.current_drive}: | F1=Help | F10=Exit]")
                    
                    # Show cursor
                    if hasattr(self.memory, 'screen_cursor'):
                        pos = self.memory.screen_cursor - 0x0400
                        row = pos // 40
                        col = pos % 40
                        # Move cursor to position (ANSI escape codes)
                        print(f"\033[{row + 2};{col + 2}H", end='', flush=True)
                    
                    last_screen = screen_text
                
                # 30 Hz refresh rate (authentic!)
                time.sleep(0.033)
                
            except Exception as e:
                # ROM shouldn't crash
                pass
    
    def _keyboard_service(self):
        """
        Background thread that handles keyboard input.
        In a real system this would be interrupt-driven.
        """
        while self.running:
            try:
                # Get a character (blocking)
                char = self._getch()
                
                if char:
                    # Add to buffer
                    self.keyboard_buffer.append(char)
                    
                    # Echo to screen
                    if char == '\r' or char == '\n':
                        self.write_string('\n')
                        # Process the line
                        self.process_input_line()
                        self.input_line = ""
                    elif char == '\b' or ord(char) == 127:  # Backspace
                        if self.input_line:
                            self.input_line = self.input_line[:-1]
                            # Move cursor back and clear character
                            if self.memory.screen_cursor > 0x0400:
                                self.memory.screen_cursor -= 1
                                self.memory.memory[self.memory.screen_cursor] = 0x20
                    else:
                        self.input_line += char
                        self.write_char(char)
                        
            except Exception:
                pass
    
    def _getch(self):
        """Get a single character from keyboard (platform-specific)."""
        try:
            if os.name == 'nt':
                import msvcrt
                return msvcrt.getch().decode('utf-8', errors='ignore')
            else:
                import termios, tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return char
        except:
            return None
    
    def write_char(self, char: str):
        """Write a character to screen memory (OSWRCH)."""
        if char:
            self.memory.write_to_screen(char)
    
    def write_string(self, text: str):
        """Write a string to screen memory."""
        for char in text:
            self.write_char(char)
    
    def process_input_line(self):
        """Process a complete line of input."""
        if not self.input_line.strip():
            return
        
        # Parse command
        parts = self.input_line.strip().upper().split()
        if not parts:
            return
        
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
    
    def command_loop(self):
        """Main command prompt loop."""
        while self.running:
            # Display prompt
            self.write_string(f"{self.current_drive}>")
            
            # Wait for input to be processed
            while self.running and not self.input_line.endswith('\n'):
                time.sleep(0.01)
    
    # Command implementations
    
    def cmd_dir(self, args: List[str]):
        """DIR - List directory of current drive."""
        drive = args[0] if args and args[0] in ['A:', 'B:'] else self.current_drive
        if ':' in drive:
            drive = drive[0]
        
        if drive not in self.drives:
            self.write_string(f"Invalid drive: {drive}\n")
            return
        
        files = self.drives[drive].list_files()
        
        if not files:
            self.write_string(f"No files on drive {drive}:\n")
            return
        
        self.write_string(f"\nDirectory of {drive}:\n\n")
        
        total_size = 0
        for filename, size in sorted(files):
            parts = filename.split('.')
            name = parts[0] if parts else filename
            ext = parts[1] if len(parts) > 1 else ""
            self.write_string(f"{name:<8} {ext:<3} {size:>7}\n")
            total_size += size
        
        self.write_string(f"\n{len(files)} file(s), {total_size} bytes\n")
        free = (40 * 16 * 256) - total_size - (16 * 256)
        self.write_string(f"{free} bytes free\n")
    
    def cmd_drive_a(self, args: List[str]):
        """Switch to drive A:"""
        self.current_drive = 'A'
        self.write_string("A: selected\n")
    
    def cmd_drive_b(self, args: List[str]):
        """Switch to drive B:"""
        self.current_drive = 'B'
        self.write_string("B: selected\n")
    
    def cmd_drive_status(self, args: List[str]):
        """Show drive status."""
        self.write_string("\nDrive Status:\n")
        for drive_letter in ['A', 'B']:
            if self.drives[drive_letter]:
                files = self.drives[drive_letter].list_files()
                self.write_string(f"  {drive_letter}: {len(files)} files")
                if drive_letter == self.current_drive:
                    self.write_string(" [CURRENT]")
                self.write_string("\n")
            else:
                self.write_string(f"  {drive_letter}: Not mounted\n")
    
    def cmd_format(self, args: List[str]):
        """FORMAT - Format a disk."""
        drive = args[0] if args else self.current_drive
        if ':' in drive:
            drive = drive[0]
        
        if drive not in self.drives:
            self.write_string(f"Invalid drive: {drive}\n")
            return
        
        self.write_string(f"Format drive {drive}:? (Y/N) ")
        # Wait for Y/N response
        # For now, just format
        self.drives[drive].format_disk(f"DISK_{drive}")
        self.write_string(f"\nDrive {drive}: formatted\n")
    
    def cmd_copy(self, args: List[str]):
        """COPY - Copy file (can copy between drives)."""
        if len(args) < 2:
            self.write_string("Syntax: COPY source dest\n")
            return
        
        source = args[0]
        dest = args[1]
        
        # Parse drive specs
        source_drive = self.current_drive
        dest_drive = self.current_drive
        
        if ':' in source:
            source_drive = source[0]
            source = source[2:]
        
        if ':' in dest:
            dest_drive = dest[0]
            dest = dest[2:]
        
        # Load from source drive
        data = self.drives[source_drive].load_file(source)
        if data is None:
            self.write_string(f"File not found: {source_drive}:{source}\n")
            return
        
        # Save to dest drive
        if self.drives[dest_drive].save_file(dest, data):
            self.write_string(f"Copied {source_drive}:{source} to {dest_drive}:{dest}\n")
        else:
            self.write_string("Error copying file\n")
    
    def cmd_type(self, args: List[str]):
        """TYPE - Display file contents."""
        if not args:
            self.write_string("Syntax: TYPE filename\n")
            return
        
        filename = args[0]
        drive = self.current_drive
        
        if ':' in filename:
            drive = filename[0]
            filename = filename[2:]
        
        if '.' not in filename:
            filename += '.TXT'
        
        data = self.drives[drive].load_file(filename)
        if data is None:
            self.write_string(f"File not found: {drive}:{filename}\n")
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
        drive = self.current_drive
        
        if ':' in filename:
            drive = filename[0]
            filename = filename[2:]
        
        if '.' not in filename:
            filename += '.TXT'
        
        if self.drives[drive].delete_file(filename):
            self.write_string(f"Deleted {drive}:{filename}\n")
        else:
            self.write_string(f"File not found: {drive}:{filename}\n")
    
    def cmd_rename(self, args: List[str]):
        """REN/RENAME - Rename file."""
        if len(args) < 2:
            self.write_string("Syntax: REN oldname newname\n")
            return
        
        old_name = args[0]
        new_name = args[1]
        drive = self.current_drive
        
        if ':' in old_name:
            drive = old_name[0]
            old_name = old_name[2:]
        
        data = self.drives[drive].load_file(old_name)
        if data is None:
            self.write_string(f"File not found: {drive}:{old_name}\n")
            return
        
        self.drives[drive].delete_file(old_name)
        
        if self.drives[drive].save_file(new_name, data):
            self.write_string(f"Renamed {drive}:{old_name} to {new_name}\n")
        else:
            self.write_string("Error renaming file\n")
    
    def cmd_cls(self, args: List[str]):
        """CLS - Clear screen."""
        self.memory.clear_screen()
    
    def cmd_basic(self, args: List[str]):
        """BASIC - Load BASIC ROM."""
        self.write_string("Loading BASIC ROM...\n")
        # TODO: Implement BASIC with screen memory I/O
        self.write_string("BASIC not yet implemented for ROM mode\n")
    
    def cmd_edit(self, args: List[str]):
        """EDIT - Load editor ROM."""
        filename = args[0] if args else None
        if filename:
            self.write_string(f"Loading EDITOR ROM with {filename}...\n")
        else:
            self.write_string("Loading EDITOR ROM...\n")
        self.write_string("EDITOR not yet implemented\n")
    
    def cmd_help(self, args: List[str]):
        """HELP - Show commands."""
        self.write_string("\nNCDOS Commands:\n\n")
        self.write_string("  DIR [d:]     - List files\n")
        self.write_string("  TYPE file    - Display file\n")
        self.write_string("  COPY s d     - Copy file\n")
        self.write_string("  DEL file     - Delete file\n")
        self.write_string("  REN old new  - Rename file\n")
        self.write_string("  FORMAT [d:]  - Format disk\n")
        self.write_string("  A: or B:     - Change drive\n")
        self.write_string("  DRIVE        - Drive status\n")
        self.write_string("  CLS          - Clear screen\n")
        self.write_string("  BASIC        - Load BASIC\n")
        self.write_string("  EXIT         - Exit NCDOS\n")
        self.write_string("\nDrive prefix: A:FILE.TXT\n")
    
    def cmd_exit(self, args: List[str]):
        """EXIT - Exit NCDOS."""
        self.write_string("Shutting down NCDOS...\n")
        self.running = False
        if self.screen_thread:
            self.screen_thread.join(timeout=1)
        if self.keyboard_thread:
            self.keyboard_thread.join(timeout=1)
        sys.exit(0)


def main():
    """Main entry point for ROM-based NCDOS."""
    dos = NCDOSWithROM()
    dos.boot()


if __name__ == "__main__":
    main()
