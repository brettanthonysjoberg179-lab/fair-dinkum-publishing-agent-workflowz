# base.py

class BaseAgent:
    def __init__(self, project_id):
        self.project_id = project_id
        self.status = 'initialized'
        self.inputs = {}
        self.outputs = {}

    def execute(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def set_input(self, key, value):
        self.inputs[key] = value

    def get_output(self, key):
        return self.outputs.get(key)

    def update_status(self, new_status):
        self.status = new_status
