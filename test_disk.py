#!/usr/bin/env python3
"""
Test the NCDOS disk SAVE/LOAD functionality
"""

import os
import sys
from repl import ZenBasicRepl

def test_save_load():
    """Test saving and loading BASIC programs to NCDOS disk"""
    print("Testing NCDOS disk operations...")
    print("-" * 40)
    
    # Create a REPL instance
    repl = ZenBasicRepl()
    
    # Create a simple program
    print("Creating test program...")
    repl.process_line("10 A = 5")
    repl.process_line("20 B = 10")
    repl.process_line("30 C = A + B")
    
    # List the program
    print("\nOriginal program:")
    repl.program_store.list_program()
    
    # Save to disk
    print("\nSaving to disk as TEST.BAS...")
    repl.command_registry.execute("SAVE TEST", repl)
    
    # List files on disk
    print("\nDisk catalog:")
    repl.command_registry.execute("CATALOG", repl)
    
    # Clear program
    print("\nClearing program...")
    repl.new_program()
    repl.program_store.list_program()
    
    # Load from disk
    print("\nLoading TEST.BAS from disk...")
    repl.command_registry.execute("LOAD TEST", repl)
    
    # List loaded program
    print("\nLoaded program:")
    repl.program_store.list_program()
    
    # Save another program
    print("\nCreating another program...")
    repl.new_program()
    repl.process_line("10 PRINT \"HELLO WORLD\"")
    repl.process_line("20 PRINT \"FROM NCDOS\"")
    
    print("\nSaving as HELLO.BAS...")
    repl.command_registry.execute("SAVE HELLO", repl)
    
    # List all files
    print("\nFinal disk catalog:")
    repl.command_registry.execute("CAT", repl)
    
    # Test delete
    print("\nDeleting TEST.BAS...")
    repl.command_registry.execute("DELETE TEST", repl)
    
    print("\nDisk catalog after delete:")
    repl.command_registry.execute("CAT", repl)
    
    print("\n" + "=" * 40)
    print("NCDOS disk test complete!")

if __name__ == "__main__":
    # Remove old disk file if it exists
    if os.path.exists("ncdos.dsk"):
        print("Removing old disk file...")
        os.remove("ncdos.dsk")
    
    test_save_load()
