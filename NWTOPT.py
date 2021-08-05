import subprocess
import time
import os
import socket
import argparse
import fileinput
import signal

## Modify nwtopt.sub to have user inputed ip:port and poll interval
def modifySubmitFile(workers, ip, port, pollInterval):
    for line in fileinput.input('nwtopt.sub', inplace = True):
        if line.startswith('arguments'):
            print(f'arguments               = {ip}:{port}/db {pollInterval}', end=os.linesep)
        elif line.startswith('queue'):
            print(f'queue {workers}', end=os.linesep)
        else:
            print(line, end='')

## Kill all processes on ^C
def signal_handler(signum, frame):
    print(f'{os.linesep} [INFO] terminating all processes')
    killProcesses()

## Modify run.sh to have user inputed timeout
def modifyTimeout(timeout):
    printNext = False
    for line in fileinput.input('run.sh', inplace = True):
        if printNext:
            if timeout is not None:
                print(timeout)
            else:
                print()
            printNext = False
        elif line.startswith('# Model timeout'):
            print(line, end='')
            printNext = True
        else:
            print(line, end='')

## End all processes that are ran by NWTOPT
def killProcesses():
    os.killpg(db.pid, signal.SIGKILL)
    try:
        os.killpg(optimizer.pid, signal.SIGKILL)
    except Exception as e:
        pass
    os.killpg(nwts.pid, signal.SIGKILL)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser(description='NWTOPT - Hyperparameter Optimization for MODFLOW-NWT')
    parser.add_argument('--ip', type=str, required=False, default=socket.gethostbyname(socket.gethostname()), help='ip address of DB')
    parser.add_argument('--port', type=int, required=False, default=27017, help='port of DB')
    parser.add_argument('--key', type=str, required=True, help='key of job you want to pull')
    parser.add_argument('--workers', type=int, required=False, default=0, help='the number of Condor workers to deploy')
    parser.add_argument('--random', type=bool, required=False, default=False, help='set to True to switch from TPE to Random Search')
    parser.add_argument('--trials', type=int, required=True, help='the number of optimization trials')
    parser.add_argument('--poll_interval', type=int, required=False, default=240, help='the frequency that a Condor worker pings the DB in seconds')
    parser.add_argument('--enable_condor', type=bool, required=False, default=True, help='set to True to send out jobs through Condor')
    parser.add_argument('--timeout', type=float, required=False, default=None, help='model run time limit - leave empty for no time limit')
    # init vars
    args = parser.parse_args()
    cluster = None
    FNULL = open(os.devnull, 'w')

    # var assertion
    assert args.trials > 0, 'You cannot run NWTOPT with less than 1 trial'
    assert args.poll_interval > 0, 'You cannot run NWTOPT with a poll interval less than 1 second'
    if args.enable_condor:
        assert args.workers > 0, 'Please specify your desired number of workers'

    modifyTimeout(args.timeout)

    cwd = os.getcwd()
    print(f'[INFO] working out of {cwd}')

    print(f'[INIT] starting database at {args.ip}:{args.port}/db')
    db = subprocess.Popen(f'{cwd}/mongodb/bin/mongod --dbpath {cwd}/mongodb/db --bind_ip {args.ip} ' +
                          f'--port {args.port} --quiet > db_output.txt', shell=True, preexec_fn=os.setsid)
    if args.enable_condor:
        time.sleep(3)
        modifySubmitFile(args.workers, args.ip, args.port, args.poll_interval)
        print(f'[CONDOR] starting {args.workers} worker(s)')
        condor = subprocess.Popen('condor_submit nwtopt.sub', shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE)
        cluster = condor.communicate()[0].decode('utf-8').split(os.linesep)[-2].split(' ')[-1][:-1]
        print(f'[CONDOR] workers started on cluster {cluster}')

    print(f'[INFO] you can find your nwts and their performance in nwt_performance.csv at {cwd}/{args.key}_nwts/')
    time.sleep(3)
    print('[INIT] starting the optimization')
    optimizer = subprocess.Popen(f'cd {cwd}/NWT_SUBMIT/NWTOPT_FILES; python optimize_NWT.py --ip {args.ip} --port {args.port} ' +
                                 f'--key {args.key} --random {args.random} --trials {args.trials}', shell=True, preexec_fn=os.setsid)
    time.sleep(3)
    nwts = subprocess.Popen(f'python {cwd}/pull_nwts.py --ip {args.ip} --port {args.port} --key {args.key} --loop True',
                            shell=True, preexec_fn=os.setsid, stdout=FNULL, stderr=FNULL)

    while optimizer.poll() is None:
        time.sleep(5)

    killProcesses()
