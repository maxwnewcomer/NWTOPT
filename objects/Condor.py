import os
import shutil
import fileinput
import asyncio
from .OPTSubprocess import OPTSubprocess

class Condor(OPTSubprocess):
    """
    Condor Subprocess Object
    """
    def __init__(self, id, logger, cwd, ip, port, poll_interval, workers, timeout):
        """
        Initialization of Condor process
        """
        super().__init__('Condor', id, logger)
        self.ip = ip
        self.port = port
        self.poll_interval = poll_interval
        self.workers = workers
        self.timeout = timeout
        self.cwd = cwd
    
    async def init_condor(self):
        """
        Initialize the Condor Process Object
        """
        self._modify_timeout()
        self._modify_submit()
        await self.submit_condor()

    def _modify_timeout(self):
        """
        Modifies the timeout of the run.sh file based on input
        """
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


    def _modify_submit(self):
        """
        Modifies the submit file used in condor process
        """
        for line in fileinput.input(os.path.dirname(__file__)+'/../nwtopt.sub', inplace = True):
            if line.startswith('arguments'):
                print(f'arguments               = {self.ip}:{self.port}/db {self.poll_interval}', end=os.linesep)
            elif line.startswith('queue'):
                print(f'queue {self.workers}', end=os.linesep)
            else:
                print(line, end='')
        self.log(f'Modified condor submit file to enforce connection to {self.ip}:{self.port}/db every {self.poll_interval} seconds', 0)

    async def submit_condor(self):
        """
        Creates the condor submission subprocesses
        """
        self.log('Preparing to submit nwtopt.sub', 0)
        condor_process = await asyncio.create_subprocess_shell(f'condor_submit nwtopt.sub', cwd=self.cwd)
        self.pid = condor_process.pid
        self.log('Submitted nwtopt.sub using condor_submit', 0)

