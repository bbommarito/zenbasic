#!/usr/bin/env python3
"""
NCDOS/ZenBasic - Boot to DOS prompt
"""

from ncdos.dos_simple import NCDOSSimple

def main():
    """Boot NCDOS - the primary interface."""
    dos = NCDOSSimple()
    dos.boot()

if __name__ == "__main__":
    main()
