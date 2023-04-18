# File: interpret.py
# Author: Maryia Mazurava


from execution import Execution
from parser import XMLParser
import xml.etree.ElementTree as ET
from errors import *
import errors as E
import sys


# Read XML file
def read_xml_file(tree, file):
    if tree is not None:
        E.error_exit("Error: tree is not none.\n", PARAM_ERROR)

    try:
        return ET.parse(file)
    except FileNotFoundError:
        E.error_exit("Error: file not found.\n", PARAM_ERROR)
    except ET.ParseError:
        E.error_exit("Error: parse error.\n", FORMAT_ERROR)


# Print help message
def help_info():
    if len(sys.argv) != 2:
        E.error_exit("Error: wrong number of parameters.\n", PARAM_ERROR)
    # TODO: other parameters
    print("interpret.py in Python 3.10.")
    print("Usage: python3.10 interpret.py [--help] [--source=file] [--input=file] [--stats=file] [--insts]")
    print(" --help: prints help message to standard output.")
    print(" --source=file: file with XML code.")
    print(" --input=file: file for the interpretation of the specified source code.")
    print(" --stats=file: file for printing the statistics.")
    print(" --insts: prints the number of so-called executed instructions.")


# Parse command line arguments, open files
def parse_args():
    input_file = None
    tree = None
    args = {
        'help': False,
        'source': None,
        'input': None,
    }
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--help':
            args['help'] = True
            help_info()
            exit(0)
        elif sys.argv[i].split('=')[0] == '--source':
             args['source'] = sys.argv[i].split('=')[1]
             tree = read_xml_file(tree, args['source'])
        elif sys.argv[i].split('=')[0] == '--input':
             args['input'] = sys.argv[i].split('=')[1]
             input_file = open(args['input'], "r")
        else:
            help_info()
            E.error_exit("Error: wrong parameters.\n", PARAM_ERROR)
        i += 1

    if input_file is None and tree is None:
        help_info()
        E.error_exit("Error: not enough arguments.\n", PARAM_ERROR)
    elif tree is None:
         tree = ET.parse(sys.stdin)

    return tree, args, input_file


if __name__ == '__main__':
    tree, args, input_file = parse_args()

    parser = XMLParser(tree)
    program = parser.parse()

    execution = Execution(program, args, input_file)
    execution.execute()


