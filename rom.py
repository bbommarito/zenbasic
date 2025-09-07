"""
NCDOS (NinthCircle DOS) ROM System
Welcome to the 9th Circle of Programming Hell

This is the system ROM that handles:
- Screen output (from screen memory)
- Keyboard input
- Disk I/O
- System vectors

Lives at $F000-$FFFF in our memory map
Because even in Hell, we respect memory boundaries
"""
import threading
import time
import sys
import os
from typing import Optional, Callable
from queue import Queue


# ROM vectors (like BBC Micro/C64)
# These are memory addresses that contain JMP instructions to ROM routines
OSWRCH = 0xFFEE  # Write character
OSRDCH = 0xFFE0  # Read character  
OSBYTE = 0xFFF4  # Misc OS functions
OSWORD = 0xFFF1  # More OS functions
OSFILE = 0xFFDD  # File operations
OSFIND = 0xFFCE  # Open/close files
OSGBPB = 0xFFD1  # Block get/put
OSARGS = 0xFFDA  # File arguments

# Zero page locations for OS workspace
OS_WORKSPACE = 0x00A0  # $A0-$CF reserved for OS

# NCDOS signature
NCDOS_SIGNATURE = b'NCDOS'  # Our mark of damnation


class NCDOSRom:
    """
    The ROM that makes ZenBasic into NCDOS.
    Monitors memory, handles I/O, provides system calls.
    Abandon all hope, ye who enter here.
    """
    
    def __init__(self, memory_manager):
        """
        Initialize the ROM with access to system memory.
        
        Args:
            memory_manager: The MemoryManager instance
        """
        self.memory = memory_manager
        self.running = False
        self.keyboard_buffer = Queue(maxsize=256)
        self.screen_thread = None
        self.keyboard_thread = None
        
        # Install ROM vectors
        self._install_vectors()
        
        # Screen state
        self.last_screen = ""
        self.cursor_visible = True
        self.cursor_blink_time = 0
        
        # Disk system (to be initialized)
        self.disk = None
        
    def _install_vectors(self):
        """
        Install jump vectors in high memory.
        In a real system these would be JMP instructions to ROM code.
        We'll store the NCDOS signature.
        """
        # Write NCDOS signature to indicate ROM is present
        # At $FFF8: "NCDOS" (our unholy mark)
        for i, byte in enumerate(NCDOS_SIGNATURE):
            self.memory.memory[0xFFF8 + i] = byte
            
        # Version number at $FFFD (1.0)
        self.memory.memory[0xFFFD] = 0x10
        
        # Boot vector at $FFFC-$FFFD (normally reset vector)
        self.memory.store_int16(0xFFFC, 0xF000)  # ROM entry point
        
    def start(self):
        """
        Start the ROM services (screen refresh, keyboard scan).
        Welcome to Hell. The thermostat is broken.
        """
        self.running = True
        
        # Print boot message to screen memory
        self._write_boot_message()
        
        # Start screen refresh thread
        self.screen_thread = threading.Thread(target=self._screen_service, daemon=True)
        self.screen_thread.start()
        
        # Start keyboard scan thread
        self.keyboard_thread = threading.Thread(target=self._keyboard_service, daemon=True)
        self.keyboard_thread.start()
        
    def stop(self):
        """
        Stop ROM services.
        You can check out any time you like, but...
        """
        self.running = False
        if self.screen_thread:
            self.screen_thread.join(timeout=1)
        if self.keyboard_thread:
            self.keyboard_thread.join(timeout=1)
            
    def _write_boot_message(self):
        """
        Write NCDOS boot message to screen memory.
        """
        message = "NCDOS 1.0 - NinthCircle DOS"
        message2 = "Abandon hope, all ye who code here"
        
        # Write to center of screen
        screen_start = 0x0400
        
        # First line at row 10
        addr = screen_start + (10 * 40) + (40 - len(message)) // 2
        for char in message:
            if addr < 0x0800:
                self.memory.memory[addr] = ord(char)
                addr += 1
                
        # Second line at row 11
        addr = screen_start + (11 * 40) + (40 - len(message2)) // 2
        for char in message2:
            if addr < 0x0800:
                self.memory.memory[addr] = ord(char)
                addr += 1
                
    def _screen_service(self):
        """
        Background thread that monitors screen memory and updates display.
        Runs at ~30 Hz like a real CRT refresh.
        Even in Hell, we maintain proper refresh rates.
        """
        while self.running:
            try:
                # Get current screen content from memory
                screen_content = self._read_screen_memory()
                
                # Only update if changed
                if screen_content != self.last_screen:
                    self._update_display(screen_content)
                    self.last_screen = screen_content
                    
                # Blink cursor
                self.cursor_blink_time += 1
                if self.cursor_blink_time >= 15:  # ~0.5 second blink
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_blink_time = 0
                    
                # 30 Hz refresh rate (authentic!)
                time.sleep(0.033)
                
            except Exception as e:
                # ROM shouldn't crash, even in Hell
                pass
                
    def _keyboard_service(self):
        """
        Background thread that scans for keyboard input.
        In a real system this would be interrupt-driven.
        In Hell, we poll. Forever.
        """
        # This is tricky in Python - we'd need a non-blocking input method
        # For now, this is a placeholder
        while self.running:
            time.sleep(0.01)  # Scan at 100Hz
            # TODO: Implement non-blocking keyboard input
            
    def _read_screen_memory(self) -> str:
        """
        Read the screen memory region and convert to displayable text.
        
        Returns:
            String representation of screen
        """
        # Screen memory is at $0400-$07FF (1KB)
        # 40x25 character display (BBC Micro Mode 7 style)
        SCREEN_START = 0x0400
        SCREEN_WIDTH = 40
        SCREEN_HEIGHT = 25
        
        lines = []
        for row in range(SCREEN_HEIGHT):
            line_chars = []
            for col in range(SCREEN_WIDTH):
                addr = SCREEN_START + (row * SCREEN_WIDTH) + col
                char_code = self.memory.memory[addr]
                
                # Convert to displayable character
                if 32 <= char_code <= 126:
                    line_chars.append(chr(char_code))
                elif char_code == 0:
                    line_chars.append(' ')
                else:
                    line_chars.append('.')
                    
            lines.append(''.join(line_chars))
            
        return '\n'.join(lines)
        
    def _update_display(self, content: str):
        """
        Update the actual display with screen memory content.
        For now, just print to console with a hellish border.
        
        Args:
            content: Screen content as string
        """
        # Clear screen (platform-specific)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Draw border with NCDOS branding
        print("╔" + "═" * 18 + " NCDOS " + "═" * 18 + "╗")
        for line in content.split('\n'):
            # Ensure line is exactly 40 chars
            display_line = line[:40].ljust(40)
            print("║" + display_line + "║")
        print("╚" + "═" * 40 + "╝")
        
        # Show cursor position
        cursor_addr = self.memory.screen_cursor if hasattr(self.memory, 'screen_cursor') else 0x0400
        cursor_pos = cursor_addr - 0x0400
        cursor_row = cursor_pos // 40
        cursor_col = cursor_pos % 40
        
        if self.cursor_visible:
            # Move cursor to position (ANSI escape codes)
            print(f"\033[{cursor_row + 2};{cursor_col + 2}H", end='')
            
    # System call implementations
    
    def oswrch(self, char: int):
        """
        OSWRCH - Write character to screen.
        Even in Hell, we support proper I/O.
        
        Args:
            char: Character code to write
        """
        if hasattr(self.memory, 'write_to_screen'):
            self.memory.write_to_screen(chr(char))
        else:
            # Direct write to screen memory at cursor
            cursor = getattr(self.memory, 'screen_cursor', 0x0400)
            if cursor < 0x0800:  # Within screen memory
                self.memory.memory[cursor] = char
                self.memory.screen_cursor = cursor + 1
                
    def osrdch(self) -> int:
        """
        OSRDCH - Read character from keyboard.
        
        Returns:
            Character code (blocks until available)
        """
        # Block until we have a character
        if not self.keyboard_buffer.empty():
            return self.keyboard_buffer.get()
        return 0  # No input available
        
    def osbyte(self, a: int, x: int, y: int) -> tuple[int, int, int]:
        """
        OSBYTE - Miscellaneous OS functions.
        
        Args:
            a: Function number
            x: Parameter
            y: Parameter
            
        Returns:
            Tuple of (a, x, y) with results
        """
        if a == 0x7A:  # Scan keyboard
            # Return key if available
            if not self.keyboard_buffer.empty():
                key = self.keyboard_buffer.get()
                return (key, 0, 0)
            return (0xFF, 0xFF, 0)  # No key (in Hell, no one can hear you type)
            
        elif a == 0x02:  # Select input stream
            # For now, ignore
            pass
            
        elif a == 0x03:  # Select output stream  
            # For now, ignore
            pass
            
        elif a == 0x66:  # Number of the Beast - NCDOS special!
            # Return 666 to confirm we're in Hell
            return (0x02, 0x9A, 0x00)  # 666 in little-endian
            
        return (a, x, y)
