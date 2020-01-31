#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

# Handle faulty commands
if len(sys.argv) < 2:
    print("")
    print("Error: Missing filename")
    print("")
    print("Try command: $python ls8.py <filename>")
    print("")
    quit()

elif len(sys.argv) > 2:
    print("")
    print("Error: Too many arguments provided")
    print("")
    print("Try command: $python ls8.py <filename>")
    print("")
    quit()

cpu = CPU()

cpu.load(sys.argv[1])
cpu.run()