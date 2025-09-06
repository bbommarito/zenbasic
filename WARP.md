# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ZenBasic is a Python-based interpreter for BBC BASIC that recreates the experience of programming on early home computers. It features an intentionally "authentic" implementation where arithmetic operations are performed through loops rather than using built-in operators.

## Key Architecture

The project uses a dual-path execution model:

### Core Components

1. **main.py** - Entry point
2. **repl.py** - Main REPL loop and command dispatch
3. **memory.py** - 64K memory management with authentic address space
4. **tokens.py** - BBC BASIC token table and tokenization
5. **tokenized_program.py** - Program storage in tokenized form
6. **token_executor.py** - Direct token execution (fast path)
7. **parser.py** - Lark grammar definition (fallback path)
8. **transformer.py** - AST transformation (fallback path)
9. **commands.py** - Command registry and handlers

## Development Commands

### Running the Interpreter
```bash
python main.py
```

### Installing Dependencies
```bash
pip install lark
```

### Running Tests
*Note: No test suite currently exists. When implementing tests, create test files for each module.*

## Development Guidelines

### Adding New Commands

#### Immediate Commands
1. Add handler function to `commands.py`
2. Register in `CommandRegistry.register_built_in_commands()`

#### Program Statements (e.g., PRINT, IF)
1. Add token definition to `tokens.py` if needed
2. Implement in `token_executor.py` for direct execution
3. Optionally add to parser grammar as fallback

### Memory Layout
- Programs stored as tokenized bytes at $1000-$EFFF
- Variables allocated at $0800-$0FFF
- Symbol table at $0208-$03FF with O(1) header at $0200
- Screen memory at $0400-$07FF (future use)

### Execution Flow
1. **Tokenization**: Text → Token bytes via `tokenize_line()`
2. **Storage**: Tokens stored in memory as linked list
3. **Execution**: Token executor reads bytes directly
4. **Fallback**: Complex statements fall back to parser

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
3. If immediate: Execute via command registry or token executor
4. RUN command executes tokens directly from memory

### State Management
- **Memory**: 64K bytearray simulating complete address space
- **Programs**: Stored as tokenized bytes in memory ($1000+)
- **Variables**: Allocated in memory with symbol table
- **No dictionaries**: Everything lives in the 64K memory!

### Error Handling
- Parser errors are caught and displayed
- Runtime errors stop program execution
- Division by zero is explicitly handled
