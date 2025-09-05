# ZenBasic

A Python-based interpreter for BBC BASIC, born from nostalgia and a love for the simplicity of early computing.

## About

ZenBasic is a learning project that recreates the experience of programming in BASIC on early home computers. It's inspired by memories of sitting in front of a tiny 13" TV with a TI-99/4A, typing out BASIC code and watching programs come to life one line at a time.

This project aims to capture that same sense of immediacy and simplicity that made early computers so engaging - where you could type a line number, enter some code, and build your program interactively.

## Features

### Currently Implemented
- **Interactive REPL** (Read-Eval-Print Loop)
- **Line-numbered program storage** - Just like classic BASIC!
- **LET statements** - Assign values to variables (uppercase names only, like a proper BASIC)
- **Variables** - Integer (%), floating point, and strings ($) in classic BASIC style
- **Real Memory System** - Variables stored at actual memory addresses!
- **Arithmetic** - All four operations implemented the *authentic* way (see below)
- **Immediate mode commands**:
  - `LIST` - Display the current program
  - `RUN` - Execute the stored program
  - `NEW` - Clear the current program  
  - `VARS` - List all variables and their values
  - `CLS`/`CLEAR` - Clear the screen
  - `SAVE filename` - Save your program (with whitespace preserved!)
  - `DUMP [address]` - Examine memory contents
  - `TURBO`/`SLOW` - Toggle fast arithmetic mode
  - `QUIT`/`EXIT` - Exit the interpreter

### Mathematical "Features" (Working As Intended)
- **Addition by counting** - Why use the ALU when you have loops? Addition is performed by incrementing one-by-one
- **Subtraction by denial** - We don't subtract, we just add negative numbers (with a fake mustache)
- **Multiplication by repeated addition** - Loops inside loops, just as nature intended
- **Division by repeated subtraction** - Count backwards until we can't anymore!
- **Integer overflow** - Store 100,000 in a 16-bit integer? You get 34,464 and you'll like it!
- **Turbo mode** - For when you need 1000 + 1000 to finish before lunch

### Example Session

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
- `main.py` - Entry point for the application
- `zenBasicRepl.py` - Core REPL implementation
- `basicTransformer.py` - Lark-based parser and transformer (where the mathematical magic happens)
- `.gitignore` - Git ignore file for Python projects

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
