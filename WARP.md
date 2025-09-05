# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ZenBasic is a Python-based interpreter for BBC BASIC that recreates the experience of programming on early home computers. It features an intentionally "authentic" implementation where arithmetic operations are performed through loops rather than using built-in operators.

## Key Architecture

The project follows a classic interpreter architecture:

1. **main.py** - Entry point that instantiates and runs the REPL
2. **zenBasicRepl.py** - Core REPL implementation handling:
   - Line number parsing and program storage
   - Immediate command execution (LIST, RUN, NEW, VARS, QUIT)
   - Program execution line-by-line
   - Variable storage as a dictionary
   - Turbo mode toggle for faster arithmetic

3. **basicTransformer.py** - Lark-based parser and AST transformer:
   - Grammar definition for BASIC syntax
   - Arithmetic operations implemented via loops (add_by_loop, sub_by_loop, multiply_by_addition, div_by_loop)
   - Turbo mode shortcuts that use native operators
   - Variable resolution and storage

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

### Parser Modifications
- Grammar is defined in `BASIC_GRAMMAR` string in basicTransformer.py
- Use Lark parser syntax for new statements
- Follow the existing pattern: create grammar rule → implement transformer method

### Adding New BASIC Commands
1. For immediate commands: Add to `execute_immediate_command()` in zenBasicRepl.py
2. For program statements: 
   - Add grammar rule in basicTransformer.py
   - Implement corresponding transformer method
   - Ensure proper variable storage/retrieval

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
2. If line number: Store in program_lines dict
3. If immediate: Execute through parser/transformer
4. RUN command executes stored lines sequentially

### State Management
- `self.program_lines`: Dict[int, str] - Stores numbered program lines
- `self.variables`: Dict[str, Any] - Stores variable values
- `self.turbo`: bool - Performance mode flag

### Error Handling
- Parser errors are caught and displayed
- Runtime errors stop program execution
- Division by zero is explicitly handled
