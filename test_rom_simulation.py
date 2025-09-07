#!/usr/bin/env python3
"""
Test the ROM-based DOS concept with simulated screen output
"""

import os
import time
from core.memory import MemoryManager
from ncdos.disk import NCDOSDisk

def display_screen_memory(memory):
    """Display the contents of screen memory in a bordered window."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Draw border
    print("╔" + "═" * 40 + "╗")
    
    # Get screen content from memory
    for row in range(25):
        line = []
        for col in range(40):
            addr = 0x0400 + (row * 40) + col
            char_code = memory.memory[addr]
            if 32 <= char_code <= 126:
                line.append(chr(char_code))
            else:
                line.append(' ')
        print("║" + ''.join(line) + "║")
    
    print("╚" + "═" * 40 + "╝")
    print("[ROM-based NCDOS - Screen Memory Display]")

def test_screen_memory():
    """Test writing to screen memory and displaying it."""
    print("Testing ROM-based screen memory system...")
    time.sleep(1)
    
    # Create memory manager
    memory = MemoryManager()
    memory.clear_screen()
    
    # Display initial empty screen
    display_screen_memory(memory)
    time.sleep(1)
    
    # Write boot message to screen memory
    messages = [
        "NCDOS 1.0 - NinthCircle DOS",
        "64K RAM System",
        "ROM-based I/O Test",
        "",
        "Testing screen memory at $0400-$07FF",
        ""
    ]
    
    for msg in messages:
        memory.write_to_screen(msg)
        memory.write_to_screen('\n')
        display_screen_memory(memory)
        time.sleep(0.5)
    
    # Test scrolling
    print("\nTesting screen scrolling...")
    time.sleep(1)
    
    for i in range(30):
        memory.write_to_screen(f"Line {i+1}: Testing scroll function\n")
        display_screen_memory(memory)
        time.sleep(0.2)
    
    print("\nScreen memory test complete!")
    print("All output went through memory at $0400-$07FF")
    print("ROM service would monitor this memory and update display")

def test_disk_operations():
    """Test multiple disk drive operations."""
    print("\n" + "="*50)
    print("Testing multiple disk drives...")
    
    # Create two disk drives
    drive_a = NCDOSDisk("test_drive_a.dsk")
    drive_b = NCDOSDisk("test_drive_b.dsk")
    
    # Format both drives
    drive_a.format_disk("DISK_A")
    drive_b.format_disk("DISK_B")
    
    # Save file to drive A
    test_data = b"This is a test file on drive A"
    drive_a.save_file("TEST.TXT", test_data)
    
    # List files on both drives
    print("\nDrive A:")
    for filename, size in drive_a.list_files():
        print(f"  {filename}: {size} bytes")
    
    print("\nDrive B:")
    files_b = drive_b.list_files()
    if not files_b:
        print("  (empty)")
    
    # Copy file from A to B
    data = drive_a.load_file("TEST.TXT")
    if data:
        drive_b.save_file("COPY.TXT", data)
        print("\nCopied TEST.TXT from A: to B:COPY.TXT")
    
    # List drive B again
    print("\nDrive B after copy:")
    for filename, size in drive_b.list_files():
        print(f"  {filename}: {size} bytes")
    
    # Clean up test disk files
    os.remove("test_drive_a.dsk")
    os.remove("test_drive_b.dsk")
    
    print("\nDisk operations test complete!")

if __name__ == "__main__":
    print("ROM-BASED NCDOS SIMULATION TEST")
    print("================================\n")
    
    # Test screen memory system
    test_screen_memory()
    
    # Test disk operations
    test_disk_operations()
    
    print("\n" + "="*50)
    print("All tests complete!")
    print("\nThe full ROM version (dos_rom.py) implements:")
    print("- Background thread monitoring screen memory")
    print("- Character-by-character keyboard input")
    print("- Multiple disk drives with full operations")
    print("- All I/O through BIOS/ROM vectors")
    print("\nThis is exactly how real 8-bit computers worked!")
