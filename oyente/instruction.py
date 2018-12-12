import six

class Instruction:
    def __init__(self, opcode):
        self.opcode = opcode
        self.operands = []

    def get_opcode(self):
        return self.opcode

    def set_opcode(self, opcode):
        self.opcode = opcode

    def get_operands(self):
        return self.operands

    def set_operands(self, operands):
        self.operands = operands

    def add_operand(self, operand):
        self.operands.append(operand)

    def display(self):
        six.print_("opcode: %s" % self.opcode)
        six.print_("operands: %s" % self.operands)
