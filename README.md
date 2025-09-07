# ZenBasic / NCDOS

A complete 8-bit computer system implemented in Python, featuring BBC BASIC and NinthCircle DOS - a working disk operating system with FAT filesystem. Born from nostalgia and the beautiful madness of recreating history.

## About

ZenBasic started as a learning project to recreate BASIC programming on early home computers. It has evolved into something beautifully absurd: a complete 8-bit computer system trapped in Python, featuring:

- **ZenBasic**: An authentic BBC BASIC interpreter with tokenized programs and memory-mapped variables
- **NCDOS (NinthCircle DOS)**: A working disk operating system with virtual floppy disks and FAT filesystem
- **Authentic Hardware Emulation**: 64K memory space, ROM banking, and disk I/O just like the 1980s

This is no longer just an interpreter - it's an entire retrocomputing ecosystem where you can write programs, save them to virtual floppies, and experience computing the way it was meant to be: one sector at a time.

## Key Features

### BASIC System
- **64K Memory Space** - Authentic memory map with zero page, stack, screen memory, and more
- **Tokenized Programs** - Keywords stored as single bytes, just like BBC BASIC
- **Direct Token Execution** - Interprets tokenized bytes directly without parsing
- **Memory-Mapped Variables** - Variables live at real addresses you can DUMP
- **Symbol Table with O(1) Access** - Optimized header structure for fast lookups
- **Line-Numbered Programs** - Classic BASIC with automatic line sorting
- **Loop-Based Arithmetic** - Authentic implementation using loops instead of ALU

### NCDOS Disk System 💾
- **Virtual Floppy Disks** - 160KB capacity (40 tracks × 16 sectors × 256 bytes)
- **FAT Filesystem** - Directory with 64 file entries
- **8.3 Filenames** - FILENAME.EXT format
- **Persistent Storage** - .dsk disk image files
- **Complete Disk Operations** - SAVE, LOAD, CATALOG, DELETE

## Quick Start

```bash
# Install and run
git clone https://github.com/bbommarito/zenbasic.git
cd zenbasic
pip install lark
python main.py
```

## Example Session

```
ZenBasic
NCDOS disk formatted
Ready

> 10 LET A% = 100
> 20 LET B% = 200  
> 30 LET C% = A% + B%
> LIST
   10 LET A% = 100
   20 LET B% = 200
   30 LET C% = A% + B%
> RUN
Running program...
> VARS
Variables:
A% = 100
B% = 200
C% = 300

> SAVE MYPROG
Saved 45 bytes to MYPROG.BAS

> NEW
Program cleared

> 10 PRINT "HELLO FROM NCDOS"
> 20 PRINT "THE NINTH CIRCLE OF DOS"
> SAVE HELLO
Saved 52 bytes to HELLO.BAS

> CATALOG
Files on disk:
  HELLO.BAS        52 bytes
  MYPROG.BAS       45 bytes

Total: 2 files, 97 bytes
Free: 159456 bytes

> NEW
Program cleared

> LOAD HELLO
Loaded 2 lines from HELLO.BAS

> RUN
HELLO FROM NCDOS
THE NINTH CIRCLE OF DOS

> QUIT
Goodbye!
```

## Commands

### Program Commands
- `LIST` - Display current program
- `RUN` - Execute stored program
- `NEW` - Clear program and variables
- `VARS` - List all variables

### Disk Commands
- `SAVE filename` - Save program to disk
- `LOAD filename` - Load program from disk
- `CATALOG`/`CAT` - List files on disk
- `DELETE filename` - Delete file from disk

### System Commands
- `MEMORY`/`MAP` - Display memory map
- `DUMP [address]` - Examine memory contents
- `SYMBOLS` - Display symbol table
- `TURBO`/`SLOW` - Toggle arithmetic mode
- `CLS`/`CLEAR` - Clear screen/variables
- `QUIT`/`EXIT` - Exit interpreter

## Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - Technical details and design decisions
- **[Commands Reference](docs/COMMANDS.md)** - Complete list of commands and examples
- **[NCDOS Modes](docs/NCDOS_MODES.md)** - Future multi-mode DOS plans
- **[Development Guide](WARP.md)** - For contributors and developers

## Project Structure

### Core System
- `main.py` - Entry point
- `repl.py` - REPL with disk integration
- `memory.py` - 64K memory management
- `tokenized_program.py` - Tokenized program storage
- `token_executor.py` - Direct token execution
- `commands.py` - Command registry (including disk ops)

### Parser/Transformer
- `transformer.py` - Lark-based parser/transformer
- `parser.py` - BASIC grammar definition
- `arithmetic.py` - Loop-based arithmetic
- `tokens.py` - Token definitions

### NCDOS Components
- `disk.py` - Virtual disk with FAT filesystem
- `rom.py` - ROM system with I/O vectors
- `ncdos.dsk` - Default disk image file

## Memory Map

```
$0000-$00FF  Zero Page       $0800-$0FFF  Variables
$0100-$01FF  Stack           $1000-$EFFF  Program
$0200-$03FF  System/Symbols  $F000-$FFFF  ROM/Hardware
$0400-$07FF  Screen Memory
```

## Roadmap

### Next Up
- [ ] **PRINT statement** - Direct to screen memory
- [ ] **INPUT statement** - Read from keyboard
- [ ] **IF/THEN** - Conditional execution
- [ ] **FOR/NEXT** - Loops
- [ ] **GOTO/GOSUB** - Branching

### Future Enhancements
- [ ] **Text Editor Mode** - Line-based editor like `ed`
- [ ] **Monitor Mode** - Memory inspection and modification
- [ ] **Multiple Disk Drives** - Support for multiple .dsk files
- [ ] **Screen ROM Services** - Proper display handling
- [ ] **PEEK/POKE** - Direct memory access

## Design Philosophy

ZenBasic/NCDOS strives for authenticity:
- **Real Memory** - Programs and variables live in a simulated 64K space
- **True Tokenization** - Keywords stored as bytes, not strings
- **Direct Execution** - Interprets tokens without parsing
- **Authentic Disk Format** - Sector/track structure like real floppies
- **No Shortcuts** - If it was hard in 1983, it's hard now

## Contributing

This is a personal learning project that has grown into something wonderfully absurd. If you share the same nostalgia for early computing and want to contribute, feel free to open an issue or submit a pull request!

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Sophie Wilson and the BBC BASIC team for the brilliant token system
- David Given ([cowlark.com](http://cowlark.com)) for the inspiration to dive into language implementation
- The designers of early disk operating systems (CP/M, DOS 1.0, BBC DFS)
- Everyone who learned to program on an 8-bit machine
- Special recognition to those who understand that sometimes the most pointless projects are the most meaningful

---

*"Welcome to the machine... where have you been?"*
*"In the ninth circle, implementing DOS one sector at a time."*
