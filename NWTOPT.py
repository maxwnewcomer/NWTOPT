# FEATURE BRAINSTORM
# file checker and directory modifier
    # check db/ exists
    # run model on local machine to confirm correct model files
    # make sure NWTOPT_FILES has right files (objective.py, optimize_NWT.py, mfnwt)
# num workers (direct edit of nwtopt.sub)
# num trials (arg parsed into optimize_NWT.py)
# rand vs TPE vs aTPE (arg parsed into optimize_NWT.py)
# generate graph (in pull_nwts.py)
# dual run of rand and TPE with combined graph (optimize_NWT.py and pull_nwts.py)
# ip and port specificiation (direct edit of nwtopt.sub, argparse into optimize_NWT.py, pull_nwts.py, and mongod)
# poll-interval specification (direct edit of nwtopt.sub)
# timeout specificiation (still need to write into runModel() of objective.py)
    #   model = subprocess.Popen('./mfnwt ' + namefile)
    #   time_elapsed = 0
    #   while model.returncode = None
    #       time.sleep(1)
    #       time_elapsed += 1
    #       if time_elapsed > specified_cutoff:
    #           print('[ERROR] early termination of model: model took longer than ' + specified_cutoff + ' seconds to termintate')
    #           model.kill()

import subprocess
import time
import os
import socket
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull NWTs from DB')
    parser.add_argument('--ip', type=str, required=False, default=socket.gethostbyname(socket.gethostname()), help='ip address of DB')
    parser.add_argument('--port', type=str, required=False, default='27017', help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--workers', type=int, required=False, default=0)
    args = parser.parse_args()
    cwd = os.getcwd()
    print('[INFO] Working out of ' + cwd)
    print('[INIT] starting database')
    db = subprocess.Popen(cwd + '/mongodb/bin/mongod --dbpath ' + cwd + '/mongodb/db --bind_ip ' + args.ip + ' --port '+ args.port + ' --quiet > db_output.txt', shell = True)
    time.sleep(2)
    print('[CONDOR] sending 100 jobs')
    condor = subprocess.Popen('cd --; cd '+ cwd + '; condor_submit nwtopt.sub', shell = True)
    time.sleep(3)
    print('[INFO] waiting for connections to database')
    time.sleep(30)
    print('[INIT] starting NWTOPT')
    optimizer = subprocess.Popen('cd --; cd '+ cwd + '/NWT_SUBMIT/NWTOPT_FILES; python optimize_NWT.py --ip ' + args.ip +
        ' --port ' + args.port + ' --key ' + args.key + ' --random False --trials 3000', shell = True)
    while True:
        time.sleep(60)
        print('[BACKUP] backing up already tested NWTs')
        nwts = subprocess.Popen('python ' + cwd + '/pull_nwts.py --ip ' + args.ip + ' --port ' + args.port + ' --key ' + args.key, shell = True)
