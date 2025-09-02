

class Agent():

    def __init__(self,model, tools,memory):
        self.model = model
        self.model.initialize(tools,memory)

    def run(self, user, context, question):
        return self.model.process(user, context,question)