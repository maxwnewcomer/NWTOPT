import sys
import shutil
import os
import asyncio
from hyperopt import fmin, tpe
from hyperopt.mongoexp import MongoTrials
from .OPTSubprocess import OPTSubprocess
# import from directory up
sys.path.append('..')
from config.HParams import MF5HParams

class Master(OPTSubprocess):
    """
    Master Subprocess
    """
    def __init__(self, id, logger, cwd, ip, port, key, random, trials):
        """
        Initializes Master subprocess
        """
        super().__init__('master', id, logger)
        self.cwd = cwd
        # Create needed NWTs directory
        if os.path.exists(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts')):
            shutil.rmtree(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))
            os.mkdir(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))
        else:
            os.mkdir(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))

        self.hparams = MF5HParams().hparams
        self.ip = ip
        self.port = port
        self.key = key
        self.random = random
        self.mongoTrials = None
        self.trials = trials

        if os.path.exists(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts', 'nwtnum.txt')):
            os.remove(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts', 'nwtnum.txt'))
            
        with open(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts', 'nwtnum.txt'), 'w+') as f:
                f.write('0')

        self.log(f'Successfully initiated NWTOPT Master Subprocess', 0)
    
    async def init_master(self):
        """
        Initialize master subprocess
        """
        self.connect_to_db()
        self.start_optimization()

    def start_optimization(self):
        """Start hyperopt optimization"""
        from NWT_SUBMIT.NWTOPT_FILES.objective import objective

        if not self.random:
            bestHp = fmin(fn=objective,
                          space=self.hparams,
                          max_queue_len=3,
                          algo=tpe.suggest,
                          max_evals=self.trials,
                          trials=self.mongoTrials)
        else:
            bestRandHp = fmin(fn=objective,
                          space=self.hparams,
                          max_queue_len=3,
                          algo=rand.suggest,
                          max_evals=self.trials,
                          trials=self.mongoTrials)
        

    def connect_to_db(self):
        """Connect to mongo db at objects port and ip"""
        if not self.mongoTrials:
            self.mongoTrials = MongoTrials(f'mongo://{self.ip}:{self.port}/db/jobs', exp_key=self.key)
            self.log(f'Connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 0)
        else:
            self.log(f'Already connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 1)
