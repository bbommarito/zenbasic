# ZenBasic

A Python-based interpreter for BBC BASIC, born from nostalgia and a love for the simplicity of early computing.

## About

ZenBasic is a learning project that recreates the experience of programming in BASIC on early home computers. It's inspired by memories of sitting in front of a tiny 13" TV with a TI-99/4A, typing out BASIC code and watching programs come to life one line at a time.

This project aims to capture that same sense of immediacy and simplicity that made early computers so engaging - where you could type a line number, enter some code, and build your program interactively.

## Features

### Currently Implemented
- **Interactive REPL** (Read-Eval-Print Loop)
- **Line-numbered program storage** - Just like classic BASIC!
- **Immediate mode commands**:
  - `LIST` - Display the current program
  - `RUN` - Execute the stored program
  - `NEW` - Clear the current program
  - `QUIT`/`EXIT` - Exit the interpreter

### Example Session

```
$ python main.py
ZenBasic
Ready

> 10 PRINT "Hello, World!"
Line 10 stored
> 20 PRINT "Welcome to ZenBasic"
Line 20 stored
> LIST
   10 PRINT "Hello, World!"
   20 PRINT "Welcome to ZenBasic"
> RUN
Running program...
[Would execute: 10 PRINT "Hello, World!"]
[Would execute: 20 PRINT "Welcome to ZenBasic"]
Program finished
> NEW
Program cleared
> QUIT
Goodbye!
```

## Getting Started

### Requirements
- Python 3.6 or higher

### Running ZenBasic
```bash
git clone https://github.com/yourusername/zenbasic.git
cd zenbasic
python main.py
```

## Project Structure
- `main.py` - Entry point for the application
- `zenBasicRepl.py` - Core REPL implementation
- `.gitignore` - Git ignore file for Python projects

## Roadmap

The REPL is just the beginning! Here's what's planned:

- [ ] **PRINT statement** - Output text and variables
- [ ] **Variables** - LET statements and variable assignment
- [ ] **Arithmetic** - Basic math operations
- [ ] **Control flow** - IF/THEN, FOR/NEXT, GOTO
- [ ] **String handling** - String variables and manipulation
- [ ] **Arrays** - DIM statements and array support
- [ ] **Functions** - Built-in functions like INT(), RND(), etc.
- [ ] **Graphics** - Simple plotting and drawing commands
- [ ] **Sound** - BEEP and simple tone generation
- [ ] **File I/O** - SAVE and LOAD programs

## Why ZenBasic?

In an era of complex development environments and sophisticated toolchains, there's something refreshing about returning to the basics. This project is about:

- **Learning** - Understanding how interpreters work by building one
- **Nostalgia** - Recreating the joy of early computing
- **Simplicity** - Appreciating the elegance of line-by-line programming
- **Fun** - Because sometimes the best projects are the ones that make us smile

## Contributing

This is a personal learning project, but if you share the same nostalgia for early computing and want to contribute, feel free to open an issue or submit a pull request!

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- The designers of BBC BASIC and TI BASIC for creating such approachable programming environments
- All the early home computer pioneers who made computing personal
- Everyone who learned to program by typing `10 PRINT "HELLO"` and hitting ENTER

---

*"The best way to predict the future is to implement it... one line number at a time."*
