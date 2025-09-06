# ZenBasic Commands Reference

## Program Commands

### LET
Assigns a value to a variable.
```basic
LET A% = 42
LET B = 3.14
LET NAME$ = "ZenBasic"  (strings not yet implemented)
```

## Immediate Mode Commands

### LIST
Display the current program with line numbers.
```
> LIST
   10 LET A% = 1
   20 LET B% = A% + 1
```

### RUN
Execute the stored program.
```
> RUN
Running program...
```

### NEW
Clear the current program and all variables.
```
> NEW
```

### CLEAR
Clear all variables (BBC BASIC style).
```
> CLEAR
Variables cleared
```

### CLS
Clear the screen.
```
> CLS
```

### VARS
List all variables and their current values.
```
> VARS
Variables:
A% = 42
B% = 100
```

### SAVE filename
Save the current program to a file.
```
> SAVE myprogram
Program saved to myprogram.bas
```

### LOAD filename
Load a program from a file. (Not yet implemented)
```
> LOAD myprogram
```

## Memory Commands

### DUMP [address]
Display memory contents starting at the specified address.
Supports multiple address formats:
- Decimal: `DUMP 2048`
- Hex with 0x: `DUMP 0x800`
- BBC BASIC style: `DUMP &800`
- 6502 style: `DUMP $800`

```
> DUMP $0800
Memory dump starting at $0800:
$0800: 2A 00 39 05 00 00 00 00 00 00 00 00 00 00 00 00
```

### MEMORY / MAP
Display the memory map and usage statistics.
```
> MEMORY
Memory Map:
$0000-$00FF  Zero Page (256 bytes)
$0100-$01FF  Stack (256 bytes)
$0200-$03FF  System Area (512 bytes)
$0400-$07FF  Screen Memory (1024 bytes)
$0800-$0FFF  Variable Storage (2048 bytes)
$1000-$EFFF  Program Memory (57344 bytes)
$F000-$FFFF  Hardware Registers (4096 bytes)

Statistics:
  Variables defined: 3
  Variable memory: $0806 (6 bytes used, 2042 bytes free)
  Symbol table: 18 bytes used
```

### SYMBOLS
Display the symbol table showing all variables and their memory addresses.
```
> SYMBOLS
Symbol table header:
  Variable count: 2
  Next symbol offset: $0214
  Next variable address: $0804

Symbol table entries at $0208:
  $0208: A% -> $0800 (2 bytes)
  $020E: B% -> $0802 (2 bytes)
```

## System Commands

### HELP
Display available commands.
```
> HELP
Available commands:
  CLEAR      - Clear all variables
  CLS        - Clear the screen
  ...
```

### QUIT / EXIT
Exit the interpreter.
```
> QUIT
Goodbye!
```

### TURBO (Deprecated)
Previously enabled fast arithmetic mode. Now all math uses native operations.

### SLOW (Deprecated)  
Previously disabled fast arithmetic mode. No longer needed.

## Variable Types

### Integer Variables (%)
16-bit signed integers (-32768 to 32767)
```basic
LET COUNT% = 100
LET SCORE% = -50
```

### Floating Point Variables
32-bit floating point numbers
```basic
LET PI = 3.14159
LET TEMPERATURE = 98.6
```

### String Variables ($)
Not yet implemented
```basic
LET NAME$ = "Player 1"
```

## Operators

### Arithmetic
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division

### Precedence
Standard mathematical precedence:
1. Parentheses
2. Multiplication and Division (left to right)
3. Addition and Subtraction (left to right)

## Examples

### Simple Program
```basic
10 LET A% = 10
20 LET B% = 20
30 LET C% = A% + B%
```

### Using Variables in Expressions
```basic
10 LET BASE = 5.5
20 LET HEIGHT = 3.0
30 LET AREA = BASE * HEIGHT / 2
```

### Memory Inspection
```
> LET X% = 1000
> DUMP $0800
Memory dump starting at $0800:
$0800: E8 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```
(1000 = 0x03E8 in little-endian format)
