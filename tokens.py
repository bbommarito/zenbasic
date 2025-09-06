"""
BBC BASIC Token Definitions
Because Sophie Wilson and team knew what they were doing in 1981

Token values from 0x80-0xFF are used for keywords
0x00-0x7F remain as regular ASCII characters
"""

# BBC BASIC Token Map - straight from the BBC Micro manual
TOKENS = {
    # 0x80-0x8F
    0x80: "AND",
    0x81: "DIV",
    0x82: "EOR",
    0x83: "MOD", 
    0x84: "OR",
    0x85: "ERROR",
    0x86: "LINE",
    0x87: "OFF",
    0x88: "STEP",
    0x89: "SPC",
    0x8A: "TAB(",
    0x8B: "ELSE",
    0x8C: "THEN",
    0x8D: "<line>",  # Used for line number references in tokenized code
    0x8E: "OPENIN",
    0x8F: "PTR",
    
    # 0x90-0x9F
    0x90: "PAGE",
    0x91: "TIME",
    0x92: "LOMEM",
    0x93: "HIMEM",
    0x94: "ABS",
    0x95: "ACS",
    0x96: "ADVAL",
    0x97: "ASC",
    0x98: "ASN",
    0x99: "ATN",
    0x9A: "BGET",
    0x9B: "COS",
    0x9C: "COUNT",
    0x9D: "DEG",
    0x9E: "ERL",
    0x9F: "ERR",
    
    # 0xA0-0xAF
    0xA0: "EVAL",
    0xA1: "EXP",
    0xA2: "EXT",
    0xA3: "FALSE",
    0xA4: "FN",
    0xA5: "GET",
    0xA6: "INKEY",
    0xA7: "INSTR(",
    0xA8: "INT",
    0xA9: "LEN",
    0xAA: "LN",
    0xAB: "LOG",
    0xAC: "NOT",
    0xAD: "OPENUP",
    0xAE: "OPENOUT",
    0xAF: "PI",
    
    # 0xB0-0xBF
    0xB0: "POINT(",
    0xB1: "POS",
    0xB2: "RAD",
    0xB3: "RND",
    0xB4: "SGN",
    0xB5: "SIN",
    0xB6: "SQR",
    0xB7: "TAN",
    0xB8: "TO",
    0xB9: "TRUE",
    0xBA: "USR",
    0xBB: "VAL",
    0xBC: "VPOS",
    0xBD: "CHR$",
    0xBE: "GET$",
    0xBF: "INKEY$",
    
    # 0xC0-0xCF
    0xC0: "LEFT$(",
    0xC1: "MID$(",
    0xC2: "RIGHT$(",
    0xC3: "STR$",
    0xC4: "STRING$",
    0xC5: "EOF",
    0xC6: "AUTO",  # Extended token
    0xC7: "DELETE",  # Extended token
    0xC8: "LOAD",
    0xC9: "LIST",
    0xCA: "NEW",
    0xCB: "OLD",
    0xCC: "RENUMBER",
    0xCD: "SAVE",
    0xCE: "PUT",  # Extended token
    0xCF: "PTR",  # Extended token
    
    # 0xD0-0xDF
    0xD0: "CONT",  # Continue
    0xD1: "CLEAR",
    0xD2: "CLOSE",
    0xD3: "CLG",
    0xD4: "CLS",
    0xD5: "DATA",
    0xD6: "DEF",
    0xD7: "DIM",
    0xD8: "DRAW",
    0xD9: "END",
    0xDA: "ENDPROC",
    0xDB: "ENVELOPE",
    0xDC: "FOR",
    0xDD: "GOSUB",
    0xDE: "GOTO",
    0xDF: "GCOL",
    
    # 0xE0-0xEF
    0xE0: "IF",
    0xE1: "INPUT",
    0xE2: "LET",
    0xE3: "LOCAL",
    0xE4: "MODE",
    0xE5: "MOVE",
    0xE6: "NEXT",
    0xE7: "ON",
    0xE8: "VDU",
    0xE9: "PLOT",
    0xEA: "PRINT",
    0xEB: "PROC",
    0xEC: "READ",
    0xED: "REM",
    0xEE: "REPEAT",
    0xEF: "REPORT",
    
    # 0xF0-0xFF
    0xF0: "RESTORE",
    0xF1: "RETURN",
    0xF2: "RUN",
    0xF3: "STOP",
    0xF4: "COLOUR",
    0xF5: "TRACE",
    0xF6: "UNTIL",
    0xF7: "WIDTH",
    0xF8: "OSCLI",
    0xF9: "ESCAPE",  # Extended/special
    0xFA: "TAB",     # Extended tab without (
    0xFB: "QUIT",    # Our addition
    0xFC: "HELP",    # Our addition
    0xFD: "TURBO",   # Our addition
    0xFE: "SLOW",    # Our addition
    0xFF: "VARS",    # Our addition
}

# Reverse mapping for tokenization
KEYWORDS_TO_TOKENS = {keyword: token for token, keyword in TOKENS.items() if keyword != "<line>"}

# Add our ZenBasic specific mappings
KEYWORDS_TO_TOKENS.update(ZENBASIC_TOKENS)

# Special tokens
TOKEN_LINE_NUM = 0x8D  # Followed by 2-byte line number
TOKEN_EOL = 0x0D       # End of line marker (carriage return)

# For ZenBasic specific commands that don't have BBC equivalents, 
# we'll use the 0xF9-0xFF range that BBC BASIC left for extensions
ZENBASIC_TOKENS = {
    "QUIT": 0xFB,
    "HELP": 0xFC,
    "TURBO": 0xFD,
    "SLOW": 0xFE,
    "VARS": 0xFF,
    "MEMORY": 0xF6,  # Reuse UNTIL token (we don't have UNTIL yet)
    "MAP": 0xF6,     # Alias for MEMORY
    "EXIT": 0xFB,    # Alias for QUIT
    "SYMBOLS": 0xFA, # Extended slot
    "DUMP": 0xF9,    # Extended slot
}

# Note: Our CLEAR is an alias for CLS (0xD4), not BBC's CLEAR (0xD1)
# BBC's CLEAR cleared variables, ours clears the screen

def tokenize_line(line: str) -> bytes:
    """
    Tokenize a BASIC line, converting keywords to their token bytes.
    Preserves strings and handles special cases.
    """
    result = []
    i = 0
    in_string = False
    in_rem = False
    
    while i < len(line):
        if in_string:
            # Inside a string, keep everything as-is
            if line[i] == '"':
                in_string = False
            result.append(ord(line[i]))
            i += 1
        elif in_rem:
            # After REM, keep everything as-is
            result.append(ord(line[i]))
            i += 1
        else:
            # Check for string start
            if line[i] == '"':
                in_string = True
                result.append(ord('"'))
                i += 1
            # Check for keywords
            else:
                found_keyword = False
                # Try to match keywords, longest first
                for length in range(min(8, len(line) - i), 0, -1):
                    word = line[i:i+length].upper()
                    if word in KEYWORDS_TO_TOKENS:
                        result.append(KEYWORDS_TO_TOKENS[word])
                        if word == "REM":
                            in_rem = True
                        i += length
                        found_keyword = True
                        break
                
                if not found_keyword:
                    # Not a keyword, keep the character
                    result.append(ord(line[i]))
                    i += 1
    
    return bytes(result)

def detokenize(tokens: bytes) -> str:
    """
    Convert tokenized bytes back to BASIC text.
    """
    result = []
    i = 0
    in_string = False
    in_rem = False
    
    while i < len(tokens):
        byte = tokens[i]
        
        if byte >= 0x80:
            # It's a token
            keyword = TOKENS.get(byte, f"<{byte:02X}>")
            result.append(keyword)
            if keyword == "REM":
                in_rem = True
        elif byte == ord('"'):
            # Quote toggles string mode
            in_string = not in_string
            result.append('"')
        else:
            # Regular ASCII character
            result.append(chr(byte))
        
        i += 1
    
    return ''.join(result)
