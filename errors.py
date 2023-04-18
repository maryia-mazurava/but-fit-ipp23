# File: errors.py
# Author: Maryia Mazurava


import sys

PARAM_ERROR = 10
INPUT_ERROR = 11
OUTPUT_ERROR = 12
FORMAT_ERROR = 31
STRUCTURE_ERROR = 32
SEMANTIC_ERROR = 52
OPERAND_TYPE_ERROR = 53
UNDECLARED_VAR_ERROR = 54
FRAME_ERROR = 55
NO_VALUE_ERROR = 56
WRONG_VALUE_ERROR = 57
STRING_ERROR = 58

# Prints error message to stderr and exits the program with the code
def error_exit(message: str, error: int):
    sys.stderr.write(message)
    exit(error)
