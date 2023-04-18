# File: parser.py
# Author: Maryia Mazurava


from xml.etree.ElementTree import ElementTree, Element
from errors import *
import errors as E
from argument import Argument
from instruction import Instruction
from program import Program

OPCODE_ATTRIBUTE = "opcode"
ORDER_ATTRIBUTE = "order"
TYPE_ATTRIBUTE = "type"

# Class representing parser of the XML code
class XMLParser:
    labels = {}
    opcodes = ["MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN",
               "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
               "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR",
               "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK"]

    def __init__(self, tree: ElementTree):
        self.tree = tree

    # Method to parse whole program
    def parse(self):
        root = self.tree.getroot()
        if root.tag != "program":
            E.error_exit('Error: XML file has wrong structure.\n', STRUCTURE_ERROR)

        # Checking the root attributes
        number_of_attributes = 0
        if "language" in root.attrib:
            if root.attrib["language"] != "IPPcode23":
                E.error_exit("Error: invalid language attribute.\n", STRUCTURE_ERROR)
            number_of_attributes += 1
        else:
            E.error_exit("Error: 'language' attribute is needed.\n", STRUCTURE_ERROR)

        if "name" in root.attrib:
            number_of_attributes += 1

        if "description" in root.attrib:
            number_of_attributes += 1

        if len(root.attrib) != number_of_attributes:
            E.error_exit("Error: invalid attributes of 'program' tag.\n", STRUCTURE_ERROR)

        check_duplicates = []
        instructions = [""] * len(root)
        for element in root:
            if element.tag != 'instruction':
                E.error_exit("Error: wrong name of the element 'instruction'.\n", STRUCTURE_ERROR)
            if ORDER_ATTRIBUTE not in element.attrib or OPCODE_ATTRIBUTE not in element.attrib:
                E.error_exit("Error: needed attribute 'order' or 'opcode' is missing.\n", STRUCTURE_ERROR)

            if not element.attrib[ORDER_ATTRIBUTE].isnumeric() or int(element.attrib[ORDER_ATTRIBUTE]) <= 0:
                E.error_exit("Error: invalid order value.\n", STRUCTURE_ERROR)

            if element.attrib[ORDER_ATTRIBUTE] in check_duplicates:
                E.error_exit("Error: wrong order.\n", STRUCTURE_ERROR)
            else:
                check_duplicates.append(element.attrib[ORDER_ATTRIBUTE])

            if element.attrib[OPCODE_ATTRIBUTE].upper() not in self.opcodes:
                E.error_exit("Error: wrong opcode.\n", STRUCTURE_ERROR)

            (order, instruction) = self.parse_instruction(element)
            if order < 1:
                E.error_exit("Error: order must start from 1.\n", STRUCTURE_ERROR)

            if order > len(instructions):
                E.error_exit("Error: wrong order.", STRUCTURE_ERROR)

            # Inserting instruction object to the position in the list according to the order
            if order - 1 < len(instructions) and instructions[order - 1] == "":
                instructions.insert(order-1, instruction)
                del instructions[order]

        return Program(instructions, self.labels)

    # Parses one instruction and returns object of class Instruction and it's order
    def parse_instruction(self, element: Element):
        opcode = element.attrib[OPCODE_ATTRIBUTE].upper()
        instruction_order = int(element.attrib[ORDER_ATTRIBUTE])
        arguments = [""] * len(element)
        for argument in element:
            if len(element) > 3:
                E.error_exit("Error: unexpected arguments.\n", STRUCTURE_ERROR)
            if TYPE_ATTRIBUTE not in argument.attrib:
                E.error_exit("Error: needed attribute 'type' is missing.\n", STRUCTURE_ERROR)
            if argument.attrib[TYPE_ATTRIBUTE] not in ['string', 'int', 'bool', 'label', 'type', 'nil', 'var']:
                E.error_exit("Error: invalid type.\n", STRUCTURE_ERROR)

            (order, argument) = self.parse_argument(argument)
            if order > len(element):
                E.error_exit("Error: missing argument.\n", STRUCTURE_ERROR)
            if arguments[order - 1] != "":
                E.error_exit("Error: duplicated number of argument.\n", STRUCTURE_ERROR)

            # Inserting argument object to the position in the list according to the order
            if order - 1 < len(arguments) and arguments[order - 1] == "":
                arguments.insert(order - 1, argument)
                del arguments[order]

        if element.attrib[OPCODE_ATTRIBUTE].upper() == "LABEL":
            if len(element) != 1:
                E.error_exit("Error: wrong argument type.\n", STRUCTURE_ERROR)
            if argument.arg_type != "label":
                E.error_exit("Error: wrong argument type.\n", STRUCTURE_ERROR)
            if argument.value in self.labels:
                E.error_exit("Error: repeated definition of the label.\n", SEMANTIC_ERROR)
            else:
                self.labels[argument.value] = element.attrib[ORDER_ATTRIBUTE]

        return instruction_order, Instruction(instruction_order, opcode, arguments)

    # Parse one argument and returns object of Argument class and order of the argument
    def parse_argument(self, argument: Element):
        value = argument.text
        if value is not None:
            value = argument.text.strip()
        order = argument.tag[-1]
        if not order.isnumeric() or int(order) > 3 or int(order) < 1:
            E.error_exit("Error: wrong name of the element 'arg'.\n", STRUCTURE_ERROR)
        if argument.tag != 'arg' + str(order):
            E.error_exit("Error: wrong name of the element 'arg'.\n", STRUCTURE_ERROR)
        arg_type = argument.attrib[TYPE_ATTRIBUTE]

        return int(order), Argument(arg_type, value)
