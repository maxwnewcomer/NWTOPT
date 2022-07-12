"""
Master Script used to Run All necessary process

[usage]: python3 NWTOPT.py --ip {mongodb ip}
    --port {mongodb port}
    --key {mongodb job key}
    --random {set True if random hyperparameter generation is desired}
    --trials {number of trials to run}
    --workers {number of HTCondor workers}
    --poll_interval {poll interval of HTCondor workers}
    --enable_condor {True to enable condor job submission}
    --timeout {desired timeout}

* NOTE * not fully completed and not to be used
"""
# Disabling pylint snake_case warnings, import error warnings, and
# redefining out of scope warnings, too many local variables
# too many branches, too many statements
#
# pylint: disable = E0401, C0103, W0621, R0914, R0912, R0915, R0915


import subprocess
import time
import sys
import os
import socket
import argparse
import fileinput
import signal
import logging
import asyncio
from collections import defaultdict
from objects.OPTSubprocess import OPTSubprocess
from objects.Master import Master
from objects.DB import DB

class NWTOPT():
    def __init__(self, args):
        self.ip = args.ip
        self.port = args.port
        self.key = args.key
        self.workers = args.workers
        self.random = args.random
        self.trials = args.trials
        self.poll_interval = args.poll_interval
        self.eneable_condor = args.enable_condor
        self.timeout = args.timeout
        self.cwd = os.getcwd()
        self.processes = defaultdict(OPTSubprocess)
        self.logger = self.init_logger()
        
        self.log(f'Working out of {self.cwd}', 0)

    def init_logger(self):
        logger = logging.getLogger('NWTOPT')
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(stream=sys.stdout)

        if logger.hasHandlers():
            for hdlr in logger.handlers:
                logger.removeHandler(hdlr)

        file_handler = logging.FileHandler('./NWTOPT.log', mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s:[%(levelname)7s]:%(name)12s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def log(self, msg, level):
        if level not in [0, 1, 2]: self.log('Invalid log level', 2)
        else:
            if level == 0:
                self.logger.info(msg)
            elif level == 1:
                self.logger.warning(msg)
            else:
                self.logger.error(msg)

    def init_db(self):
        db_process = DB(1, self.logger, self.cwd, self.ip, self.port)
        dbLoop = asyncio.new_event_loop()
        dbLoop.create_task(db_process.init_db())
        dbLoop.run_forever()
        self.processes['DB'] = db_process
    
    def modifySubmitFile(self, workers, ip, port, pollInterval):
        for line in fileinput.input('nwtopt.sub', inplace = True):
            if line.startswith('arguments'):
                print(f'arguments               = {ip}:{port}/db {pollInterval}', end=os.linesep)
            elif line.startswith('queue'):
                print(f'queue {workers}', end=os.linesep)
            else:
                print(line, end='')

    def signal_handler(self, signum, frame):
        """
        Kill all processes on ^C
        """
        print(f'{os.linesep} [INFO] terminating all processes')
        killProcesses()

    ## Modify run.sh to have user inputed timeout
    def modifyTimeout(self):
        printNext = False
        for line in fileinput.input('run.sh', inplace = True):
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

    def killProcesses(self):
        pass

if __name__ == '__main__':
    # REMEBER TO REREQUIRE CERTAIN ARGS, SIMPLY FALSE FOR TESTING
    parser = argparse.ArgumentParser(description='NWTOPT - Hyperparameter Optimization for MODFLOW-NWT')
    parser.add_argument('--ip', type=str, required=False, default=socket.gethostbyname(socket.gethostname()), help='ip address of DB')
    parser.add_argument('--port', type=int, required=False, default=27017, help='port of DB')
    parser.add_argument('--key', type=str, required=False, default = '', help='key of job you want to pull')
    parser.add_argument('--workers', type=int, required=False, default=1, help='the number of Condor workers to deploy')
    parser.add_argument('--random', type=bool, required=False, default=False, help='set to True to switch from TPE to Random Search')
    parser.add_argument('--trials', type=int, required=False, default = 1, help='the number of optimization trials')
    parser.add_argument('--poll_interval', type=int, required=False, default=240, help='the frequency that a Condor worker pings the DB in seconds')
    parser.add_argument('--enable_condor', type=bool, required=False, default=True, help='set to True to send out jobs through Condor')
    parser.add_argument('--timeout', type=float, required=False, default=None, help='model run time limit - leave empty for no time limit')
    # init vars
    args = parser.parse_args()
    assert args.trials > 0, 'You cannot run NWTOPT with less than 1 trial' 
    assert args.poll_interval > 0, 'You cannot run NWTOPT with a poll interval less than 1 second'
    if args.enable_condor:
        assert args.workers > 0, 'Please specify your desired number of workers'
    
    OPTHandler = NWTOPT(args)
    cluster = None
    FNULL = open(os.devnull, 'w')

    
    OPTHandler.modifyTimeout()
    OPTHandler.init_db()
   # print(f'[INIT] starting database at {args.ip}:{args.port}/db')
   # db = subprocess.Popen(f'{cwd}/mongodb/bin/mongod --dbpath {cwd}/mongodb/db --bind_ip {args.ip} ' +
   #                       f'--port {args.port} --quiet > db_output.txt', shell=True, preexec_fn=os.setsid)
   # if args.enable_condor:
   #     time.sleep(3)
   #     modifySubmitFile(args.workers, args.ip, args.port, args.poll_interval)
   #     print(f'[CONDOR] starting {args.workers} worker(s)')
   #     condor = subprocess.Popen('condor_submit nwtopt.sub', shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE) cluster = condor.communicate()[0].decode('utf-8').split(os.linesep)[-2].split(' ')[-1][:-1] print(f'[CONDOR] workers started on cluster {cluster}') # print(f'[INFO] you can find your nwts and their performance in nwt_performance.csv at {cwd}/{args.key}_nwts/') time.sleep(3) print('[INIT] starting the optimization') optimizer = subprocess.Popen(f'cd {cwd}/NWT_SUBMIT/NWTOPT_FILES; python optimize_NWT.py --ip {args.ip} --port {args.port} ' + f'--key {args.key} --random {args.random} --trials {args.trials}', shell=True, preexec_fn=os.setsid) time.sleep(3) nwts = subprocess.Popen(f'python {cwd}/pull_nwts.py --ip {args.ip} --port {args.port} --key {args.key} --loop True', shell=True, preexec_fn=os.setsid, stdout=FNULL, stderr=FNULL) # while optimizer.poll() is None: time.sleep(5) # killProcesses()
