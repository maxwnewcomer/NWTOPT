class OPTSubprocess():
    def __init__(self, type, id, logger):
        self.type = type
        self.id = id
        self.logger = logger

    def __str__(self):
        return f'{self.type}:{self.id}'

    def __repr__(self):
        return f'OPTSubprocess({self.type}, {self.id}, {self.logger})'

    def log(self, msg, warning_level):
        pass

    def run(self):
        pass

    
