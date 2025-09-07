# NCDOS Multi-Mode Architecture

## Operating Modes

NCDOS can operate in multiple modes, switchable via commands:

### 1. BASIC Mode (Default)
- Current ZenBasic interpreter
- Access to all BASIC commands
- Can SAVE/LOAD programs to disk
- Command: `*BASIC` to enter

### 2. Editor Mode  
- Line-based text editor (like `ed` or BBC Micro's editor)
- Commands:
  - `*EDIT filename` - Start editing
  - Line numbers for navigation
  - `I` - Insert mode
  - `D` - Delete line
  - `L` - List lines
  - `S` - Save and exit
  - `Q` - Quit without saving

### 3. Monitor Mode
- Direct memory inspection/modification
- Like Apple II monitor or C64 monitor
- Commands:
  - `*MON` to enter
  - `M xxxx` - Display memory at address
  - `M xxxx:yyyy` - Display memory range
  - `W xxxx nn` - Write byte to memory
  - `G xxxx` - Execute from address
  - `X` - Exit to BASIC

## Memory Map with Modes

```
$0000-$00FF - Zero page (system workspace)
$0100-$01FF - Stack
$0200-$03FF - Input buffer / Editor line buffer
$0400-$07FF - Screen memory (shared by all modes)
$0800-$EFFF - User space:
  - BASIC programs (tokenized)
  - Editor text buffer
  - User data
$F000-$F7FF - NCDOS ROM (mode switching, I/O)
$F800-$FBFF - BASIC ROM routines
$FC00-$FEFF - Editor ROM routines  
$FF00-$FFFF - System vectors
```

## Implementation Plan

### Phase 1: Mode Infrastructure
```python
class NCDOS:
    def __init__(self):
        self.current_mode = "BASIC"
        self.modes = {
            "BASIC": BasicMode(self),
            "EDIT": EditorMode(self),
            "MON": MonitorMode(self)
        }
```

### Phase 2: Editor Implementation
```python
class EditorMode:
    """
    Line-based text editor
    Stores text in memory as linked list of lines
    """
    def __init__(self, ncdos):
        self.ncdos = ncdos
        self.buffer = []  # List of text lines
        self.current_line = 0
        self.filename = None
```

### Phase 3: Shared Services
- Screen output (all modes write to screen memory)
- Keyboard input (all modes read from input buffer)
- Disk I/O (all modes can save/load files)
- Memory management (allocate regions per mode)

## Command Examples

```
# Start in BASIC mode
> 10 PRINT "HELLO"
> RUN
HELLO

# Switch to editor
> *EDIT HELLO.TXT
NCDOS Editor v1.0
: 1I
Enter text, '.' to end
: Hello from the editor!
: This is line 2.
: .
: S
Saved to HELLO.TXT
: Q

# Back in BASIC
> *CAT
HELLO.TXT     44
PROGRAM.BAS   128

# Enter monitor
> *MON
NCDOS Monitor
* M 0400
0400: 48 65 6C 6C 6F 20 20 20  Hello   
* X

# Back to BASIC
>
```

## Benefits

1. **Authentic**: Matches real 8-bit computer capabilities
2. **Practical**: Can edit both BASIC programs and text files
3. **Educational**: Shows how multi-mode systems worked
4. **Extensible**: Easy to add more modes (assembler, spreadsheet, etc.)

## Technical Considerations

- Mode switching preserves memory where possible
- Each mode has its own command parser
- Shared screen/keyboard/disk routines in ROM
- Memory regions can be protected per mode
- File types (.BAS, .TXT) determine default mode

This makes NCDOS a complete DOS environment, not just a BASIC interpreter!
