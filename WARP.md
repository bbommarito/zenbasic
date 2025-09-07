# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ZenBasic/NCDOS is a complete 8-bit computer system implemented in Python:
- **ZenBasic**: BBC BASIC interpreter with tokenized programs and memory-mapped variables
- **NCDOS (NinthCircle DOS)**: Disk operating system with FAT filesystem and virtual floppy disks
- **Authentic Implementation**: Arithmetic through loops, 64K memory space, disk sectors - all historically accurate

## Key Architecture

The project implements a complete 8-bit computer system:

### Core Interpreter
1. **main.py** - Entry point
2. **repl.py** - REPL with disk integration:
   - Line number parsing and tokenized storage
   - Command execution (LIST, RUN, NEW, SAVE, LOAD, etc.)
   - Disk system integration
   - Memory-mapped variable storage

3. **Memory System**:
   - **memory.py** - 64K address space management
   - **tokenized_program.py** - Programs stored as tokens in memory
   - **token_executor.py** - Direct token execution (bypasses parsing)

4. **Parser/Transformer**:
   - **transformer.py** - Lark-based parser with loop arithmetic
   - **parser.py** - BASIC grammar definition
   - **arithmetic.py** - Authentic loop-based operations

5. **NCDOS Components**:
   - **disk.py** - Virtual 160KB floppy with FAT filesystem
   - **rom.py** - ROM banking and I/O vectors
   - **ncdos.dsk** - Persistent disk image file

## Development Commands

### Running the System
```bash
python main.py
# This will create/load ncdos.dsk automatically
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

### Running Tests
*Note: No test suite currently exists. When implementing tests, create test files for each module.*

## Development Guidelines

### Parser Modifications
- Grammar is defined in `BASIC_GRAMMAR` string in transformer.py
- Use Lark parser syntax for new statements
- Follow the existing pattern: create grammar rule → implement transformer method

### Adding New Commands
1. Register in `commands.py` CommandRegistry
2. Implement handler function
3. For disk operations, use `repl.disk` object
4. For program statements:
   - Add token in `tokens.py`
   - Implement in `token_executor.py` for fast path
   - Add grammar rule in `parser.py` as fallback

### Arithmetic Implementation
The project intentionally implements arithmetic through loops for authenticity:
- Addition: Incrementing one-by-one
- Subtraction: Adding negative numbers
- Multiplication: Repeated addition
- Division: Repeated subtraction

When in turbo mode, operations use native Python operators for speed.

### Variable Handling
- Variables must be uppercase (enforced by grammar: `/[A-Z][A-Z0-9_]*/`)
- Stored in `self.variables` dictionary
- Currently only supports integers

## Common Tasks

### Adding a New Statement Type
Example for adding PRINT statement:
1. Update BASIC_GRAMMAR to include print rule
2. Add transformer method in BasicTransformer class
3. Handle both immediate and program execution modes

### Debugging Parser Issues
- Lark exceptions are caught and displayed to user
- Use `tree = self.parser.parse(command)` to debug grammar
- Parser errors show as "Syntax error: [details]"

### Extending Variable Support
Currently only integers are supported. To add strings:
1. Modify grammar to recognize string literals
2. Update transformer to handle string types
3. Consider separate storage for string variables (like BASIC's A$ notation)

## Architecture Notes

### REPL Flow
1. User input → Parse for line number
2. If line number: Tokenize and store in memory
3. If immediate: Check command registry → Execute
4. RUN command: Try token executor → Fall back to parser

### Disk System
- 40 tracks × 16 sectors × 256 bytes = 160KB
- Track 0: Boot sector, directory, FAT
- Tracks 1-39: User data
- Files stored as sector chains
- 8.3 filename format (FILENAME.EXT)

### State Management
- `self.program_lines`: Dict[int, str] - Stores numbered program lines
- `self.variables`: Dict[str, Any] - Stores variable values
- `self.turbo`: bool - Performance mode flag

### Error Handling
- Parser errors are caught and displayed
- Runtime errors stop program execution
- Division by zero is explicitly handled
