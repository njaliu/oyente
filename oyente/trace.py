import six

class Trace:
    def __init__(self):
        self.trace = []

    def get_trace(self):
        return self.trace

    def set_trace(self, trace):
        self.trace = trace

    def add_to_trace(self, instruction):
        self.trace.append(instruction)

    def get_last_instruction(self):
        idx = len(self.trace) - 1
        return self.trace[idx]

    def display(self):
        six.print_("================")
        six.print_("trace size: %d" % len(self.trace))
        for i in range(len(self.trace)):
            six.print_("instruction %d" % i)
            self.trace[i].display()
