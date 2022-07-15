import sys
import shutil
import os
import asyncio
from hyperopt import fmin, tpe
from hyperopt.mongoexp import MongoTrials
from .OPTSubprocess import OPTSubprocess
# import from directory up
sys.path.append('..')
from NWT_SUBMIT.NWTOPT_FILES.objective import objective
from config.HParams import MF5HParams

class Master(OPTSubprocess):
    def __init__(self, id, logger, cwd, ip, port, key, random, trials):
        super().__init__('master', id, logger)
        self.cwd = cwd
        try:
            os.mkdir(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))
        except FileExistsError:
            shutil.rmtree(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))
            os.mkdir(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts'))

        self.hparams = MF5HParams().hparams
        self.ip = ip
        self.port = port
        self.key = key
        self.random = random
        self.mongoTrials = None
        self.trials = trials

        try:
            os.remove(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts', 'nwtnum.txt'))
        except Exception:
            pass
        with open(os.path.join(self.cwd, 'NWT_SUBMIT', 'PROJECT_FILES', 'nwts', 'nwtnum.txt'), 'w+') as f:
                f.write('0')
        self.log(f'Successfully initiated NWTOPT Master Subprocess', 0)
    
    async def init_master(self):
        self.connect_to_db()
        self.start_optimization()

    def start_optimization(self):
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
        if not self.mongoTrials:
            self.mongoTrials = MongoTrials(f'mongo://{self.ip}:{self.port}/db/jobs', exp_key=self.key)
            self.log(f'Connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 0)
            ## ADD a check that connection was successful
        else:
            self.log(f'Already connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 1)
