import os
import time
import fileinput
from wrapt_timeout_decorator import *
from subprocess import call, Popen
from shutil import copyfile, rmtree
import pandas as pd
from hyperopt import STATUS_OK
import math

global timelim
timelim = None

def inputHp2nwt(inputHp):
    global cwd
    global namefile
    global initnwt
    global NWTNUM
    with open(os.path.join(cwd, 'nwts', 'nwtnum.txt'), 'r+') as f:
        NWTNUM = int(f.read())
        f.seek(0)
        f.truncate()
        f.write(str(NWTNUM+1))
    with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'w') as file:
        file.write(('{} {} {} {} {} {} {} {} CONTINUE {} {} {} {} {} {} {} {}'.format(inputHp[1], inputHp[2], int(inputHp[3]), inputHp[4], inputHp[0]['linmeth'], inputHp[5],
                   inputHp[6], inputHp[7], inputHp[8], inputHp[9], inputHp[10], inputHp[11],
                   inputHp[12], int(inputHp[13]), inputHp[14], inputHp[15])) + '\n')
    if inputHp[0]['linmeth'] == 1:
        with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
           file.write(('{} {} {} {} {}'.format(int(inputHp[0]['maxitinner']), inputHp[0]['ilumethod'], int(inputHp[0]['levfill']),
                      inputHp[0]['stoptol'], int(inputHp[0]['msdr']))))
    elif inputHp[0]['linmeth'] == 2:
        with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
           file.write(('{} {} {} {} {} {} {} {} {} {}'.format(inputHp[0]['iacl'], inputHp[0]['norder'], int(inputHp[0]['level']),
                      int(inputHp[0]['north']), inputHp[0]['iredsys'], inputHp[0]['rrctols'],
                      inputHp[0]['idroptol'], inputHp[0]['epsrn'], inputHp[0]['hclosexmd'],
                      int(inputHp[0]['mxiterxmd']))))
    # print('[INFO] pulling nwt from', os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))))
    return os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM)))

def trials2csv(trials):
    global cwd
    global namefile
    global initnwt
    df = pd.DataFrame(trials.results).drop('loss', axis=1)
    df.to_csv(os.path.join(cwd, 'nwt_performance.csv'))

@timeout(timelim)
def runModel(pathtonwt, initnwt):
    global cwd
    global namefile
    copyfile(pathtonwt, os.path.join(cwd, initnwt))
    print('[INFO] Starting run.sh out of ', cwd)
    call(['./run.sh'], cwd = cwd, shell = False)
    return True

def getdata():
    global cwd
    global namefile
    global listfile
    global initnwt
    mbline, timeline, iterline = '', '', ''
    with open(os.path.join(cwd, listfile), 'r') as file:
        mbfound = False
        for line in reversed(list(file)):
            if 'Error in Preconditioning' in line:
                return 999999, -1, 999999
            if 'PERCENT DISCREPANCY' in line and mbfound == False:
                mbfound = True
                mbline = line
            if 'Elapsed run time' in line:
                timeline = line
            if 'OUTER ITERATIONS' in line:
                iterline = line
                break
    if timeline == '':
        return 999999, -1, 999999

    for val in mbline.split(' '):
        try:
            mass_balance = float(val)
            break
        except:
            pass
    foundmin, foundsec, foundhour = False, False, False
    min, sec, hrs, days = 0, 0, 0, 0
    for val in reversed(timeline.split(' ')):
        if foundsec == False:
            try:
                sec = float(val)
                foundsec = True
            except:
                pass
        elif foundmin == False:
            try:
                min = float(val)
                foundmin = True
            except:
                pass
        elif foundhour == False:
            try:
                hrs = float(val)
                foundhour = True
            except:
                pass
        else:
            try:
                days = float(val)
                break
            except:
                pass

    sec_elapsed = days * 24 * 3600 + hrs * 3600 + min * 60 + sec
    if sec_elapsed == 0:
        print('[ERROR] bad run')
        return 999999, -1, 999999
    for val in iterline.split(' '):
        try:
            iterations = float(val)
            break
        except:
            pass
    try:
        print('[MASS BALANCE]:', mass_balance)
        print('[SECONDS]:', sec_elapsed)
        print('[TOTAL ITERATIONS]:', iterations)
        return sec_elapsed, iterations, mass_balance
    except:
        print('[ERROR] bad run')
        return 999999, -1, 999999

def processRunCommand():
    global timelim
    cd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cd)  # Get all the files in that directory
    last_line = ""
    print("Files in %r: %s" % (cd, files))
    with open('../run.sh') as f:
        for line in f:
            last_line = line
    try:
        timelim = int(last_line) * 60
        print(f'[INFO] Timeout for model run is set to {timelim / 60} minutes')
    except Exception as e:
        print('[INFO] No timeout set for model run')

def objective(inputHp):
    global cwd
    global namefile
    global listfile
    global initnwt
    global timelim
    cwd = os.path.join(os.sep + os.path.join(*os.getcwd().split(os.sep)[0:-1]), os.path.join('NWT_SUBMIT','PROJECT_FILES'))
    for file in os.listdir(cwd):
        if file.endswith('.nam'):
            namefile = file
        elif file.endswith('.list') or file.endswith('.lst'):
            listfile = file
        elif file.endswith('.nwt'):
            initnwt = file
    foundList, foundNWT = False, False
    with open(os.path.join(cwd, namefile), 'r') as f:
        while(not(foundList and foundNWT)):
            line = f.readline()
            for e in line.split(' '):
                if '.list' in e or '.lst' in e:
                    foundList = True
                    listfile = e.strip()
                elif '.nwt' in e:
                    foundNWT = True
                    initnwt = e.strip()

    pathtonwt = inputHp2nwt(inputHp)
    processRunCommand()
    if not runModel(pathtonwt, initnwt):
        return {'loss': 999999999999,
                'status':  STATUS_OK,
                'eval_time': time.time(),
                'mass_balance': 999999,
                'sec_elapsed': timelim,
                'iterations': -1,
                'NWT Used': pathtonwt}

    sec_elapsed, iterations, mass_balance = getdata()
    if mass_balance == 999999:
        loss = 999999999999
    else:
        loss = math.exp(mass_balance ** 2) * sec_elapsed

    return {'loss': loss,
            'status':  STATUS_OK,
            'eval_time': time.time(),
            'mass_balance': mass_balance,
            'sec_elapsed': sec_elapsed,
            'iterations': iterations,
            'NWT Used': pathtonwt}
