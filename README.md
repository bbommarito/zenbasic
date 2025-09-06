# ZenBasic

An authentic 8-bit BASIC interpreter with tokenized program storage, direct token execution, and a full 64K memory space - all implemented in Python.

## About

ZenBasic recreates the experience of programming on early home computers like the BBC Micro and Commodore 64. It features authentic tokenized program storage, memory-mapped variables, and direct token execution - just like real 8-bit systems, but running on modern hardware.

## Key Features

- **64K Memory Space** - Authentic memory map with zero page, stack, screen memory, and more
- **Tokenized Programs** - Keywords stored as single bytes, just like BBC BASIC
- **Direct Token Execution** - Interprets tokenized bytes directly without parsing
- **Memory-Mapped Variables** - Variables live at real addresses you can DUMP
- **Symbol Table with O(1) Access** - Optimized header structure for fast lookups
- **Line-Numbered Programs** - Classic BASIC with automatic line sorting
- **Immediate and Program Modes** - Execute commands directly or store them in a program

See [COMMANDS.md](docs/COMMANDS.md) for a complete command reference.

## Quick Start

```bash
# Install and run
git clone https://github.com/bbommarito/zenbasic.git
cd zenbasic
pip install lark
python main.py
```

### Example Session

```
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
> DUMP $0800
Memory dump starting at $0800:
$0800: 64 00 C8 00 2C 01 00 00 00 00 00 00 00 00 00 00
```

## Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - Technical details and design decisions
- **[Commands Reference](docs/COMMANDS.md)** - Complete list of commands and examples
- **[Development Guide](WARP.md)** - For contributors and developers

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
- [ ] **PEEK/POKE** - Direct memory access

### Future (NCDOS)
- [ ] **ROM Layer** - System calls and I/O
- [ ] **Virtual Disk** - 160KB floppy simulation
- [ ] **Filesystem** - FAT-like with DIR, LOAD, SAVE
- [ ] **Screen Services** - Proper display from memory

## Design Philosophy

ZenBasic strives for authenticity:
- **Real Memory** - Programs and variables live in a simulated 64K space
- **True Tokenization** - Keywords stored as bytes, not strings
- **Direct Execution** - Interprets tokens without parsing, like real 8-bit systems
- **No Shortcuts** - If it was hard in 1983, it's hard now

## Contributing

This is a personal learning project, but if you share the same nostalgia for early computing and want to contribute, feel free to open an issue or submit a pull request!

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Sophie Wilson and the BBC BASIC team for the brilliant token system
- David Given ([cowlark.com](http://cowlark.com)) for the inspiration to dive into language implementation
- Everyone who learned to program on an 8-bit machine

---

*"The best way to predict the future is to implement it... one line number at a time."*
