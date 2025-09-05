# ZenBasic Refactoring Ideas

## Current Issues
1. `zenBasicRepl.py` is getting large (245 lines) with mixed responsibilities
2. Memory management, command handling, and program storage are all in one class
3. The giant if/elif chain in `execute_immediate_command` is getting unwieldy
4. Arithmetic operations are mixed with parsing logic in `basicTransformer.py`

## Proposed Module Structure

### 1. `memory.py` - Memory Management
```python
class MemoryManager:
    - __init__(size=65536)
    - store_int16(address, value)
    - read_int16(address) 
    - dump(start_address, length)
    - allocate_variable(name, size) -> address
    - Memory map constants (ZERO_PAGE, STACK, VARS_START, etc.)
```

### 2. `variables.py` - Variable Storage
```python
class VariableManager:
    - __init__(memory_manager)
    - set_variable(name, value, type)
    - get_variable(name)
    - list_variables()
    - clear_variables()
    - Store both in dict AND memory
```

### 3. `program.py` - Program Storage
```python
class ProgramStore:
    - add_line(line_num, code)
    - delete_line(line_num)
    - get_line(line_num)
    - list_program()
    - clear_program()
    - save_to_file(filename)
    - load_from_file(filename)
```

### 4. `commands.py` - Command Registry
```python
class CommandRegistry:
    - register_command(name, handler)
    - execute_command(command_str)
    - Built-in commands as separate functions
    
def cmd_list(repl): ...
def cmd_run(repl): ...
def cmd_save(repl, filename): ...
# etc.
```

### 5. `arithmetic.py` - Arithmetic Operations
```python
class AuthenticArithmetic:
    - add_by_loop(a, b)
    - sub_by_loop(a, b)
    - multiply_by_addition(a, b)
    - div_by_loop(a, b)
    - Can toggle turbo mode
```

### 6. `parser.py` - Grammar and Parsing
```python
# Move BASIC_GRAMMAR here
# Keep parser initialization separate
```

### 7. `executor.py` - Program Execution
```python
class ProgramExecutor:
    - __init__(parser, transformer, variables)
    - execute_line(line_num, code)
    - run_program(program_store)
    - Handle execution context (GOSUB stack later)
```

## Benefits

1. **Single Responsibility**: Each module has one clear job
2. **Testability**: Can unit test arithmetic without REPL
3. **Extensibility**: Easy to add new commands or memory features
4. **Readability**: Find code where you expect it
5. **Command Pattern**: New commands just need registration
6. **Future-Proof**: Ready for GOSUB stack, arrays, etc.

## Migration Strategy

1. Start with `memory.py` - easiest to extract
2. Move arithmetic to its own module
3. Extract command handlers one by one
4. Create command registry last
5. Keep backward compatibility during migration

## Example Command Registration

```python
# In commands.py
registry = CommandRegistry()
registry.register("LIST", cmd_list)
registry.register("RUN", cmd_run)
registry.register("SAVE", cmd_save, takes_args=True)
registry.register("DUMP", cmd_dump, takes_args=True, optional_args=True)

# In zenBasicRepl.py
if not self.commands.try_execute(command):
    # Try to parse as BASIC statement
    self.execute_statement(command)
```

## Future Considerations

- `screen.py` for when we add PRINT and screen memory
- `sound.py` for BEEP and tones
- `graphics.py` for plotting commands
- `stack.py` for GOSUB/RETURN stack management
