"""
NCDOS Virtual Disk System
Because even in Hell, we need persistent storage

Simulates a 160KB floppy disk:
- 40 tracks
- 16 sectors per track  
- 256 bytes per sector
- Total: 163,840 bytes

Track 0: Directory and FAT
Track 1-39: Data
"""
import os
import struct
from typing import Optional, List, Tuple


# Disk geometry (5.25" floppy style)
TRACKS = 40
SECTORS_PER_TRACK = 16
BYTES_PER_SECTOR = 256
DISK_SIZE = TRACKS * SECTORS_PER_TRACK * BYTES_PER_SECTOR  # 163,840 bytes

# Directory structure
DIR_TRACK = 0
DIR_SECTOR = 0
DIR_ENTRIES = 64  # Max files
DIR_ENTRY_SIZE = 32  # Bytes per directory entry

# FAT (File Allocation Table)
FAT_TRACK = 0
FAT_SECTOR = 8  # Second half of track 0
FAT_SIZE = 8 * BYTES_PER_SECTOR  # 8 sectors for FAT

# Directory entry format (32 bytes):
# 0-7:   Filename (8 chars, space padded)
# 8-10:  Extension (3 chars, space padded)  
# 11:    Attributes (bit 7=deleted)
# 12-13: First track/sector
# 14-15: File size in bytes
# 16-31: Reserved


class NCDOSDisk:
    """
    Virtual disk for NCDOS.
    Provides a simple filesystem on our virtual floppy.
    """
    
    def __init__(self, filename: str = "ncdos.dsk"):
        """
        Initialize or load a virtual disk.
        
        Args:
            filename: Disk image filename
        """
        self.filename = filename
        self.disk = bytearray(DISK_SIZE)
        self.mounted = False
        
        # Try to load existing disk
        if os.path.exists(filename):
            self.load_disk()
        else:
            self.format_disk()
            
    def format_disk(self, label: str = "NCDOS"):
        """
        Format the disk with empty filesystem.
        Welcome to a fresh Hell.
        
        Args:
            label: Volume label (max 8 chars)
        """
        # Clear entire disk
        self.disk = bytearray(DISK_SIZE)
        
        # Write boot sector signature
        self._write_sector(0, 0, b'NCDOS1.0' + b'\x00' * 248)
        
        # Initialize FAT (all sectors free)
        # FAT entry: 0xFF = free, 0x00-0xFE = next sector in chain, 0xFE = end of file
        fat = bytearray(FAT_SIZE)
        for i in range(FAT_SIZE):
            fat[i] = 0xFF  # All free
            
        # Mark system tracks as used
        fat[0] = 0x00  # Boot sector used
        for i in range(1, 16):  # Rest of track 0 used for directory/FAT
            fat[i] = 0x00
            
        # Write FAT
        for i in range(8):
            self._write_sector(0, FAT_SECTOR + i, fat[i * BYTES_PER_SECTOR:(i + 1) * BYTES_PER_SECTOR])
            
        # Create volume label in first directory entry
        label_entry = self._create_dir_entry(label[:8], "VOL", 0, 0, 0x08)  # 0x08 = volume label
        self._write_sector(0, 1, label_entry + b'\xFF' * (BYTES_PER_SECTOR - 32))
        
        self.mounted = True
        self.save_disk()
        
    def _create_dir_entry(self, name: str, ext: str, track: int, sector: int, 
                         attributes: int = 0, size: int = 0) -> bytes:
        """
        Create a directory entry.
        
        Args:
            name: Filename (max 8 chars)
            ext: Extension (max 3 chars)
            track: Starting track
            sector: Starting sector
            attributes: File attributes
            size: File size in bytes
            
        Returns:
            32-byte directory entry
        """
        entry = bytearray(32)
        
        # Filename (8 bytes, space padded)
        name_bytes = name.upper().ljust(8)[:8].encode('ascii')
        entry[0:8] = name_bytes
        
        # Extension (3 bytes, space padded)
        ext_bytes = ext.upper().ljust(3)[:3].encode('ascii')
        entry[8:11] = ext_bytes
        
        # Attributes
        entry[11] = attributes
        
        # First track/sector
        entry[12] = track
        entry[13] = sector
        
        # File size
        entry[14] = size & 0xFF
        entry[15] = (size >> 8) & 0xFF
        
        return bytes(entry)
        
    def save_file(self, filename: str, data: bytes) -> bool:
        """
        Save a file to disk.
        
        Args:
            filename: Filename (8.3 format)
            data: File contents
            
        Returns:
            True if successful
        """
        # Parse filename
        parts = filename.upper().split('.')
        name = parts[0][:8] if parts else filename[:8]
        ext = parts[1][:3] if len(parts) > 1 else "   "
        
        # Check if file exists and delete it
        self.delete_file(filename)
        
        # Find free directory entry
        dir_entry_addr = self._find_free_dir_entry()
        if dir_entry_addr is None:
            return False  # Directory full
            
        # Allocate sectors for file
        sectors_needed = (len(data) + BYTES_PER_SECTOR - 1) // BYTES_PER_SECTOR
        allocated = self._allocate_sectors(sectors_needed)
        if not allocated:
            return False  # Disk full
            
        # Write data to allocated sectors
        for i, (track, sector) in enumerate(allocated):
            start = i * BYTES_PER_SECTOR
            end = min(start + BYTES_PER_SECTOR, len(data))
            sector_data = data[start:end]
            if len(sector_data) < BYTES_PER_SECTOR:
                sector_data += b'\x00' * (BYTES_PER_SECTOR - len(sector_data))
            self._write_sector(track, sector, sector_data)
            
        # Create directory entry
        first_track, first_sector = allocated[0]
        dir_entry = self._create_dir_entry(name, ext, first_track, first_sector, 0, len(data))
        
        # Write directory entry
        track, sector, offset = dir_entry_addr
        sector_data = bytearray(self._read_sector(track, sector))
        sector_data[offset:offset + 32] = dir_entry
        self._write_sector(track, sector, bytes(sector_data))
        
        # Update FAT with file chain
        self._update_fat_chain(allocated)
        
        self.save_disk()
        return True
        
    def load_file(self, filename: str) -> Optional[bytes]:
        """
        Load a file from disk.
        
        Args:
            filename: Filename to load
            
        Returns:
            File contents or None if not found
        """
        # Find directory entry
        entry = self._find_file(filename)
        if not entry:
            return None
            
        # Read file size and starting position
        track = entry[12]
        sector = entry[13]
        size = entry[14] | (entry[15] << 8)
        
        # Follow FAT chain to read file
        data = bytearray()
        while track != 0 or sector != 0:
            sector_data = self._read_sector(track, sector)
            data.extend(sector_data)
            
            # Get next sector from FAT
            fat_entry = self._get_fat_entry(track, sector)
            if fat_entry == 0xFE:  # End of file
                break
            elif fat_entry == 0xFF:  # Error - free sector in chain
                return None
            else:
                # Next sector in chain
                track = fat_entry // SECTORS_PER_TRACK
                sector = fat_entry % SECTORS_PER_TRACK
                
        return bytes(data[:size])
        
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from disk.
        Send it to a deeper circle of Hell.
        
        Args:
            filename: File to delete
            
        Returns:
            True if deleted
        """
        # Find directory entry
        entry_addr = self._find_file_entry(filename)
        if not entry_addr:
            return False
            
        track, sector, offset = entry_addr
        sector_data = bytearray(self._read_sector(track, sector))
        
        # Get file's starting position
        file_track = sector_data[offset + 12]
        file_sector = sector_data[offset + 13]
        
        # Mark directory entry as deleted (set bit 7 of attributes)
        sector_data[offset + 11] |= 0x80
        self._write_sector(track, sector, bytes(sector_data))
        
        # Free sectors in FAT
        self._free_fat_chain(file_track, file_sector)
        
        self.save_disk()
        return True
        
    def list_files(self) -> List[Tuple[str, int]]:
        """
        List all files on disk.
        
        Returns:
            List of (filename, size) tuples
        """
        files = []
        
        # Scan directory
        for i in range(DIR_ENTRIES):
            entry = self._read_dir_entry(i)
            if entry and entry[0] != 0xFF and entry[0] != 0x00:  # Not empty or deleted
                if entry[11] & 0x80 == 0:  # Not deleted
                    name = entry[0:8].decode('ascii').strip()
                    ext = entry[8:11].decode('ascii').strip()
                    if ext:
                        filename = f"{name}.{ext}"
                    else:
                        filename = name
                    size = entry[14] | (entry[15] << 8)
                    
                    if entry[11] & 0x08:  # Volume label
                        continue
                        
                    files.append((filename, size))
                    
        return files
        
    def _write_sector(self, track: int, sector: int, data: bytes):
        """Write data to a sector."""
        offset = (track * SECTORS_PER_TRACK + sector) * BYTES_PER_SECTOR
        self.disk[offset:offset + BYTES_PER_SECTOR] = data[:BYTES_PER_SECTOR]
        
    def _read_sector(self, track: int, sector: int) -> bytes:
        """Read data from a sector."""
        offset = (track * SECTORS_PER_TRACK + sector) * BYTES_PER_SECTOR
        return bytes(self.disk[offset:offset + BYTES_PER_SECTOR])
        
    def _find_free_dir_entry(self) -> Optional[Tuple[int, int, int]]:
        """Find a free directory entry. Returns (track, sector, offset)."""
        for i in range(DIR_ENTRIES):
            entry = self._read_dir_entry(i)
            if entry[0] == 0xFF or entry[0] == 0x00 or entry[11] & 0x80:  # Free or deleted
                # Calculate position
                entry_num = i
                sector_num = 1 + (entry_num * 32) // BYTES_PER_SECTOR
                offset = (entry_num * 32) % BYTES_PER_SECTOR
                return (0, sector_num, offset)
        return None
        
    def _read_dir_entry(self, index: int) -> bytes:
        """Read a directory entry by index."""
        sector_num = 1 + (index * 32) // BYTES_PER_SECTOR
        offset = (index * 32) % BYTES_PER_SECTOR
        sector_data = self._read_sector(0, sector_num)
        return sector_data[offset:offset + 32]
        
    def _find_file(self, filename: str) -> Optional[bytes]:
        """Find a file's directory entry."""
        parts = filename.upper().split('.')
        name = parts[0][:8] if parts else filename[:8]
        ext = parts[1][:3] if len(parts) > 1 else ""
        
        for i in range(DIR_ENTRIES):
            entry = self._read_dir_entry(i)
            if entry[0] != 0xFF and entry[0] != 0x00:
                entry_name = entry[0:8].decode('ascii').strip()
                entry_ext = entry[8:11].decode('ascii').strip()
                if entry_name == name and entry_ext == ext:
                    if entry[11] & 0x80 == 0:  # Not deleted
                        return entry
        return None
        
    def _find_file_entry(self, filename: str) -> Optional[Tuple[int, int, int]]:
        """Find a file's directory entry position."""
        parts = filename.upper().split('.')
        name = parts[0][:8] if parts else filename[:8]
        ext = parts[1][:3] if len(parts) > 1 else ""
        
        for i in range(DIR_ENTRIES):
            entry = self._read_dir_entry(i)
            if entry[0] != 0xFF and entry[0] != 0x00:
                entry_name = entry[0:8].decode('ascii').strip()
                entry_ext = entry[8:11].decode('ascii').strip()
                if entry_name == name and entry_ext == ext:
                    if entry[11] & 0x80 == 0:  # Not deleted
                        sector_num = 1 + (i * 32) // BYTES_PER_SECTOR
                        offset = (i * 32) % BYTES_PER_SECTOR
                        return (0, sector_num, offset)
        return None
        
    def _allocate_sectors(self, count: int) -> List[Tuple[int, int]]:
        """Allocate free sectors. Returns list of (track, sector) tuples."""
        allocated = []
        fat = self._read_fat()
        
        # Start from track 1 (track 0 is system)
        for track in range(1, TRACKS):
            for sector in range(SECTORS_PER_TRACK):
                index = track * SECTORS_PER_TRACK + sector
                if fat[index] == 0xFF:  # Free
                    allocated.append((track, sector))
                    if len(allocated) >= count:
                        return allocated
        return []  # Not enough free space
        
    def _read_fat(self) -> bytearray:
        """Read the entire FAT."""
        fat = bytearray()
        for i in range(8):
            fat.extend(self._read_sector(0, FAT_SECTOR + i))
        return fat
        
    def _write_fat(self, fat: bytes):
        """Write the entire FAT."""
        for i in range(8):
            self._write_sector(0, FAT_SECTOR + i, 
                             fat[i * BYTES_PER_SECTOR:(i + 1) * BYTES_PER_SECTOR])
            
    def _get_fat_entry(self, track: int, sector: int) -> int:
        """Get FAT entry for a sector."""
        fat = self._read_fat()
        index = track * SECTORS_PER_TRACK + sector
        return fat[index]
        
    def _update_fat_chain(self, sectors: List[Tuple[int, int]]):
        """Update FAT with file chain."""
        fat = self._read_fat()
        
        for i, (track, sector) in enumerate(sectors):
            index = track * SECTORS_PER_TRACK + sector
            if i < len(sectors) - 1:
                # Point to next sector
                next_track, next_sector = sectors[i + 1]
                fat[index] = next_track * SECTORS_PER_TRACK + next_sector
            else:
                # End of file
                fat[index] = 0xFE
                
        self._write_fat(fat)
        
    def _free_fat_chain(self, track: int, sector: int):
        """Free a chain of sectors in FAT."""
        fat = self._read_fat()
        
        while track != 0 or sector != 0:
            index = track * SECTORS_PER_TRACK + sector
            next_val = fat[index]
            fat[index] = 0xFF  # Mark as free
            
            if next_val == 0xFE:  # End of chain
                break
            elif next_val == 0xFF:  # Already free (error)
                break
            else:
                # Next in chain
                track = next_val // SECTORS_PER_TRACK
                sector = next_val % SECTORS_PER_TRACK
                
        self._write_fat(fat)
        
    def save_disk(self):
        """Save disk image to file."""
        with open(self.filename, 'wb') as f:
            f.write(self.disk)
            
    def load_disk(self):
        """Load disk image from file."""
        with open(self.filename, 'rb') as f:
            self.disk = bytearray(f.read(DISK_SIZE))
        self.mounted = True
