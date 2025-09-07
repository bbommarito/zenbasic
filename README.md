# NCDOS / ZenBasic

A complete DOS-based 8-bit computer system implemented in Python. Boot directly to the NCDOS command prompt, just like MS-DOS or CP/M in 1983. Features a working FAT filesystem, virtual floppy disks, and a BBC BASIC interpreter you can launch from DOS.

## About

What started as a BASIC interpreter has evolved into a complete DOS-based computer system, authentically recreating the 1983 computing experience:

- **NCDOS (NinthCircle DOS)**: Boot directly to `A>` prompt, just like MS-DOS or CP/M
- **DOS Commands**: DIR, TYPE, COPY, DEL, REN - manage files from the command line
- **ZenBasic**: Type `BASIC` at the DOS prompt to launch the BBC BASIC interpreter
- **Virtual Floppy Disk**: 160KB disk with FAT filesystem, persistent .dsk files
- **Authentic Architecture**: 64K memory, ROM banking, proper DOS/program separation

This is computing as it was in 1983: boot to DOS, launch programs, return to DOS. No GUI, no mouse, just you and the command prompt.

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

# You'll boot directly to NCDOS:
NCDOS 1.0 - NinthCircle DOS
64K RAM System, 160KB Disk

A>_
```

## Example Session

```
NCDOS 1.0 - NinthCircle DOS
64K RAM System, 160KB Disk

A>DIR

Directory of A:

HELLO    BAS      43
LETTER   TXT     256

2 file(s), 299 bytes
159445 bytes free

A>TYPE LETTER.TXT
Dear User,
Welcome to the Ninth Circle of DOS!
Enjoy your stay.

A>BASIC
Loading BASIC ROM...

ZenBasic
Ready

> 10 LET A% = 100
> 20 LET B% = 200  
> 30 LET C% = A% + B%
> RUN
Running program...
> VARS
Variables:
A% = 100
B% = 200
C% = 300
> SAVE MYPROG
Saved 45 bytes to MYPROG.BAS
> QUIT
Goodbye!

Returned to NCDOS
A>DIR

Directory of A:

HELLO    BAS      43
LETTER   TXT     256
MYPROG   BAS      45

3 file(s), 344 bytes
159400 bytes free

A>EXIT
Goodbye from the Ninth Circle!
```

## Commands

### NCDOS Commands (at A> prompt)
- `DIR` or `CAT` - List files on disk
- `TYPE filename` - Display text file contents
- `COPY source dest` - Copy a file
- `DEL filename` - Delete a file
- `REN old new` - Rename a file
- `CLS` - Clear screen
- `BASIC` - Launch ZenBasic interpreter
- `EDIT filename` - Launch text editor (coming soon)
- `HELP` - Show available commands
- `EXIT` - Exit NCDOS

### BASIC Commands (after typing BASIC)
- `LIST` - Display current program
- `RUN` - Execute stored program
- `NEW` - Clear program and variables
- `VARS` - List all variables
- `SAVE filename` - Save program to disk
- `LOAD filename` - Load program from disk
- `CATALOG` - List files on disk
- `MEMORY` - Display memory map
- `DUMP [address]` - Examine memory contents
- `TURBO`/`SLOW` - Toggle arithmetic mode
- `QUIT` - Return to NCDOS

## Documentation

- **[NCDOS Commands](docs/NCDOS_COMMANDS.md)** - Complete DOS command reference
- **[BASIC Commands](docs/COMMANDS.md)** - ZenBasic interpreter commands
- **[Architecture Overview](docs/ARCHITECTURE.md)** - Technical details and design
- **[NCDOS Modes](docs/NCDOS_MODES.md)** - Future expansion plans
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
