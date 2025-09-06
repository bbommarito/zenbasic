# ZenBasic Architecture

## Overview

ZenBasic is a tokenized BASIC interpreter that simulates an authentic 8-bit computing environment with:
- 64K memory space
- Tokenized program storage
- Direct token execution
- Memory-mapped variables

## Core Components

### Memory System (`memory.py`)
- **64K Address Space**: Full $0000-$FFFF memory simulation
- **Memory Map**:
  ```
  $0000-$00FF  Zero Page (256 bytes)
  $0100-$01FF  Stack (256 bytes)  
  $0200-$03FF  System Area (512 bytes)
  $0400-$07FF  Screen Memory (1KB)
  $0800-$0FFF  Variable Storage (2KB)
  $1000-$EFFF  Program Memory (57KB)
  $F000-$FFFF  Hardware/ROM (4KB)
  ```
- **Header Structure** at $0200:
  - Variable count (16-bit)
  - Next symbol pointer (16-bit)
  - Next variable address (16-bit)
  - PAGE pointer for program start (16-bit)

### Tokenization System (`tokens.py`)
- **BBC BASIC Token Table**: Tokens from $80-$FF
- **Token Storage**: Keywords stored as single bytes
- **Tokenizer**: Converts text to token bytes
- **Detokenizer**: Converts tokens back to text for display

### Program Storage (`tokenized_program.py`)
- **Tokenized Storage**: Programs stored as bytes in memory
- **Line Format**: `[next_ptr:2][line_num:2][tokens...][0x0D]`
- **Linked List**: Lines form a linked list in memory
- **Memory Compaction**: Automatic when replacing lines

### Token Executor (`token_executor.py`)
- **Direct Execution**: Executes tokens without parsing
- **Expression Evaluator**: Handles arithmetic directly on tokens
- **Fallback System**: Falls back to parser for unimplemented statements
- **Native Math**: Uses Python arithmetic (no more loops!)

### Parser System (`parser.py`, `transformer.py`)
- **Lark Grammar**: Defines BASIC syntax
- **AST Transformation**: Converts parse tree to executable form
- **Legacy Path**: Used as fallback for complex statements

### Command System (`commands.py`)
- **Command Registry**: Centralized command handling
- **Immediate Commands**: LIST, RUN, NEW, SAVE, etc.
- **No if/elif chains**: Clean command dispatch

### REPL (`repl.py`)
- **Main Loop**: Read-Eval-Print Loop
- **Line Number Parsing**: Detects program vs immediate mode
- **Execution Router**: Routes to token executor or parser

## Data Flow

### Program Entry
1. User types line with number → Store as tokenized bytes
2. User types immediate command → Execute directly

### Program Storage
1. Text input → Tokenizer → Token bytes
2. Token bytes → Memory storage at $1000+
3. Lines linked via pointers

### Program Execution
1. Read token bytes from memory
2. Token executor interprets bytes directly
3. Falls back to detokenize+parse if needed

### Variable Storage
1. Variables allocated in $0800-$0FFF
2. Symbol table in $0208-$03FF
3. O(1) access via header pointers

## Key Design Decisions

### Why Tokenization?
- **Authentic**: Real 8-bit BASICs used tokens
- **Memory Efficient**: Keywords as single bytes
- **Fast Execution**: No parsing during RUN

### Why Direct Token Execution?
- **Performance**: Skip text parsing entirely
- **Authenticity**: How real interpreters worked
- **Simplicity**: Byte-by-byte interpretation

### Why Memory-Mapped Variables?
- **Realism**: Variables at actual addresses
- **PEEK/POKE Ready**: Direct memory access
- **Educational**: Shows how computers really work

## Future Architecture (NCDOS)

The planned NCDOS layer will add:
- **ROM System**: System calls and I/O handling
- **Virtual Disk**: 160KB floppy simulation
- **Filesystem**: FAT-like with 8.3 filenames
- **Screen Services**: Memory-mapped display
