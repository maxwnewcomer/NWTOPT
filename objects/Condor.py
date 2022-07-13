import os
import fileinput
import asyncio
from .OPTSubprocess import OPTSubprocess

class Condor(OPTSubprocess):
    def __init__(self, id, logger, ip, port, poll_interval, workers, timeout):
        super().__init__('Condor', id, logger)
        self.ip = ip
        self.port = port
        self.poll_interval = poll_interval
        self.workers = workers
        self.timeout = timeout
    
    async def init_condor(self):
        self.modify_timeout()
        self.modify_submit()
        # await self.submit_condor()

        
    def modify_timeout(self):
        printNext = False
        # print() statements are part of the fileinput input method
        for line in fileinput.input(os.path.dirname(__file__)+'/../run.sh', inplace = True):
            if printNext:
                if self.timeout is not None:
                    print(self.timeout)
                else:
                    print()
                printNext = False
            elif line.startswith('# Model timeout'):
                print(line, end='')
                printNext = True
            else:
                print(line, end='')
        self.log(f'Modified the run.sh file to enforce a worker timeout of {self.timeout} minutes', 0)


    def modify_submit(self):
        for line in fileinput.input(os.path.dirname(__file__)+'/../nwtopt.sub', inplace = True):
            if line.startswith('arguments'):
                print(f'arguments               = {self.ip}:{self.port}/db {self.poll_interval}', end=os.linesep)
            elif line.startswith('queue'):
                print(f'queue {self.workers}', end=os.linesep)
            else:
                print(line, end='')
        self.log(f'Modified condor submit file to enforce connection to {self.ip}:{self.port}/db every {self.poll_interval} seconds', 0)

    async def submit_condor(self):
        self.log('Preparing to submit nwtopt.sub', 0)
        condor_process = await asyncio.create_subprocess_shell(f'condor_submit {os.path.dirname(__file__)}/../nwtopt.sub')
        self.pid = condor_process.pid
        self.log('Submitted nwtopt.sub using condor_submit', 0)
