# ZenBasic / NCDOS

A Python-based 8-bit computer system featuring BBC BASIC and NinthCircle DOS - a complete disk operating system with FAT filesystem. Born from nostalgia and the beautiful madness of recreating history.

## About

ZenBasic started as a learning project to recreate BASIC programming on early home computers. It has evolved into something beautifully absurd: a complete 8-bit computer system trapped in Python, featuring:

- **ZenBasic**: An authentic BBC BASIC interpreter with tokenized programs and memory-mapped variables
- **NCDOS (NinthCircle DOS)**: A working disk operating system with virtual floppy disks and FAT filesystem
- **Authentic Hardware Emulation**: 64K memory space, ROM banking, and disk I/O just like the 1980s

This is no longer just an interpreter - it's an entire retrocomputing ecosystem where you can write programs, save them to virtual floppies, and experience computing the way it was meant to be: one sector at a time.

## Features

### Currently Implemented

#### BASIC System
- **Interactive REPL** with tokenized program storage
- **Line-numbered programs** - Stored as tokens in memory
- **LET statements** - Variables stored at real memory addresses
- **Variables** - Integer (%), floating point, and strings ($)
- **Arithmetic** - Implemented with loops for authenticity
- **Memory System** - Full 64K address space

#### NCDOS Disk System 💾
- **Virtual Floppy Disks** - 160KB capacity (40 tracks × 16 sectors × 256 bytes)
- **FAT Filesystem** - Directory with 64 file entries
- **8.3 Filenames** - FILENAME.EXT format
- **Persistent Storage** - .dsk disk image files
- **Disk Commands**:
  - `SAVE filename` - Save program to disk
  - `LOAD filename` - Load program from disk
  - `CATALOG`/`CAT` - List files on disk
  - `DELETE filename` - Delete file from disk

#### System Commands
- `LIST` - Display current program
- `RUN` - Execute stored program
- `NEW` - Clear program and variables
- `VARS` - List all variables
- `MEMORY`/`MAP` - Display memory map
- `DUMP [address]` - Examine memory contents
- `TURBO`/`SLOW` - Toggle arithmetic mode
- `CLS`/`CLEAR` - Clear screen/variables
- `QUIT`/`EXIT` - Exit interpreter

### Mathematical "Features" (Working As Intended)
- **Addition by counting** - Why use the ALU when you have loops? Addition is performed by incrementing one-by-one
- **Subtraction by denial** - We don't subtract, we just add negative numbers (with a fake mustache)
- **Multiplication by repeated addition** - Loops inside loops, just as nature intended
- **Division by repeated subtraction** - Count backwards until we can't anymore!
- **Integer overflow** - Store 100,000 in a 16-bit integer? You get 34,464 and you'll like it!
- **Turbo mode** - For when you need 1000 + 1000 to finish before lunch

### Example Session - Now with Disk Support!

```
$ python main.py
ZenBasic
Ready

> LET A% = 42
Allocated A% at address $0800
Stored 42 in memory at $0800
Variable A% set to 42
> LET B% = 1337
Allocated B% at address $0802  
Stored 1337 in memory at $0802
Variable B% set to 1337
> DUMP
Memory dump starting at $0800:
$0800: 2A 00 39 05 00 00 00 00 00 00 00 00 00 00 00 00
> LET C% = A% + B%
Allocated C% at address $0804
Stored 1379 in memory at $0804
Variable C% set to 1379
> 10      LET X = 2 * 3
> 20 LET Y = X / 2  
> LIST
   10      LET X = 2 * 3
   20 LET Y = X / 2
> SAVE myprogram
Program saved to myprogram.bas
> NEW
Program cleared
> LIST
No program in memory

> 10 PRINT "HELLO FROM NCDOS"
> 20 PRINT "THE NINTH CIRCLE OF DOS"
> SAVE HELLO
Saved 52 bytes to HELLO.BAS

> CATALOG
Files on disk:
  HELLO.BAS        52 bytes
  MYPROGRAM.BAS    67 bytes

Total: 2 files, 119 bytes
Free: 159232 bytes

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

## Getting Started

### Requirements
- Python 3.6 or higher
- Lark parser (`pip install lark`)
- Patience for arithmetic operations on large numbers

### Running ZenBasic
```bash
git clone https://github.com/yourusername/zenbasic.git
cd zenbasic
python main.py
```

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

ZenBasic implements a full 64K memory space, just like classic 8-bit computers:

```
$0000-$00FF  Zero Page (256 bytes) - Fast access variables/pointers
$0100-$01FF  Stack (256 bytes) - For subroutine calls later
$0200-$03FF  System Area (512 bytes) - Interpreter state, buffers
$0400-$07FF  Screen Memory (1K) - 40x25 character display  
$0800-$0FFF  Variable Storage (2K) - BASIC variables live here
$1000-$EFFF  Program Memory (57K) - Your BASIC program lines
$F000-$FFFF  Hardware Registers (4K) - Memory-mapped I/O
```

Integer variables (%) are allocated starting at $0800, using 2 bytes each in little-endian format.

### Memory Example
```
> LET A% = 100
Allocated A% at address $0800
Stored 100 in memory at $0800
> LET B% = 256  
Allocated B% at address $0802
Stored 256 in memory at $0802
> DUMP
Memory dump starting at $0800:
$0800: 64 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00
```

## Roadmap

The REPL is just the beginning! Here's what's planned:

- [ ] **PRINT statement** - Output text and variables
- [x] **Variables** - Integer (%), float, and string ($) variables ✓
- [x] **Basic Arithmetic** - All four operations (the hard way) ✓
- [x] **Memory System** - Real memory addresses for variables ✓
- [x] **File I/O** - SAVE programs with whitespace preservation ✓
- [ ] **LOAD command** - Bring those saved programs back to life
- [ ] **Control flow** - IF/THEN, FOR/NEXT, GOTO (but not computed GOTO, we're not animals)
- [ ] **ON x GOTO/GOSUB** - The civilized way to branch
- [ ] **Arrays** - DIM statements and array support
- [ ] **Functions** - Built-in functions like INT(), RND(), etc.
- [ ] **Graphics** - Simple plotting and drawing commands
- [ ] **Sound** - BEEP and simple tone generation
- [ ] **PEEK/POKE** - Direct memory access for the brave

## Why ZenBasic?

In an era of complex development environments and sophisticated toolchains, there's something refreshing about returning to the basics. This project is about:

- **Learning** - Understanding how interpreters work by building one
- **Nostalgia** - Recreating the joy of early computing
- **Simplicity** - Appreciating the elegance of line-by-line programming
- **Authenticity** - If BBC BASIC didn't have an ALU, neither do we!
- **Fun** - Because sometimes the best projects are the ones that make us smile

### Design Philosophy

ZenBasic adheres to strict historical accuracy*:
- Line numbers are mandatory (no cheating with modern editors!)
- Arithmetic is performed using period-appropriate algorithms (counting)
- If it was hard in 1978, it should be hard now
- Commit messages must reference classic songs

*Historical accuracy not actually verified

## Contributing

This is a personal learning project, but if you share the same nostalgia for early computing and want to contribute, feel free to open an issue or submit a pull request!

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- The designers of BBC BASIC and TI BASIC for creating such approachable programming environments
- All the early home computer pioneers who made computing personal
- Everyone who learned to program by typing `10 PRINT "HELLO"` and hitting ENTER
- Special blame/credit to David Given ([GitHub](https://github.com/davidgiven), [cowlark.com](http://cowlark.com)) of [Poking Technology](https://www.youtube.com/@hjalfi) for the inspiration (insanity?) to dive into language implementation through his epic compiler/assembler videos

---

*"The best way to predict the future is to implement it... one line number at a time."*
