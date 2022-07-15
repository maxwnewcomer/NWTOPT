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


import time
import sys
import os
import socket
import argparse
import logging
import asyncio
from collections import defaultdict
from objects.OPTSubprocess import OPTSubprocess
from objects.Master import Master
from objects.DB import DB
from objects.Condor import Condor
from objects.DB_Poller import DB_Poller

class NWTOPT():
    def __init__(self, args):
        self.ip = args.ip
        self.port = args.port
        self.key = args.key
        self.workers = args.workers
        self.random = args.random
        self.trials = args.trials
        self.poll_interval = args.poll_interval
        self.enable_condor = args.enable_condor
        self.timeout = args.timeout
        self.cwd = os.getcwd()
        self.processes = defaultdict(OPTSubprocess)
        self.logger = self.init_logger()
        
        self.event_loop = asyncio.new_event_loop()
        
        self.log(f'Working out of {self.cwd}', 0)

    def init_logger(self):
        logger = logging.getLogger('NWTOPT')
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(stream=sys.stdout)

        if logger.hasHandlers():
            for hdlr in logger.handlers:
                logger.removeHandler(hdlr)

        file_handler = logging.FileHandler('./NWTOPT.log', mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s:[%(levelname)7s]:%(threadName)12s - %(message)s')
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
    async def wait(self, time):
        await asyncio.sleep(time)

    def start_loop(self):
        self.event_loop.create_task(self.processes['DB'].init_db())
        self.event_loop.create_task(self.processes['DB_Poller'].init_poller())
        if self.enable_condor:
            self.event_loop.create_task(self.processes['Condor'].init_condor())
        self.event_loop.create_task(self.processes['Master'].init_master())
        self.event_loop.run_forever()
        
    def init_master(self):
        master_process = Master(3, self.logger, self.cwd, self.ip, self.port, self.key, self.random, self.trials)
        self.processes['Master'] = master_process

    def init_db(self):
        db_process = DB(1, self.logger, self.cwd, self.ip, self.port)
        self.processes['DB'] = db_process
    
    def init_condor(self):
        condor_process = Condor(2, self.logger, self.cwd, self.ip, self.port, self.poll_interval, self.workers, self.timeout)
        self.processes['Condor'] = condor_process

    def init_db_poller(self):
        dbPoll_process = DB_Poller(4, self.logger, self.cwd, self.ip, self.port, self.key, 60)
        self.processes['DB_Poller'] = dbPoll_process
    
if __name__ == '__main__':
    # REMEBER TO REREQUIRE CERTAIN ARGS, SIMPLY FALSE FOR TESTING
    parser = argparse.ArgumentParser(description='NWTOPT - Hyperparameter Optimization for MODFLOW-NWT')
    parser.add_argument('--ip', type=str, required=False, default=socket.gethostbyname(socket.gethostname()), help='ip address of DB')
    parser.add_argument('--port', type=int, required=False, default=27017, help='port of DB')
    parser.add_argument('--key', type=str, required=True, default = '', help='key of job you want to pull')
    parser.add_argument('--workers', type=int, required=False, default=1, help='the number of Condor workers to deploy')
    parser.add_argument('--random', type=bool, required=False, default=False, help='set to True to switch from TPE to Random Search')
    parser.add_argument('--trials', type=int, required=False, default = 1, help='the number of optimization trials')
    parser.add_argument('--poll_interval', type=int, required=False, default=240, help='the frequency that a Condor worker pings the DB in seconds')
    parser.add_argument('--enable_condor', type=bool, required=False, default=False, help='set to True to send out jobs through Condor')
    parser.add_argument('--timeout', type=float, required=False, default=22, help='model run time limit - leave empty for no time limit')
    # init vars
    args = parser.parse_args()
    assert args.trials > 0, 'You cannot run NWTOPT with less than 1 trial' 
    assert args.poll_interval > 0, 'You cannot run NWTOPT with a poll interval less than 1 second'
    if args.enable_condor:
        assert args.workers > 0, 'Please specify your desired number of workers'
    
    OPTHandler = NWTOPT(args)
    
    OPTHandler.init_db()
    OPTHandler.init_master()
    if args.enable_condor:
        OPTHandler.init_condor()
    OPTHandler.init_db_poller()
    OPTHandler.start_loop() 

   #  killProcesses()
