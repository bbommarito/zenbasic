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
- **Variables** - Store integers in classic BASIC style (A through Z and beyond!)
- **Arithmetic** - Addition and subtraction implemented the *authentic* way (see below)
- **Immediate mode commands**:
  - `LIST` - Display the current program
  - `RUN` - Execute the stored program (now actually runs!)
  - `NEW` - Clear the current program
  - `VARS` - List all variables and their values
  - `QUIT`/`EXIT` - Exit the interpreter

### Mathematical "Features" (Working As Intended)
- **Addition by counting** - Why use the ALU when you have loops? Addition is performed by incrementing one-by-one
- **Subtraction by denial** - We don't subtract, we just add negative numbers (with a fake mustache)
- **No negative literals** - Want `-5`? Better calculate `0 - 5` like it's 1978!
- **Multiplication** - Coming soon: loops inside loops!
- **Division** - Coming soon: repeated subtraction until we can't anymore!

### Example Session

```
$ python main.py
ZenBasic
Ready

> LET A = 5
Variable A set to 5
> LET B = 3
Variable B set to 3
> LET C = A + B
Variable C set to 8
> VARS
Variables:
A = 5
B = 3
C = 8
> 10 LET X = 2 + 3
> 20 LET Y = X - 1
> LIST
   10 LET X = 2 + 3
   20 LET Y = X - 1
> RUN
Running program...
Executing line 10: LET X = 2 + 3
Variable X set to 5
Executing line 20: LET Y = X - 1
Variable Y set to 4
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

## Roadmap

The REPL is just the beginning! Here's what's planned:

- [ ] **PRINT statement** - Output text and variables
- [x] **Variables** - LET statements and variable assignment ✓
- [x] **Basic Arithmetic** - Addition and subtraction (the hard way) ✓
- [ ] **More Arithmetic** - Multiplication (nested loops!), Division (count backwards!)
- [ ] **Negative numbers** - Currently `LET A = -5` explodes. Feature or bug? You decide!
- [ ] **Control flow** - IF/THEN, FOR/NEXT, GOTO (but not computed GOTO, we're not animals)
- [ ] **ON x GOTO/GOSUB** - The civilized way to branch
- [ ] **String handling** - String variables and manipulation
- [ ] **Arrays** - DIM statements and array support
- [ ] **Functions** - Built-in functions like INT(), RND(), etc.
- [ ] **Graphics** - Simple plotting and drawing commands
- [ ] **Sound** - BEEP and simple tone generation
- [ ] **File I/O** - SAVE and LOAD programs (with proper whitespace preservation!)

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
