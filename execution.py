# File: execution.py
# Author: Maryia Mazurava


from program import Program
from var import Variable
from errors import *
import errors as E
import sys

GF_FRAME_NAME = 'GF'
TF_FRAME_NAME = 'TF'
LF_FRAME_NAME = "LF"
VAR_ARG_TYPE = "var"
INT_ARG_TYPE = "int"
STRING_ARG_TYPE = "string"
NIL_ARG_TYPE = "nil"
BOOL_ARG_TYPE = "bool"
TYPE_ARG_TYPE = "type"
LABEL_ARG_TYPE = "label"

# Class representing execution of the program
class Execution:
    data_stack = []
    call_stack = []
    frames = {
        GF_FRAME_NAME: {},
        LF_FRAME_NAME: [],
        TF_FRAME_NAME: None
    }

    def __init__(self, program: Program, args, input_file):
        self.program = program
        self.args = args
        self.input_file = input_file

    # TODO CURRENT_ORDER
    def execute(self, current_order=0):
        for instruction in self.program.instructions[current_order:]:
            # Break the loop if list is empty
            if len(self.program.instructions) == 0:
                break
            match instruction.opcode:
                case "MOVE":
                    self.move_instruction(instruction)
                case "CREATEFRAME":
                    self.createframe_instruction(instruction)
                case "PUSHFRAME":
                    self.pushframe_instruction(instruction)
                case "POPFRAME":
                    self.popframe_instruction(instruction)
                case "DEFVAR":
                    self.defvar_instruction(instruction)
                case "ADD" | "MUL" | "SUB" | "IDIV":
                    self.math_instruction(instruction)
                case "CONCAT":
                    self.concat_instruction(instruction)
                case "WRITE":
                    self.write_instruction(instruction)
                case "SETCHAR":
                    self.setchar_instruction(instruction)
                case "STRLEN":
                    self.strlen_instruction(instruction)
                case "STRI2INT":
                    self.stri2int_instruction(instruction)
                case "INT2CHAR":
                    self.int2char_instruction(instruction)
                case "GETCHAR":
                    self.getchar_instruction(instruction)
                case "TYPE":
                    self.type_instruction(instruction)
                case "EXIT":
                    self.exit_instruction(instruction)
                case "DPRINT":
                    self.dprint_instruction(instruction)
                case "BREAK":
                    self.break_instruction(instruction)
                case "OR" | "AND" | "NOT":
                    self.bool_instruction(instruction)
                case "LT" | "GT" | "EQ":
                    self.relation_instruction(instruction)
                case "PUSHS":
                    self.pushs_instruction(instruction)
                case "POPS":
                    self.pops_instruction(instruction)
                case "READ":
                    self.read_instruction(instruction)
                case "LABEL":
                    self.label_instruction(instruction)
                case "CALL":
                    self.call_instruction(instruction)
                case "JUMPIFEQ" | "JUMPIFNEQ":
                    self.jump_condition_instruction(instruction)
                case "JUMP":
                    self.jump_instruction(instruction)
                case "RETURN":
                    self.return_instruction(instruction)

            # If current instruction is the last - clear the list and terminate the loop
            if len(self.program.instructions) > 0:
                if instruction == self.program.instructions[-1]:
                    self.program.instructions.clear()
                    break

    @staticmethod
    def count_arguments(instruction, expected):
        if len(instruction.arguments) != expected:
            E.error_exit("Error: wrong number of arguments.\n", STRUCTURE_ERROR)

    def get_variable(self, name: str):
        [frame_name, var_name] = name.split("@")
        current_frame = self.get_frame(frame_name)
        if var_name not in current_frame:
            E.error_exit("Error: variable is not defined in this frame.\n", UNDECLARED_VAR_ERROR)

        return current_frame[var_name]

    def get_frame(self, frame_name):
        if frame_name == LF_FRAME_NAME:
            current_frame = self.frames[frame_name][0]
        else:
            current_frame = self.frames[frame_name]
        if current_frame is None:
            E.error_exit("Error: frame doesn't exist.\n", FRAME_ERROR)

        return current_frame

    def set_variable(self, name, variable):
        [frame_name, var_name] = name.split("@")
        current_frame = self.get_frame(frame_name)
        if var_name not in current_frame:
            E.error_exit("Error: variable is not defined in this frame.\n", UNDECLARED_VAR_ERROR)

        current_frame[var_name] = variable

    def check_type(self, symbol):
        if symbol.arg_type == VAR_ARG_TYPE:
            result = self.get_variable(symbol.value)
            if result.value is None:
                E.error_exit("Error: variable has no value.\n", NO_VALUE_ERROR)
            type = result.var_type
            value = result.value
        else:
            type = symbol.arg_type
            value = symbol.value
        return type, value

    def move_instruction(self, instruction):
        self.count_arguments(instruction, 2)

        var_name = instruction.arguments[0]
        symb = instruction.arguments[1]

        if var_name.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        symb_type, symb_value = self.check_type(symb)
        if symb_type == STRING_ARG_TYPE and symb_value is None:
            symb_value = ""

        self.set_variable(var_name.value, Variable(symb_type, symb_value))

    def createframe_instruction(self, instruction):
        self.count_arguments(instruction, 0)
        self.frames[TF_FRAME_NAME] = {}

    def defvar_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        if instruction.arguments[0].arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)
        name = instruction.arguments[0].value

        [frame_name, var_name] = name.split("@")
        current_frame = self.get_frame(frame_name)
        if var_name in current_frame:
            E.error_exit("Error: repeated definition of the variable.\n", SEMANTIC_ERROR)

        current_frame[var_name] = None

    def pushframe_instruction(self, instruction):
        self.count_arguments(instruction, 0)
        if self.frames[TF_FRAME_NAME] is None:
            E.error_exit("Error: frame is not defined.\n", FRAME_ERROR)
        self.frames[LF_FRAME_NAME].append(self.frames[TF_FRAME_NAME])
        self.frames[TF_FRAME_NAME] = None

    def popframe_instruction(self, instruction):
        self.count_arguments(instruction, 0)
        if len(self.frames[LF_FRAME_NAME]) == 0:
            E.error_exit("Error: frame is empty.\n", FRAME_ERROR)
        self.frames[TF_FRAME_NAME] = self.frames[LF_FRAME_NAME].pop()

    def math_instruction(self, instruction):
        self.count_arguments(instruction, 3)

        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        first_op_type, first_op = self.check_type(symb1)
        second_op_type, second_op = self.check_type(symb2)

        if first_op_type != INT_ARG_TYPE or second_op_type != INT_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        if first_op[0] == "-" or second_op[0] == "-":
            if not (first_op[1:].isnumeric() and second_op[1:].isnumeric()):
                E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)
        elif not (first_op.isnumeric() and second_op.isnumeric()):
            E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)

        if instruction.opcode == "ADD":
            result = str(int(first_op) + int(second_op))
        elif instruction.opcode == "MUL":
            result = str(int(first_op) * int(second_op))
        elif instruction.opcode == "SUB":
            result = str(int(first_op) - int(second_op))
        else:
            if second_op == "0":
                E.error_exit("Eror: division by zero.\n", WRONG_VALUE_ERROR)
            result = str(int(int(first_op) / int(second_op)))

        self.set_variable(var.value, Variable(INT_ARG_TYPE, result))

    def concat_instruction(self, instruction):
        self.count_arguments(instruction, 3)

        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        first_op_type, first_op = self.check_type(symb1)
        second_op_type, second_op = self.check_type(symb2)

        if first_op_type != STRING_ARG_TYPE or second_op_type != STRING_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        result = first_op + second_op
        self.set_variable(var.value, Variable(STRING_ARG_TYPE, result))

    def write_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        symb = instruction.arguments[0]
        symb_type, symb_value = self.check_type(symb)

        if symb_type == STRING_ARG_TYPE:
            result = ""
            i = 0
            while i < len(symb_value):
                if symb_value[i] == '\\' and i + 3 < len(symb_value) and symb_value[i + 1:i + 4].isdigit():
                    add = symb_value[i + 1:i + 4].encode().decode("unicode-escape")
                    result += chr(int(add))
                    i += 4
                else:
                    result += symb_value[i]
                    i += 1
        elif symb_type == NIL_ARG_TYPE:
            result = ""
        else:
            result = symb_value
        print(str(result), end='', file=sys.stdout)

    def setchar_instruction(self, instruction):
        self.count_arguments(instruction, 3)

        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        var_op_type, var_op = self.check_type(var)
        first_op_type, first_op = self.check_type(symb1)
        second_op_type, second_op = self.check_type(symb2)

        if var_op_type != STRING_ARG_TYPE or first_op_type != INT_ARG_TYPE or second_op_type != STRING_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        if not first_op.isnumeric() or int(first_op) < 0 or int(first_op) > len(var_op) or second_op == "":
            E.error_exit("Error: operation is not possible.\n", STRING_ERROR)

        src_string = var_op[:int(first_op)] + second_op[0] + var_op[int(first_op) + 1:]
        self.set_variable(var.value, Variable(STRING_ARG_TYPE, src_string))

    def strlen_instruction(self, instruction):
        self.count_arguments(instruction, 2)

        var = instruction.arguments[0]
        symb = instruction.arguments[1]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        symb_type, symb_value = self.check_type(symb)

        if symb_type != STRING_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        result = len(symb_value)
        self.set_variable(var.value, Variable(INT_ARG_TYPE, result))

    def stri2int_instruction(self, instruction):
        self.count_arguments(instruction, 3)

        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)
            exit(STRUCTURE_ERROR)

        first_op_type, first_op = self.check_type(symb1)
        second_op_type, second_op = self.check_type(symb2)

        if first_op_type != STRING_ARG_TYPE or second_op_type != INT_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        if not second_op.isnumeric() or int(second_op) < 0 or int(second_op) > len(first_op) or second_op == "":
            E.error_exit("Error: operation is not possible.\n", STRING_ERROR)

        result = ord(first_op[int(second_op)])
        self.set_variable(var.value, Variable(INT_ARG_TYPE, result))

    def int2char_instruction(self, instruction):
        self.count_arguments(instruction, 2)

        var = instruction.arguments[0]
        symb = instruction.arguments[1]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        symb_type, symb_value = self.check_type(symb)
        if symb_type != INT_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)
        if not symb_value.isnumeric() or not (0 <= int(symb_value) <= 256):
            E.error_exit("Error: operation is not possible.\n", STRING_ERROR)

        result = chr(int(symb_value))
        if len(result) != 1:
            E.error_exit("Error: can't perform an operation.\n", STRING_ERROR)
        self.set_variable(var.value, Variable(STRING_ARG_TYPE, result))

    def getchar_instruction(self, instruction):
        self.count_arguments(instruction, 3)

        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        first_op_type, first_op = self.check_type(symb1)
        second_op_type, second_op = self.check_type(symb2)

        if first_op_type != STRING_ARG_TYPE or second_op_type != INT_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

        if not second_op.isnumeric() or not (0 <= int(second_op) < len(first_op)) or second_op == "":
            E.error_exit("Error: operation is not possible.\n", STRING_ERROR)

        result = first_op[int(second_op)]
        self.set_variable(var.value, Variable(STRING_ARG_TYPE, result))

    def type_instruction(self, instruction):
        self.count_arguments(instruction, 2)

        var = instruction.arguments[0]
        symb = instruction.arguments[1]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        if symb.arg_type == VAR_ARG_TYPE:
            symb_var = self.get_variable(symb.value)
            if symb_var is None:
                result = ""
            else:
                result = symb_var.var_type
        else:
            result = symb.arg_type

        self.set_variable(var.value, Variable(STRING_ARG_TYPE, result))

    def exit_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        symb = instruction.arguments[0]
        symb_type, symb_value = self.check_type(symb)
        if symb_type != INT_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)
        if not symb_value.isnumeric() or not (0 <= int(symb_value) <= 49):
            E.error_exit("Error: invalid exit code.\n", WRONG_VALUE_ERROR)
        exit(int(symb_value))

    def dprint_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        symb = instruction.arguments[0]
        symb_type, symb_value = self.check_type(symb)
        sys.stderr.write(symb_value)

    def break_instruction(self, instruction):
        self.count_arguments(instruction, 0)
        result = str(self.frames) + "\nNumber of executed instructions = " + str(instruction.order) + "\n"
        sys.stderr.write(result)

    def bool_instruction(self, instruction):
        if instruction.opcode == "AND" or instruction.opcode == "OR":
            self.count_arguments(instruction, 3)

            var = instruction.arguments[0]
            symb1 = instruction.arguments[1]
            symb2 = instruction.arguments[2]

            if var.arg_type != VAR_ARG_TYPE:
                E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

            symb1_type, symb1_value = self.check_type(symb1)
            symb2_type, symb2_value = self.check_type(symb2)

            if symb1_type != BOOL_ARG_TYPE or symb2_type != BOOL_ARG_TYPE:
                E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

            if symb1_value not in ["true", "false"] or symb2_value not in ["true", "false"]:
                E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)

            if symb1_value == "true":
                symb1_value = True
            else:
                symb1_value = False

            if symb2_value == "true":
                symb2_value = True
            else:
                symb2_value = False

            if instruction.opcode == "AND":
                result = str(symb1_value and symb2_value).lower()
            else:
                result = str(symb1_value or symb2_value).lower()

            self.set_variable(var.value, Variable(BOOL_ARG_TYPE, result))

        else:
            self.count_arguments(instruction, 2)

            var = instruction.arguments[0]
            symb = instruction.arguments[1]

            if var.arg_type != VAR_ARG_TYPE:
                E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

            symb_type, symb_value = self.check_type(symb)

            if symb_type != BOOL_ARG_TYPE:
                E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

            if symb_value not in ["true", "false"]:
                E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)

            if symb_value == "true":
                symb_value = True
            else:
                symb_value = False

            result = str(not symb_value).lower()
            self.set_variable(var.value, Variable(BOOL_ARG_TYPE, result))

    def relation_instruction(self, instruction):
        self.count_arguments(instruction, 3)
        var = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        symb1_type, symb1_value = self.check_type(symb1)
        symb2_type, symb2_value = self.check_type(symb2)

        if instruction.opcode == "LT" or instruction.opcode == "GT":
            if symb1_type == NIL_ARG_TYPE or symb2_type == NIL_ARG_TYPE:
                E.error_exit("Error: can't apply this instruction with nil operand.\n", OPERAND_TYPE_ERROR)
            if symb1_type != symb2_type or (symb1_type or symb2_type) not in [INT_ARG_TYPE, STRING_ARG_TYPE, BOOL_ARG_TYPE]:
                E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

            if symb1_type == BOOL_ARG_TYPE:
                if symb1_value not in ["true", "false"] or symb2_value not in ["true", "false"]:
                    E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)

                if symb1_value == "true":
                    symb1_value = True
                else:
                    symb1_value = False

                if symb2_value == "true":
                    symb2_value = True
                else:
                    symb2_value = False

            if symb1_type == INT_ARG_TYPE:
                if not (symb1_value.isnumeric() and symb2_value.isnumeric()):
                    E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)
                symb1_value = int(symb1_value)
                symb2_value = int(symb2_value)

            if instruction.opcode == "LT":
                result = str(symb1_value < symb2_value).lower()
            else:
                result = str(symb1_value > symb2_value).lower()
        else:
            if (symb1_type or symb2_type) not in [INT_ARG_TYPE, STRING_ARG_TYPE, BOOL_ARG_TYPE, NIL_ARG_TYPE]:
                E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)

            if symb1_type == NIL_ARG_TYPE or symb2_type == NIL_ARG_TYPE:
                if symb1_type == symb2_type:
                    result = "true"
                else:
                    result = "false"
            else:
                if symb1_type != symb2_type:
                    E.error_exit("Error: wrong type of argument.\n", OPERAND_TYPE_ERROR)
                if symb1_type == BOOL_ARG_TYPE:
                    if symb1_value not in ["true", "false"] or symb2_value not in ["true", "false"]:
                        E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)

                    if symb1_value == "true":
                        symb1_value = True
                    else:
                        symb1_value = False

                    if symb2_value == "true":
                        symb2_value = True
                    else:
                        symb2_value = False

                if symb1_type == INT_ARG_TYPE:
                    if not (symb1_value.isnumeric() and symb2_value.isnumeric()):
                        E.error_exit("Error: wrong value of argument.\n", STRUCTURE_ERROR)
                    symb1_value = int(symb1_value)
                    symb2_value = int(symb2_value)

                result = str(symb1_value == symb2_value).lower()

        self.set_variable(var.value, Variable(BOOL_ARG_TYPE, result))

    def pushs_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        symb = instruction.arguments[0]
        symb_type, symb_value = self.check_type(symb)
        self.data_stack.append([symb_type, symb_value])

    def pops_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        var = instruction.arguments[0]

        if var.arg_type != VAR_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        if len(self.data_stack) == 0:
            E.error_exit("Error: stack is empty.\n", NO_VALUE_ERROR)

        result_type = self.data_stack[-1][0]
        result_value = self.data_stack[-1][1]
        del self.data_stack[-1]
        self.set_variable(var.value, Variable(result_type, result_value))

    def read_instruction(self, instruction):
        self.count_arguments(instruction, 2)
        var = instruction.arguments[0]
        type = instruction.arguments[1]

        if var.arg_type != VAR_ARG_TYPE or type.arg_type != TYPE_ARG_TYPE:
            E.error_exit("Error: wrong type of argument.\n", STRUCTURE_ERROR)

        if type.value not in [INT_ARG_TYPE, BOOL_ARG_TYPE, STRING_ARG_TYPE]:
            E.error_exit("Error: wrong value of.\n", WRONG_VALUE_ERROR)

        if self.args['input'] is None:
            symb = input()
            if symb == "":
                self.set_variable(var.value, Variable(NIL_ARG_TYPE, ""))
            symb = symb.rstrip()
        else:
            symb = self.input_file.readline().strip()
            if symb == "":
                self.set_variable(var.value, Variable(NIL_ARG_TYPE, ""))

        if type.value == INT_ARG_TYPE:
            if not symb.isnumeric():
                symb = ""
            else:
                symb = str(symb)
        elif type.value == STRING_ARG_TYPE:
            symb = str(symb)
        elif type.value == BOOL_ARG_TYPE:
            if symb.lower() == "true":
                symb = "true"
            elif symb.lower() == "false":
                symb = "false"

        self.set_variable(var.value, Variable(INT_ARG_TYPE, symb))

    def label_instruction(self, instruction):
        pass

    def call_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        label = instruction.arguments[0]

        if label.arg_type != LABEL_ARG_TYPE:
            E.error_exit("Error: wrong argument type.\n", STRUCTURE_ERROR)

        if label.value not in self.program.labels:
            E.error_exit("Error: label doesn't exist.\n", SEMANTIC_ERROR)

        order = self.program.labels[label.value]
        self.call_stack.append(int(instruction.order) + 1)
        self.execute(int(order)-1)

    # TODO
    def return_instruction(self, instruction):
        self.count_arguments(instruction, 0)

        if len(self.call_stack) == 0:
            E.error_exit("Error: nowhere to return.\n", NO_VALUE_ERROR)
        order = self.call_stack[-1]
        del self.call_stack[-1]
        self.execute(int(order) - 1)

    def jump_instruction(self, instruction):
        self.count_arguments(instruction, 1)
        label = instruction.arguments[0]

        if label.arg_type != LABEL_ARG_TYPE:
            E.error_exit("Error: wrong argument type.\n", STRUCTURE_ERROR)

        if label.value not in self.program.labels:
            E.error_exit("Error: label doesn't exist.\n", SEMANTIC_ERROR)

        order = self.program.labels[label.value]
        self.execute(int(order) - 1)

    def jump_condition_instruction(self, instruction):
        self.count_arguments(instruction, 3)
        label = instruction.arguments[0]
        symb1 = instruction.arguments[1]
        symb2 = instruction.arguments[2]

        if label.arg_type != LABEL_ARG_TYPE:
            E.error_exit("Error: wrong argument type.\n", STRUCTURE_ERROR)

        if label.value not in self.program.labels:
            E.error_exit("Error: label doesn't exist.\n", SEMANTIC_ERROR)

        symb1_type, symb1_value = self.check_type(symb1)
        symb2_type, symb2_value = self.check_type(symb2)
        order = self.program.labels[label.value]

        if symb1_type == symb2_type or symb1_type == NIL_ARG_TYPE or symb2_type == NIL_ARG_TYPE:
            if instruction.opcode == "JUMPIFEQ":
                if symb1_value == symb2_value:
                    self.execute(int(order) - 1)
            else:
                if symb1_value != symb2_value:
                    self.execute(int(order) - 1)
        else:
            E.error_exit("Error: wrong arguments.\n", OPERAND_TYPE_ERROR)













