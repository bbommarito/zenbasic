# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

NCDOS/ZenBasic is a complete DOS-based 8-bit computer system implemented in Python:
- **NCDOS (NinthCircle DOS)**: Primary interface - boots to A> prompt like MS-DOS/CP/M
- **ZenBasic**: BBC BASIC interpreter launched by typing `BASIC` at DOS prompt
- **Authentic Architecture**: Proper DOS/program separation, ROM banking, FAT filesystem
- **Historical Accuracy**: Boots to command line, launches programs, returns to DOS - exactly like 1983

## Key Architecture

The project uses a dual-path execution model with integrated disk system:

### Core Components

1. **main.py** - Entry point
2. **repl.py** - Main REPL with disk integration:
   - Line number parsing and tokenized storage
   - Command execution (LIST, RUN, NEW, SAVE, LOAD, etc.)
   - Disk system integration
   - Memory-mapped variable storage

### Memory System
- **memory.py** - 64K address space management
- **tokenized_program.py** - Programs stored as tokens in memory
- **token_executor.py** - Direct token execution (fast path)
- **tokens.py** - BBC BASIC token table and tokenization

### Parser/Transformer (Fallback Path)
- **parser.py** - Lark grammar definition
- **transformer.py** - AST transformation with loop arithmetic
- **arithmetic.py** - Authentic loop-based operations

### NCDOS Components
- **dos_simple.py** - Main DOS command prompt (current implementation)
- **dos.py** - Full ROM vector version (future)
- **disk.py** - Virtual 160KB floppy with FAT filesystem
- **rom.py** - ROM banking and I/O vectors
- **ncdos.dsk** - Persistent disk image file

## Development Commands

### Running the System
```bash
python main.py
# Boots directly to NCDOS A> prompt
# Type 'HELP' for commands
# Type 'BASIC' to enter ZenBasic
```

### Testing Disk Operations
```bash
python test_disk.py
# Tests SAVE, LOAD, CATALOG, DELETE
```

### Installing Dependencies
```bash
pip install lark
```

## Development Guidelines

### Adding New Commands

#### Immediate Commands
1. Add handler function to `commands.py`
2. Register in `CommandRegistry.register_built_in_commands()`
3. For disk operations, use `repl.disk` object

#### Program Statements (e.g., PRINT, IF)
1. Add token definition to `tokens.py`
2. Implement in `token_executor.py` for direct execution
3. Add grammar rule in `parser.py` as fallback
4. Update transformer if needed

### Memory Layout
- Programs stored as tokenized bytes at $1000-$EFFF
- Variables allocated at $0800-$0FFF
- Symbol table at $0208-$03FF with O(1) header at $0200
- Screen memory at $0400-$07FF (future use)

### Disk System
- 40 tracks × 16 sectors × 256 bytes = 160KB
- Track 0: Boot sector, directory (64 entries), FAT
- Tracks 1-39: User data
- Files stored as sector chains
- 8.3 filename format (FILENAME.EXT)

## Architecture Notes

### Execution Flow
1. **Tokenization**: Text → Token bytes via `tokenize_line()`
2. **Storage**: Tokens stored in memory as linked list
3. **Execution**: Token executor reads bytes directly
4. **Fallback**: Complex statements fall back to parser

### REPL Flow
1. User input → Parse for line number
2. If line number: Tokenize and store in memory
3. If immediate: Check command registry → Execute
4. RUN command: Try token executor → Fall back to parser

### State Management
- **Memory**: 64K bytearray simulating complete address space
- **Programs**: Stored as tokenized bytes in memory ($1000+)
- **Variables**: Allocated in memory with symbol table
- **Disk**: Virtual floppy disk with FAT filesystem
- **No dictionaries**: Everything lives in the 64K memory!

### Error Handling
- Parser errors are caught and displayed
- Runtime errors stop program execution
- Division by zero is explicitly handled
- Disk errors reported (disk full, file not found, etc.)

## Common Tasks

### Adding Disk Support to New Features
1. Check for `repl.disk` availability
2. Use disk methods: `save_file()`, `load_file()`, `list_files()`, `delete_file()`
3. Handle disk errors gracefully
4. Files automatically get .BAS extension if not specified

### Testing Disk Operations
```python
from disk import NCDOSDisk
disk = NCDOSDisk("test.dsk")
disk.save_file("TEST.BAS", b"10 PRINT HELLO")
data = disk.load_file("TEST.BAS")
files = disk.list_files()
```

### Debugging
- Use `DUMP` command to inspect memory
- Use `SYMBOLS` to see variable allocation
- Use `CATALOG` to see disk contents
- Check `ncdos.dsk` with hex editor to see raw disk structure

## Design Philosophy

This project embraces authentic limitations:
- Real 64K memory constraint
- Tokenized program storage
- Sector-based disk access
- Loop-based arithmetic (in non-turbo mode)
- Everything that was hard in 1983 is hard now

"It's not a bug, it's historically accurate!"
