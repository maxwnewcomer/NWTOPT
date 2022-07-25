from .OPTSubprocess import OPTSubprocess
import asyncio

class DB(OPTSubprocess):
    """
    Database Subprocess Class
    """
    def __init__(self, id, logger, cwd, ip, port):
        """
        Database Initialization

        Requires:
            ID
            Logger
            Current working directory
            IP
            Port
        """
        super().__init__('MongoDB', id, logger)
        self.cwd = cwd
        self.ip = ip
        self.port = port
    
    async def init_db(self):
        """
        Creates Asyncio subprocess
        """
        db = await asyncio.create_subprocess_shell(f'{self.cwd}/mongodb/bin/mongod --dbpath {self.cwd}/mongodb/db --bind_ip {self.ip} ' +
                 f'--port {self.port} --quiet > db_output.txt')
        self.pid = db.pid
        self.log(f'MongoDB started at {self.ip}:{self.port}/db with PID {self.pid}', 0)
