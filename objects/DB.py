from .OPTSubprocess import OPTSubprocess
import asyncio

class DB(OPTSubprocess):
    def __init__(self, id, logger, cwd, ip, port):
        super().__init__('MongoDB', id, logger)
        self.cwd = cwd
        self.ip = ip
        self.port = port
    
    async def init_db(self):
        db = await asyncio.create_subprocess_shell(f'{self.cwd}/mongodb/bin/mongod --dbpath {self.cwd}/mongodb/db --bind_ip {self.ip} ' +
                 f'--port {self.port} --quiet > db_output.txt')
        self.pid = db.pid
        super().log(f'MongoDB started at {self.ip}:{self.port}/db with PID {self.pid}', 0)
