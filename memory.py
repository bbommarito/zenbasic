"""
Memory management for ZenBasic - authentic 64K address space
"""
from typing import Tuple, Optional
import struct

# Memory map constants
ZERO_PAGE_START = 0x0000
ZERO_PAGE_END = 0x00FF
STACK_START = 0x0100
STACK_END = 0x01FF
SYSTEM_START = 0x0200
SYSTEM_END = 0x03FF
SCREEN_START = 0x0400
SCREEN_END = 0x07FF
VARS_START = 0x0800
VARS_END = 0x0FFF
PROGRAM_START = 0x1000
PROGRAM_END = 0xEFFF
HARDWARE_START = 0xF000
HARDWARE_END = 0xFFFF

# Symbol table starts at beginning of system area
SYMBOL_TABLE_START = SYSTEM_START
SYMBOL_TABLE_END = SYSTEM_END

# Memory header structure at 0x0200
HEADER_VAR_COUNT = 0x0200      # 16-bit: Number of variables
HEADER_NEXT_SYMBOL = 0x0202    # 16-bit: Offset to next free symbol slot
HEADER_NEXT_VAR = 0x0204       # 16-bit: Next free variable address
HEADER_PAGE = 0x0206           # 16-bit: Start of BASIC program (PAGE)
SYMBOL_DATA_START = 0x0208     # Actual symbol entries start here

# Program storage
DEFAULT_PAGE = PROGRAM_START   # Default PAGE value (0x1000)

class MemoryManager:
    """Manages the 64K memory space for ZenBasic"""
    
    def __init__(self, size: int = 65536):
        self.memory = bytearray(size)
        self.size = size
        
        # Initialize header
        self.store_int16(HEADER_VAR_COUNT, 0)
        self.store_int16(HEADER_NEXT_SYMBOL, SYMBOL_DATA_START)
        self.store_int16(HEADER_NEXT_VAR, VARS_START)
        self.store_int16(HEADER_PAGE, DEFAULT_PAGE)  # Start of BASIC program
        
        # Initialize program storage
        self.program_top = DEFAULT_PAGE  # Current end of program
    
    def store_int16(self, address: int, value: int) -> None:
        """Store 16-bit integer at address, little endian"""
        if address < 0 or address + 1 >= self.size:
            raise ValueError(f"Address {address:04X} out of range")
        
        value = int(value) & 0xFFFF  # Clamp to 16-bit
        self.memory[address] = value & 0xFF        # Low byte first
        self.memory[address + 1] = (value >> 8) & 0xFF  # High byte second
    
    def read_int16(self, address: int) -> int:
        """Read 16-bit integer from address, little endian"""
        if address < 0 or address + 1 >= self.size:
            raise ValueError(f"Address {address:04X} out of range")
        
        low_byte = self.memory[address]
        high_byte = self.memory[address + 1]
        return low_byte | (high_byte << 8)
    
    def store_float32(self, address: int, value: float) -> None:
        """Store 32-bit float at address, little endian"""
        if address < 0 or address + 3 >= self.size:
            raise ValueError(f"Address {address:04X} out of range")
        
        # Convert Python float to 32-bit IEEE 754 bytes
        bytes_data = struct.pack('<f', value)  # '<' for little endian, 'f' for float32
        
        # Store the 4 bytes
        for i, byte in enumerate(bytes_data):
            self.memory[address + i] = byte
    
    def read_float32(self, address: int) -> float:
        """Read 32-bit float from address, little endian"""
        if address < 0 or address + 3 >= self.size:
            raise ValueError(f"Address {address:04X} out of range")
        
        # Read 4 bytes
        bytes_data = bytes(self.memory[address:address + 4])
        
        # Convert from IEEE 754 bytes back to Python float
        return struct.unpack('<f', bytes_data)[0]
    
    def allocate_variable(self, name: str, size: int) -> int:
        """Allocate space for a variable, return its address"""
        # First check the symbol table in memory
        symbol_info = self.find_symbol(name)
        if symbol_info:
            # Variable already exists in symbol table
            return symbol_info[0]
        
        # Get current next variable address from header
        next_var_address = self.read_int16(HEADER_NEXT_VAR)
        
        # Check if we have enough space
        if next_var_address + size > VARS_END:
            raise MemoryError(f"Variable storage full! Cannot allocate {size} bytes for {name}")
        
        # Allocate the space
        address = next_var_address
        
        # Update next variable address in header
        self.store_int16(HEADER_NEXT_VAR, next_var_address + size)
        
        # Write to symbol table
        symbol_addr = self.write_symbol_entry(name, address, size)
        if symbol_addr is None:
            raise MemoryError(f"Symbol table full! Cannot store entry for {name}")
        
        # Increment variable count in header
        var_count = self.read_int16(HEADER_VAR_COUNT)
        self.store_int16(HEADER_VAR_COUNT, var_count + 1)
        
        return address
    
    def dump(self, start_addr: int, length: int = 64) -> None:
        """Dump memory contents in hex format"""
        print(f"Memory dump starting at ${start_addr:04X}:")
        
        for i in range(0, length, 16):
            addr = start_addr + i
            if addr >= self.size:
                break
            
            # Address
            line = f"${addr:04X}: "
            
            # Hex bytes
            for j in range(16):
                if addr + j < self.size:
                    line += f"{self.memory[addr + j]:02X} "
                else:
                    line += "   "
            
            print(line)
    
    def clear_variables(self) -> None:
        """Clear variable allocation table (but not the memory itself)"""
        # Reset header values
        self.store_int16(HEADER_VAR_COUNT, 0)
        self.store_int16(HEADER_NEXT_SYMBOL, SYMBOL_DATA_START)
        self.store_int16(HEADER_NEXT_VAR, VARS_START)
    
    def write_symbol_entry(self, name: str, address: int, size: int) -> Optional[int]:
        """Write a symbol table entry to memory. Returns address of entry or None if no space."""
        name_bytes = name.encode('ascii')
        entry_size = 1 + len(name_bytes) + 2 + 1  # length + name + address + size
        
        # Get next symbol address from header
        next_symbol_address = self.read_int16(HEADER_NEXT_SYMBOL)
        
        # Check if we have room
        if next_symbol_address + entry_size > SYMBOL_TABLE_END:
            return None
            
        entry_addr = next_symbol_address
        
        # Write the entry
        ptr = entry_addr
        self.memory[ptr] = len(name_bytes)  # Name length
        ptr += 1
        
        for byte in name_bytes:  # Name characters
            self.memory[ptr] = byte
            ptr += 1
            
        self.memory[ptr] = address & 0xFF  # Address low byte
        ptr += 1
        self.memory[ptr] = (address >> 8) & 0xFF  # Address high byte
        ptr += 1
        
        self.memory[ptr] = size  # Variable size
        ptr += 1
        
        # Update next symbol address in header
        self.store_int16(HEADER_NEXT_SYMBOL, ptr)
        return entry_addr
    
    def find_symbol(self, name: str) -> Optional[Tuple[int, int]]:
        """Find a symbol in the symbol table. Returns (address, size) or None."""
        name_bytes = name.encode('ascii')
        ptr = SYMBOL_DATA_START
        next_symbol_address = self.read_int16(HEADER_NEXT_SYMBOL)
        
        while ptr < next_symbol_address:
            name_len = self.memory[ptr]
            if name_len == 0:  # End of table marker
                break
                
            # Check if name matches
            matches = True
            if name_len == len(name_bytes):
                for i in range(name_len):
                    if self.memory[ptr + 1 + i] != name_bytes[i]:
                        matches = False
                        break
            else:
                matches = False
                
            if matches:
                # Read address and size
                addr_ptr = ptr + 1 + name_len
                address = self.memory[addr_ptr] | (self.memory[addr_ptr + 1] << 8)
                size = self.memory[addr_ptr + 2]
                return (address, size)
                
            # Move to next entry
            ptr = ptr + 1 + name_len + 2 + 1
            
        return None
    
    def get_all_symbols(self) -> list[tuple[str, int, int]]:
        """Get all symbols from the symbol table. Returns list of (name, address, size)."""
        symbols = []
        ptr = SYMBOL_DATA_START
        next_symbol_address = self.read_int16(HEADER_NEXT_SYMBOL)
        
        while ptr < next_symbol_address:
            name_len = self.memory[ptr]
            if name_len == 0:
                break
                
            # Read name
            name = ''.join(chr(self.memory[ptr + 1 + i]) for i in range(name_len))
            
            # Read address and size
            addr_ptr = ptr + 1 + name_len
            address = self.memory[addr_ptr] | (self.memory[addr_ptr + 1] << 8)
            size = self.memory[addr_ptr + 2]
            
            symbols.append((name, address, size))
            
            # Move to next entry
            ptr = ptr + 1 + name_len + 2 + 1
            
        return symbols
    
    def dump_symbol_table(self) -> None:
        """Dump the symbol table for debugging."""
        var_count = self.read_int16(HEADER_VAR_COUNT)
        next_symbol_address = self.read_int16(HEADER_NEXT_SYMBOL)
        
        print(f"Symbol table header:")
        print(f"  Variable count: {var_count}")
        print(f"  Next symbol offset: ${next_symbol_address:04X}")
        print(f"  Next variable address: ${self.read_int16(HEADER_NEXT_VAR):04X}")
        print(f"\nSymbol table entries at ${SYMBOL_DATA_START:04X}:")
        
        ptr = SYMBOL_DATA_START
        
        while ptr < next_symbol_address:
            name_len = self.memory[ptr]
            if name_len == 0:
                break
                
            # Read name
            name = ''.join(chr(self.memory[ptr + 1 + i]) for i in range(name_len))
            
            # Read address and size
            addr_ptr = ptr + 1 + name_len
            address = self.memory[addr_ptr] | (self.memory[addr_ptr + 1] << 8)
            size = self.memory[addr_ptr + 2]
            
            print(f"  ${ptr:04X}: {name} -> ${address:04X} ({size} bytes)")
            
            # Move to next entry
            ptr = ptr + 1 + name_len + 2 + 1
            
        print(f"\nSymbol table uses {next_symbol_address - SYMBOL_DATA_START} bytes")
    
    def store_program_line(self, line_num: int, tokens: bytes) -> bool:
        """
        Store a tokenized program line in memory.
        Format: [next_ptr:2][line_num:2][tokens...][0x0D]
        Returns True if successful, False if out of memory.
        """
        # Calculate space needed: 2 (next) + 2 (line#) + len(tokens) + 1 (EOL)
        line_size = 4 + len(tokens) + 1
        
        # Check if we have space
        if self.program_top + line_size > PROGRAM_END:
            return False
        
        # Get PAGE pointer
        page = self.read_int16(HEADER_PAGE)
        
        # Find where to insert this line (sorted by line number)
        prev_ptr = 0
        curr_ptr = page
        
        while curr_ptr < self.program_top:
            # Read line number at current position
            curr_line_num = self.read_int16(curr_ptr + 2)
            
            if curr_line_num == line_num:
                # Replace existing line - TODO: implement line replacement
                # For now, we'll delete and re-add
                self.delete_program_line(line_num)
                return self.store_program_line(line_num, tokens)
            elif curr_line_num > line_num:
                # Insert before this line
                break
            
            # Move to next line
            prev_ptr = curr_ptr
            next_ptr = self.read_int16(curr_ptr)
            if next_ptr == 0:
                # End of program
                break
            curr_ptr = next_ptr
        
        # Insert the new line at program_top
        new_line_ptr = self.program_top
        
        # Write the line structure
        self.store_int16(new_line_ptr, 0)  # Will update next pointer later
        self.store_int16(new_line_ptr + 2, line_num)
        
        # Write tokens
        for i, byte in enumerate(tokens):
            self.memory[new_line_ptr + 4 + i] = byte
        
        # Write end-of-line marker
        self.memory[new_line_ptr + 4 + len(tokens)] = 0x0D
        
        # Update pointers
        if prev_ptr == 0:
            # This is the first line or insert at beginning
            if curr_ptr == page and self.program_top == page:
                # Very first line
                self.store_int16(new_line_ptr, 0)  # No next line
            else:
                # Insert at beginning
                self.store_int16(new_line_ptr, curr_ptr)  # Point to old first
                self.store_int16(HEADER_PAGE, new_line_ptr)  # Update PAGE
        else:
            # Insert in middle or at end
            next_of_prev = self.read_int16(prev_ptr)
            self.store_int16(prev_ptr, new_line_ptr)  # Previous points to new
            self.store_int16(new_line_ptr, next_of_prev)  # New points to next
        
        # Update program_top
        self.program_top = new_line_ptr + line_size
        
        return True
    
    def delete_program_line(self, line_num: int) -> bool:
        """
        Delete a program line from memory.
        Returns True if line was found and deleted.
        """
        page = self.read_int16(HEADER_PAGE)
        prev_ptr = 0
        curr_ptr = page
        
        while curr_ptr < self.program_top:
            curr_line_num = self.read_int16(curr_ptr + 2)
            
            if curr_line_num == line_num:
                # Found the line to delete
                next_ptr = self.read_int16(curr_ptr)
                
                if prev_ptr == 0:
                    # Deleting first line
                    self.store_int16(HEADER_PAGE, next_ptr if next_ptr else page)
                else:
                    # Update previous line's next pointer
                    self.store_int16(prev_ptr, next_ptr)
                
                # Note: We don't actually reclaim memory here (like real BASIC)
                # Could implement compaction later
                return True
            
            prev_ptr = curr_ptr
            next_ptr = self.read_int16(curr_ptr)
            if next_ptr == 0:
                break
            curr_ptr = next_ptr
        
        return False
    
    def get_program_lines(self) -> list[tuple[int, bytes]]:
        """
        Get all program lines from memory.
        Returns list of (line_number, tokenized_bytes) tuples.
        """
        lines = []
        page = self.read_int16(HEADER_PAGE)
        curr_ptr = page
        
        while curr_ptr < self.program_top:
            # Read line number
            line_num = self.read_int16(curr_ptr + 2)
            
            # Read tokens until EOL
            tokens = []
            i = curr_ptr + 4
            while i < self.program_top and self.memory[i] != 0x0D:
                tokens.append(self.memory[i])
                i += 1
            
            lines.append((line_num, bytes(tokens)))
            
            # Move to next line
            next_ptr = self.read_int16(curr_ptr)
            if next_ptr == 0:
                break
            curr_ptr = next_ptr
        
        return lines
    
    def clear_program(self) -> None:
        """Clear the stored BASIC program."""
        page = self.read_int16(HEADER_PAGE)
        self.program_top = page
        # Clear first word to indicate empty program
        self.store_int16(page, 0)
    
    def get_memory_map_info(self) -> str:
        """Return human-readable memory map information"""
        # Read values from header
        var_count = self.read_int16(HEADER_VAR_COUNT)
        next_symbol = self.read_int16(HEADER_NEXT_SYMBOL)
        next_var_addr = self.read_int16(HEADER_NEXT_VAR)
        
        symbols_used = next_symbol - SYMBOL_DATA_START
        vars_used = next_var_addr - VARS_START
        
        return f"""Memory Map:
$0000-$00FF  Zero Page ({ZERO_PAGE_END - ZERO_PAGE_START + 1} bytes)
$0100-$01FF  Stack ({STACK_END - STACK_START + 1} bytes)
$0200-$03FF  System Area ({SYSTEM_END - SYSTEM_START + 1} bytes)
             Header: 8 bytes, Symbols: {symbols_used} bytes used
$0400-$07FF  Screen Memory ({SCREEN_END - SCREEN_START + 1} bytes)
$0800-$0FFF  Variable Storage ({VARS_END - VARS_START + 1} bytes)
$1000-$EFFF  Program Memory ({PROGRAM_END - PROGRAM_START + 1} bytes)
$F000-$FFFF  Hardware Registers ({HARDWARE_END - HARDWARE_START + 1} bytes)

Statistics:
  Variables defined: {var_count}
  Variable memory: ${next_var_addr:04X} ({vars_used} bytes used, {VARS_END - next_var_addr + 1} bytes free)
  Symbol table: {symbols_used} bytes used"""
