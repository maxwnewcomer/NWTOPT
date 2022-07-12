import sys
from .OPTSubprocess import OPTSubprocess
# import from directory up
sys.path.append('..')
from config.HParams import hparams

class Master(OPTSubprocess):
    def __init__(self, ip, port, key, random, trials, id, logger):
        super().__init__('master', id, logger)
        self.cwd = os.getcwd()
        try:
            os.mkdir(os.path.join(os.path.join(self.cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
        except FileExistsError:
            rmtree(os.path.join(os.path.join(self.cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
            os.mkdir(os.path.join(os.path.join(self.cwd[0:-12], 'PROJECT_FILES'), 'nwts'))

        self.hparams = hparams
        self.ip = ip
        self.port = port
        self.key = key
        self.random = random
        self.trials = None

        try:
            os.remove(os.path.join(self.cwd, 'nwts/nwtnum.txt'))
        except Exception:
            pass
        with open(os.path.join(self.cwd, 'nwts/nwtnum.txt'), 'w+') as f:
                f.write('0')
        self.log(f'Successfully initiated NWTOPT Master Subprocess', 0)

    def connect_to_db(self):
        if not self.trials:
            self.trials = MongoTrials('mongo://'+ self.ip + ':'+ self.port + '/db/jobs', exp_key=self.key)
            self.log(f'Connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 0)
            ## ADD a check that connection was successful
        else:
            self.log(f'Already connected to mongo://{self.ip}:{self.port}/db/jobs with job key - {self.key}', 1)
