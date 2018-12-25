import six


class Trace:
    def __init__(self):
        self.trace = []
        self.path_conditions = []
        self.callable = False
        self.line = -1

    def get_trace(self):
        return self.trace

    def set_trace(self, trace):
        self.trace = trace

    def add_to_trace(self, instruction):
        self.trace.append(instruction)

    def get_last_instruction(self):
        idx = len(self.trace) - 1
        return self.trace[idx]

    def get_path_conditions(self):
        return self.path_conditions

    def set_path_conditions(self, path_conditions):
        self.path_conditions = path_conditions[:]

    def get_callable(self):
        return self.callable

    def set_callable(self, _callable):
        self.callable = _callable

    def get_line(self):
        return self.line

    def set_line(self, line):
        self.line = line

    def display(self):
        six.print_("================")
        six.print_("trace size: %d" % len(self.trace))
        six.print_("path condition: %s" % str(self.path_conditions))
        six.print_("callable: %s" % str(self.callable))
        six.print_("line: %d" % self.line)
        for i in range(len(self.trace)):
            six.print_("instruction %d" % i)
            self.trace[i].display()
