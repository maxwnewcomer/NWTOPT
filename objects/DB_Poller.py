import asyncio
import pandas as pd
import time
import sys
import os
from .OPTSubprocess import OPTSubprocess
from hyperopt.mongoexp import MongoTrials
from hyperopt.exceptions import AllTrialsFailed

sys.path.append('..')
from config.HParams import MF5HParams

class DB_Poller(OPTSubprocess):
    def __init__(self, id, logger, cwd, ip, port, key, poll_interval):
        super().__init__('DB_Poller', id, logger)
        self.ip = ip
        self.port = port
        self.cwd = cwd
        self.poll_interval = poll_interval
        self.HParams = MF5HParams()
        self.key = key
        try:
            os.mkdir(os.path.join(self.cwd, f'{self.key}_{self.HParams.filetype}s'))
            self.log(f'Created {self.HParams.filetype} log directory', 0)
        except FileExistsError:
            pass

    async def init_poller(self):
        while True:
            self.pullHParams()
            await asyncio.sleep(self.poll_interval)

    def pullHParams(self):
        trials = MongoTrials(f'mongo://{self.ip}:{self.port}/db/jobs', exp_key=self.key)
        # get best trial from run
        try:
            self.HParams.HParam2File(trials.best_trial.get('misc').get('vals').to_dict(), 
                                     os.path.join(self.cwd, f'{self.key}_{self.HParams.filetype}s', f'best.{self.HParams.filetype}'))
        except AllTrialsFailed:
            pass
        # get the rest of the trials
        for i in range(len(trials.trials)):
            self.HParams.HParam2File(trials.trials[i].get('misc').get('vals').to_dict(), 
                                     os.path.join(self.cwd, f'{self.key}_{self.HParams.filetype}s', f'{self.HParams.filetype}_{i}.{self.HParams.filetype}'))

        # get results of each trial and compile them into a list
        results = []
        minLoss = 9999999
        for i in range(len(trials.trials)):
            trial = trials.trials[i].get('result').to_dict()
            try:
                if trial['loss'] < minLoss:
                    minLoss = trial['loss']
                results.append([i,
                                trial['eval_time'],
                                trial['finish_time'],
                                trial['loss'],
                                trial['mass_balance'],
                                trial['sec_elapsed'],
                                trial['iterations'],
                                minLoss])
            except Exception:
                pass
        # convert list to pd.DataFrame object and then convert that DataFrame
        # to {HParams.filetype}_performance.csv
        df = pd.DataFrame(results, columns=['NWT Number',
                                            'Start Time',
                                            'Finish Time',
                                            'Loss',
                                            'Mass Balance',
                                            'Seconds Elapased',
                                            '# of Iterations',
                                            'Min Loss'])
        df.to_csv(os.path.join(self.cwd, f'{self.key}_{self.HParams.filetype}s', f'{self.HParams.filetype}_performance.csv'), index = False)
