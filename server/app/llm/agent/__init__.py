from dspy import Module


class BaseAgent(Module):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, **data):
        if not data.get('name'):
            raise ValueError("name is not set")
        self.name = data.get('name')
