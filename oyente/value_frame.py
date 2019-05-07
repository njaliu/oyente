import logging

log = logging.getLogger(__name__)


class ValueFrame:
    def __init__(self, value, dep):
        self.value = value
        self.dep = dep

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def get_dep(self):
        return self.dep

    def set_dep(self, dep):
        self.dep = dep

    def append2dep(self, value):
        self.dep.append(value)

    def extend2dep(self, values):
        self.dep.extend(values)

    def display(self):
        log.info("Value: " + self.value + ", Dependency: " + self.dep)

