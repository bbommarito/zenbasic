"""
Memory management for ZenBasic - authentic 64K address space
"""
from typing import Tuple, Optional

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

class MemoryManager:
    """Manages the 64K memory space for ZenBasic"""
    
    def __init__(self, size: int = 65536):
        self.memory = bytearray(size)
        self.size = size
        self.next_var_address = VARS_START
        self.var_table: dict[str, Tuple[int, int]] = {}  # name -> (address, size)
    
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
    
    def allocate_variable(self, name: str, size: int) -> int:
        """Allocate space for a variable, return its address"""
        if name in self.var_table:
            # Variable already exists, return existing address
            return self.var_table[name][0]
        
        # Check if we have enough space
        if self.next_var_address + size > VARS_END:
            raise MemoryError(f"Variable storage full! Cannot allocate {size} bytes for {name}")
        
        # Allocate the space
        address = self.next_var_address
        self.var_table[name] = (address, size)
        self.next_var_address += size
        
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
    
    def get_memory_map_info(self) -> str:
        """Return human-readable memory map information"""
        return f"""Memory Map:
$0000-$00FF  Zero Page ({ZERO_PAGE_END - ZERO_PAGE_START + 1} bytes)
$0100-$01FF  Stack ({STACK_END - STACK_START + 1} bytes)
$0200-$03FF  System Area ({SYSTEM_END - SYSTEM_START + 1} bytes)
$0400-$07FF  Screen Memory ({SCREEN_END - SCREEN_START + 1} bytes)
$0800-$0FFF  Variable Storage ({VARS_END - VARS_START + 1} bytes)
$1000-$EFFF  Program Memory ({PROGRAM_END - PROGRAM_START + 1} bytes)
$F000-$FFFF  Hardware Registers ({HARDWARE_END - HARDWARE_START + 1} bytes)

Variable allocation: ${self.next_var_address:04X} (${self.next_var_address - VARS_START} bytes used)"""
