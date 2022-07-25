class OPTSubprocess():
    """
    NWTOPT Subprocess Super class
    """
    def __init__(self, type, id, logger):
        """
        Initialization
        """
        self.type = type
        self.id = id
        self.logger = logger
        self.pid = None

    def __str__(self):
        return f'{self.type}:{self.id} - PID {self.pid}'

    def __repr__(self):
        return f'OPTSubprocess({self.type}, {self.id}, {self.logger})'

    def log(self, msg, level):
        """
        Each subprocess will inherit a log function
        """
        if level not in [0, 1, 2]: self.log('Invalid log level', 2)
        else:
            if level == 0:
                self.logger.info(msg)
            elif level == 1:
                self.logger.warning(msg)
            else:
                self.logger.error(msg)

    
