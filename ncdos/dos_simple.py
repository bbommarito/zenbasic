"""
NCDOS Command Prompt (Simplified Version)
Direct to DOS prompt like MS-DOS/CP/M
"""

import os
from typing import Optional, Dict, List, Callable
from ncdos.disk import NCDOSDisk


class NCDOSSimple:
    """
    Simplified NCDOS that boots to A> prompt.
    Uses regular I/O for now, but follows the architecture.
    """
    
    def __init__(self):
        """Initialize NCDOS with disk."""
        self.disk = NCDOSDisk(os.path.join(os.path.dirname(__file__), "ncdos.dsk"))
        self.current_drive = 'A'
        self.running = True
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
            'BASIC': self.cmd_basic,
            'EDIT': self.cmd_edit,
            'HELP': self.cmd_help,
            'EXIT': self.cmd_exit,
            'QUIT': self.cmd_exit,
        }
    
    def boot(self):
        """Boot NCDOS and start command prompt."""
        print("NCDOS 1.0 - NinthCircle DOS")
        print("64K RAM System, 160KB Disk")
        print()
        self.command_loop()
    
    def command_loop(self):
        """Main command prompt loop."""
        while self.running:
            try:
                # Display prompt
                command_line = input(f"{self.current_drive}>").strip()
                
                if not command_line:
                    continue
                
                # Parse command
                parts = command_line.upper().split()
                if not parts:
                    continue
                
                cmd = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                if cmd in self.commands:
                    try:
                        self.commands[cmd](args)
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print(f"Bad command or file name: {cmd}")
                    
            except (EOFError, KeyboardInterrupt):
                print()
                break
    
    def cmd_dir(self, args: List[str]):
        """DIR/CAT - List directory."""
        files = self.disk.list_files()
        
        if not files:
            print("No files found")
            return
        
        print()
        print("Directory of A:")
        print()
        
        total_size = 0
        for filename, size in sorted(files):
            parts = filename.split('.')
            name = parts[0] if parts else filename
            ext = parts[1] if len(parts) > 1 else ""
            print(f"{name:<8} {ext:<3} {size:>7}")
            total_size += size
        
        print(f"\n{len(files)} file(s), {total_size} bytes")
        free = (40 * 16 * 256) - total_size - (16 * 256)
        print(f"{free} bytes free")
    
    def cmd_type(self, args: List[str]):
        """TYPE - Display file contents."""
        if not args:
            print("Syntax: TYPE filename")
            return
        
        filename = args[0]
        if '.' not in filename:
            filename += '.TXT'
        
        data = self.disk.load_file(filename)
        if data is None:
            print(f"File not found: {filename}")
            return
        
        try:
            text = data.decode('ascii')
            print(text, end='')
            if not text.endswith('\n'):
                print()
        except:
            print("File is not a text file")
    
    def cmd_delete(self, args: List[str]):
        """DEL/DELETE - Delete file."""
        if not args:
            print("Syntax: DEL filename")
            return
        
        filename = args[0]
        if '.' not in filename:
            filename += '.TXT'
        
        if self.disk.delete_file(filename):
            print(f"Deleted {filename}")
        else:
            print(f"File not found: {filename}")
    
    def cmd_copy(self, args: List[str]):
        """COPY - Copy file."""
        if len(args) < 2:
            print("Syntax: COPY source dest")
            return
        
        source = args[0]
        dest = args[1]
        
        data = self.disk.load_file(source)
        if data is None:
            print(f"File not found: {source}")
            return
        
        if self.disk.save_file(dest, data):
            print(f"Copied {source} to {dest}")
        else:
            print("Error copying file")
    
    def cmd_rename(self, args: List[str]):
        """REN/RENAME - Rename file."""
        if len(args) < 2:
            print("Syntax: REN oldname newname")
            return
        
        old_name = args[0]
        new_name = args[1]
        
        data = self.disk.load_file(old_name)
        if data is None:
            print(f"File not found: {old_name}")
            return
        
        self.disk.delete_file(old_name)
        
        if self.disk.save_file(new_name, data):
            print(f"Renamed {old_name} to {new_name}")
        else:
            print("Error renaming file")
    
    def cmd_cls(self, args: List[str]):
        """CLS/CLEAR - Clear screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cmd_basic(self, args: List[str]):
        """BASIC - Load BASIC ROM."""
        print("Loading BASIC ROM...")
        print()
        
        # Launch BASIC interpreter
        from core.repl import ZenBasicRepl
        basic = ZenBasicRepl()
        
        # Clear screen and run
        os.system('cls' if os.name == 'nt' else 'clear')
        basic.repl()
        
        print("\nReturned to NCDOS")
    
    def cmd_edit(self, args: List[str]):
        """EDIT - Load editor ROM."""
        filename = args[0] if args else None
        
        if filename:
            print(f"Loading EDITOR ROM with {filename}...")
        else:
            print("Loading EDITOR ROM...")
        
        print("EDITOR not yet implemented")
    
    def cmd_help(self, args: List[str]):
        """HELP - Show available commands."""
        print("\nNCDOS Commands:")
        print()
        print("  DIR/CAT         - List files")
        print("  TYPE filename   - Display file")
        print("  DEL filename    - Delete file")
        print("  COPY src dest   - Copy file")
        print("  REN old new     - Rename file")
        print("  CLS             - Clear screen")
        print("  BASIC           - Load BASIC ROM")
        print("  EDIT [file]     - Load Editor ROM")
        print("  HELP            - This message")
        print("  EXIT            - Exit NCDOS")
        print()
    
    def cmd_exit(self, args: List[str]):
        """EXIT/QUIT - Exit NCDOS."""
        print("Goodbye from the Ninth Circle!")
        self.running = False


def main():
    """Main entry point for NCDOS."""
    dos = NCDOSSimple()
    dos.boot()


if __name__ == "__main__":
    main()
