import six


class Trace:
    def __init__(self):
        self.trace = []
        self.path_conditions = []
        self.callable = False
        self.lines = []

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

    def get_lines(self):
        return self.lines

    def set_lines(self, lines):
        self.lines = lines

    def add_line(self, new_line):
        self.lines.append(new_line)

    def display(self):
        six.print_("================")
        six.print_("trace size: %d" % len(self.trace))
        six.print_("path condition: %s" % str(self.path_conditions))
        six.print_("callable: %s" % str(self.callable))
        six.print_("line: %s" % str(self.lines))
        for i in range(len(self.trace)):
            six.print_("instruction %d" % i)
            self.trace[i].display()
