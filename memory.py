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

class MemoryManager:
    """Manages the 64K memory space for ZenBasic"""
    
    def __init__(self, size: int = 65536):
        self.memory = bytearray(size)
        self.size = size
        self.next_var_address = VARS_START
        self.var_table: dict[str, Tuple[int, int]] = {}  # name -> (address, size)
        self.next_symbol_address = SYMBOL_TABLE_START  # Where to write next symbol
    
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
        
        # Check if we have enough space
        if self.next_var_address + size > VARS_END:
            raise MemoryError(f"Variable storage full! Cannot allocate {size} bytes for {name}")
        
        # Allocate the space
        address = self.next_var_address
        self.next_var_address += size
        
        # Write to symbol table
        symbol_addr = self.write_symbol_entry(name, address, size)
        if symbol_addr is None:
            raise MemoryError(f"Symbol table full! Cannot store entry for {name}")
            
        # Keep Python dict for backward compatibility (for now)
        self.var_table[name] = (address, size)
        
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
        self.var_table.clear()
        self.next_var_address = VARS_START
        self.next_symbol_address = SYMBOL_TABLE_START
    
    def write_symbol_entry(self, name: str, address: int, size: int) -> Optional[int]:
        """Write a symbol table entry to memory. Returns address of entry or None if no space."""
        name_bytes = name.encode('ascii')
        entry_size = 1 + len(name_bytes) + 2 + 1  # length + name + address + size
        
        # Check if we have room
        if self.next_symbol_address + entry_size > SYMBOL_TABLE_END:
            return None
            
        entry_addr = self.next_symbol_address
        
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
        
        self.next_symbol_address = ptr
        return entry_addr
    
    def find_symbol(self, name: str) -> Optional[Tuple[int, int]]:
        """Find a symbol in the symbol table. Returns (address, size) or None."""
        name_bytes = name.encode('ascii')
        ptr = SYMBOL_TABLE_START
        
        while ptr < self.next_symbol_address:
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
    
    def dump_symbol_table(self) -> None:
        """Dump the symbol table for debugging."""
        print(f"Symbol table at ${SYMBOL_TABLE_START:04X}:")
        ptr = SYMBOL_TABLE_START
        
        while ptr < self.next_symbol_address:
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
            
        print(f"Symbol table uses {self.next_symbol_address - SYMBOL_TABLE_START} bytes")
    
    def get_memory_map_info(self) -> str:
        """Return human-readable memory map information"""
        symbols_used = self.next_symbol_address - SYMBOL_TABLE_START
        return f"""Memory Map:
$0000-$00FF  Zero Page ({ZERO_PAGE_END - ZERO_PAGE_START + 1} bytes)
$0100-$01FF  Stack ({STACK_END - STACK_START + 1} bytes)
$0200-$03FF  System Area ({SYSTEM_END - SYSTEM_START + 1} bytes) - Symbols: {symbols_used} bytes used
$0400-$07FF  Screen Memory ({SCREEN_END - SCREEN_START + 1} bytes)
$0800-$0FFF  Variable Storage ({VARS_END - VARS_START + 1} bytes)
$1000-$EFFF  Program Memory ({PROGRAM_END - PROGRAM_START + 1} bytes)
$F000-$FFFF  Hardware Registers ({HARDWARE_END - HARDWARE_START + 1} bytes)

Variable allocation: ${self.next_var_address:04X} (${self.next_var_address - VARS_START} bytes used)"""
