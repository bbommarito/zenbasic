# NCDOS Command Reference

## Overview

NCDOS (NinthCircle DOS) is a command-line disk operating system that manages files and launches programs. It boots directly to the `A>` prompt, just like MS-DOS, CP/M, and other DOS systems of the early 1980s.

## DOS Commands

All commands can be typed at the `A>` prompt. Commands are not case-sensitive.

### File Management

#### DIR / CAT
List all files on the current disk.
```
A>DIR

Directory of A:

HELLO    BAS      43
LETTER   TXT     256

2 file(s), 299 bytes
159445 bytes free
```

#### TYPE filename
Display the contents of a text file.
```
A>TYPE LETTER.TXT
Dear User,
Welcome to the Ninth Circle of DOS!
```

#### COPY source destination
Copy a file to a new name.
```
A>COPY LETTER.TXT BACKUP.TXT
Copied LETTER.TXT to BACKUP.TXT
```

#### DEL / DELETE filename
Delete a file from disk.
```
A>DEL BACKUP.TXT
Deleted BACKUP.TXT
```

#### REN / RENAME oldname newname
Rename a file.
```
A>REN LETTER.TXT MESSAGE.TXT
Renamed LETTER.TXT to MESSAGE.TXT
```

### System Commands

#### CLS / CLEAR
Clear the screen.
```
A>CLS
```

#### HELP
Display available commands.
```
A>HELP

NCDOS Commands:

  DIR/CAT         - List files
  TYPE filename   - Display file
  ...
```

#### EXIT / QUIT
Exit NCDOS.
```
A>EXIT
Goodbye from the Ninth Circle!
```

### Program Launching

#### BASIC
Launch the ZenBasic interpreter.
```
A>BASIC
Loading BASIC ROM...

ZenBasic
Ready

>
```

To return to DOS from BASIC, type `QUIT`:
```
>QUIT
Goodbye!

Returned to NCDOS
A>
```

#### EDIT [filename]
Launch the text editor (coming soon).
```
A>EDIT LETTER.TXT
Loading EDITOR ROM...
EDITOR not yet implemented
```

## File Types

NCDOS uses the 8.3 filename format (8 character name, 3 character extension):

- `.BAS` - BASIC program files
- `.TXT` - Text files
- `.DAT` - Data files

If no extension is specified:
- Text commands (TYPE, EDIT) assume `.TXT`
- BASIC commands assume `.BAS`

## Disk Information

- **Capacity**: 160KB (163,840 bytes)
- **Structure**: 40 tracks × 16 sectors × 256 bytes/sector
- **File System**: FAT-like with directory and allocation table
- **Max Files**: 64 directory entries
- **System Reserved**: Track 0 (boot sector, directory, FAT)

## Tips

1. **Case Insensitive**: Commands can be typed in any case
2. **Wildcards**: Not yet supported (coming soon)
3. **Paths**: Single directory only (no subdirectories yet)
4. **File Recovery**: Deleted files cannot be recovered
5. **Disk Image**: All data is stored in `ncdos.dsk`

## Future Commands

These commands are planned for future implementation:

- `FORMAT` - Format a disk
- `CHKDSK` - Check disk integrity
- `COMP` - Compare two files
- `PRINT` - Print a file (to screen for now)
- `BACKUP` - Backup entire disk
- `RESTORE` - Restore from backup

## Authentic 1983 Experience

NCDOS recreates the authentic DOS experience of 1983:

- No mouse support (keyboard only)
- No GUI (command line interface)
- No multitasking (one program at a time)
- No long filenames (8.3 format only)
- No directories (flat file system)
- No undo (be careful with DEL!)

This is computing as it was meant to be: you, a command prompt, and 160KB of storage.

Welcome to A>_
