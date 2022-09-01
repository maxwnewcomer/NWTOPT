"""
objective function utilized by hyperopt-monogdb-worker

Receives hyperparameters, reformats them as a nwt,
runs the model, pulls trial information from .list
file, computes loss, and returns that loss

Uses code from flopy package 
https://github.com/modflowpy/flopy/blob/develop/flopy/utils/mflistfile.py
"""
# Disabling pylint snake_case warnings, import error warnings, and
# redefining out of scope warnings, too many local variables
# too many branches, too many statements
#
# pylint: disable = E0401, C0103, W0621, R0914, R0912, R0915, R0915

import os
import math
from datetime import datetime
from subprocess import run, TimeoutExpired
from shutil import copyfile
import pandas as pd
import numpy as np
from hyperopt import STATUS_OK
from numpy import Inf as INF
from .utils.mflistfile import ListBudget
def inputHp2nwt(inputHp, cwd):
    """
    Takes Hyperopt Hyperparameter format and reformats it as a .nwt file. This .nwt file
    overwrites the local .nwt file and will thus be used by MODFLOW

    inputHp - hyperopt hyperparams
    cwd - working directory of project

    creates *.nwt file

    returns path to *.nwt file
    """
    # keep track of which NWTNUM the machine is on
    with open(os.path.join(cwd, 'nwts', 'nwtnum.txt'), 'r+') as f:
        NWTNUM = int(f.read())
        f.seek(0)
        f.truncate()
        f.write(str(NWTNUM+1))
    # Write the standard first line of the .nwt file
    with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'w') as file:
        file.write(('{} {} {} {} {} {} {} {} CONTINUE {} {} {} {} {} {} {} {}'.format(inputHp[1],
            inputHp[2],
            int(inputHp[3]),
            inputHp[4],
            inputHp[0]['linmeth'],
            inputHp[5],
            inputHp[6],
            inputHp[7],
            inputHp[8],
            inputHp[9],
            inputHp[10],
            inputHp[11],
            inputHp[12],
            int(inputHp[13]),
            inputHp[14],
            inputHp[15])) + '\n')
    # depending on the linmeth setting, change the formatting of the rest of the file
    if inputHp[0]['linmeth'] == 1:
        with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
            file.write(('{} {} {} {} {}'.format(int(inputHp[0]['maxitinner']),
                                                inputHp[0]['ilumethod'],
                                                int(inputHp[0]['levfill']),
                                                inputHp[0]['stoptol'],
                                                int(inputHp[0]['msdr']))))
    elif inputHp[0]['linmeth'] == 2:
        with open(os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
            file.write(('{} {} {} {} {} {} {} {} {} {}'.format(inputHp[0]['iacl'],
                                                            inputHp[0]['norder'],
                                                            int(inputHp[0]['level']),
                                                            int(inputHp[0]['north']),
                                                            inputHp[0]['iredsys'],
                                                            inputHp[0]['rrctols'],
                                                            inputHp[0]['idroptol'],
                                                            inputHp[0]['epsrn'],
                                                            inputHp[0]['hclosexmd'],
                                                            int(inputHp[0]['mxiterxmd']))))

    return os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(NWTNUM)))

def trials2csv(trials, d):
    """
    Converts Trials Dataframe Object to csv

    trials - MongoTrials object
    d - directory to save to

    outputs nwt_performance.csv
    """
    df = pd.DataFrame(trials.results).drop('loss', axis=1)
    df.to_csv(os.path.join(d, 'nwt_performance.csv'))

def getModelRunCommands(cwd):
    """
    Pull time limit, run command, and run type from run.sh file

    cwd - directory containing run.sh

    returns time limit, run command, run type
    """

    last_line = ""
    run_command = ""
    run_type = ""
    use_next = False
    rcommand = False
    rtype = False
    # open run.sh and look for run command and last line
    with open(os.path.join(cwd, 'run.sh')) as f:
        for line in f:
            if use_next:
                if rcommand:
                    run_command = line
                if rtype:
                    run_type = line
                use_next = False
            elif line.startswith('# Run Command:'):
                use_next = True
                rcommand = True
            elif line.startswith('# Model run_type'):
                use_next = True
                rtype = True
            last_line = line
    # last line should be timout, if empty or non-convertable timelim none
    try:
        timelim = float(last_line) * 60
        print(f'[INFO] Timeout for model run is set to {timelim / 60} minutes')
    except ValueError:
        timelim = None
        print('[INFO] No timeout set for model run')
    return timelim, run_command, run_type

def runModel(pathtonwt, initnwt, cwd, timelim, run_command):
    """
    Run the MODFLOW Model/Run Command using subprocess.run

    pathtonwt - path to generated nwt
    initnwt - path to initial nwt
    cwd - working directory of the project
    timelim - time limit
    run_command - run command located in run.sh

    returns True if successful terminimation of trial,
    else returns false due to TimeoutExpired error

    * NOTE * "successful termination" doesn't necessarily mean the model
            didn't error out, only that the process has finished.
    """
    # replace initial nwt with newly generated nwt
    copyfile(pathtonwt, os.path.join(cwd, initnwt))
    print(f'[INFO] Using run command: {run_command.strip()}')
    print(f'[INFO] Starting run out of {cwd}')

    # try running, and if timeout catch
    try:
        modflowProcess = run(run_command.strip().split(' '),
                            cwd = cwd,
                            capture_output = True,
                            timeout = timelim,
                            check = True)
        print(str(modflowProcess.stdout, 'utf-8'), '\n', str(modflowProcess.stderr, 'utf-8'))
        print("[INFO] Successful termination of trial")
        return True
    except TimeoutExpired:
        print('[WARNING] Time Limit reached, terminating run')
        return False

def getRunResults(cwd, listfile):
    """
    Pull Run Results from MODFLOW *.list file

    cwd - project running directory
    listfile - path to *.list file

    if successful:
        returns sec_elapsed, iterations, mass_balance
    else:
        returns INF, -1, INF
    """
    # find all the necessary lines in the .list file
    mbline, timeline, iterline = '', '', ''
    with open(os.path.join(cwd, listfile), 'r') as file:
        mbfound = False
        for line in reversed(list(file)):
            if 'Error in Preconditioning' in line:
                return INF, -1, INF
            if 'PERCENT DISCREPANCY' in line and mbfound is False:
                mbfound = True
                mbline = line
            if 'Elapsed run time' in line:
                timeline = line
            if 'OUTER ITERATIONS' in line:
                iterline = line
                break

    # check for run failure
    if timeline == '':
        return INF, -1, INF
    mass_balance = None
    # pull mass balance
    for val in mbline.split(' '):
        try:
            mass_balance = float(val)
            break
        except ValueError:
            pass
    if not mass_balance:
        print('[ERROR] bad run')
        return INF, -1, INF

    # prepare to pull run time information
    foundmin, foundsec, foundhour = False, False, False
    minutes, sec, hrs, days = 0, 0, 0, 0

    # MODFLOW doesn't report timing consitantly, so we have
    # to use some weird looping and calculations to
    # pull the correct time information
    for val in reversed(timeline.split(' ')):
        if foundsec is False:
            try:
                sec = float(val)
                foundsec = True
            except ValueError:
                pass
        elif foundmin is False:
            try:
                minutes = float(val)
                foundmin = True
            except ValueError:
                pass
        elif foundhour is False:
            try:
                hrs = float(val)
                foundhour = True
            except ValueError:
                pass
        else:
            try:
                days = float(val)
                break
            except ValueError:
                pass
    # calculate how long everything took
    sec_elapsed = days * 24 * 3600 + hrs * 3600 + minutes * 60 + sec

    # check for good values
    if sec_elapsed == 0:
        print('[ERROR] bad run')
        return INF, -1, INF
    iterations = None
    for val in iterline.split(' '):
        try:
            iterations = float(val)
            break
        except ValueError:
            pass
    if not iterations:
        print('[ERROR] bad run')
        return INF, -1, INF

    print('[MASS BALANCE]:', mass_balance)
    print('[SECONDS]:', sec_elapsed)
    print('[TOTAL ITERATIONS]:', iterations)
    return sec_elapsed, iterations, mass_balance

def objective(inputHp):
    """
    Objective funciton that is called by hyperopt-mongo-worker

    inputHp - hyperparams from Hyperopt

    returns dictionary of trial run metrics:
        {'loss': loss,
        'status':  STATUS_OK,
        'eval_time': eval_time,
        'mass_balance': mass_balance,
        'sec_elapsed': sec_elapsed,
        'iterations': iterations,
        'NWT Used': pathtonwt,
        'finish_time': finish_time}
    """
    # get eval time, set up main variables to run
    eval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cwd = os.path.join(os.path.dirname(os.getcwd()), 'nwtenv','bin','NWT_SUBMIT','PROJECT_FILES')
    # get necessary file names and paths
    for file in os.listdir(cwd):
        if file.endswith('.nam'):
            namefile = file
        elif file.endswith('.list') or file.endswith('.lst'):
            listfile = file
        elif file.endswith('.nwt'):
            initnwt = file
    foundList, foundNWT = False, False
    # pull correct list and nwt names from .name file
    with open(os.path.join(cwd, namefile), 'r') as f:
        while not(foundList and foundNWT):
            line = f.readline()
            for e in line.split(' '):
                if '.list' in e or '.lst' in e:
                    foundList = True
                    listfile = e.strip()
                elif '.nwt' in e:
                    foundNWT = True
                    initnwt = e.strip()
    # convert hyperparams to nwt and get path
    pathtonwt = inputHp2nwt(inputHp, cwd)
    timelim, run_command, run_type = getModelRunCommands(cwd)
    # run the model and check for errors
    if not runModel(pathtonwt, initnwt, cwd, timelim, run_command):
        finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {'loss': INF,
                'status':  STATUS_OK,
                'eval_time': eval_time,
                'mass_balance': INF,
                'sec_elapsed': timelim,
                'iterations': -1,
                'NWT Used': pathtonwt,
                'finish_time': finish_time}
    # if no errors get run results based off of run_type
    if run_type == 'nwt-ss':
        sec_elapsed, iterations, mass_balance = getRunResults(cwd, listfile)
        if mass_balance == INF:
            loss = INF
        else:
            loss = math.exp(mass_balance ** 2) * sec_elapsed
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # do final reporting
        return {'loss': loss,
                'status':  STATUS_OK,
                'eval_time': eval_time,
                'mass_balance': mass_balance,
                'sec_elapsed': sec_elapsed,
                'iterations': iterations,
                'NWT Used': pathtonwt,
                'finish_time': finish_time}
    elif run_type == 'nwt-t':
        sec_elapsed, iterations, mass_balance = getDataTransient(listfile)
        if mass_balance == INF:
            loss = INF
        else:
            loss = math.exp(mass_balance ** 2) * sec_elapsed
            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {'loss': loss,
                'status':  STATUS_OK,
                'eval_time': eval_time,
                'mass_balance': mass_balance,
                'sec_elapsed': sec_elapsed,
                'iterations': iterations,
                'NWT Used': pathtonwt,
                'finish_time': finish_time}
def getDataTransient(listfile):
    '''
    Version of getdata() that uses flopy to get the mass balance
    errors for the whole transient run and returns the mass loss as
    sum(abs(incremental_percent_disrepancy)*length_stress_period)/sum(length_stress_period).

    flopy doesn't grab iterations - just set to -1 for right now.

    '''
    
    try:
        mf_list = ListBudget.MfListBudget(listfile)
        incr_df, cum_df = mf_list.get_dataframes(start_datetime='1984-10-01')
        sec_elapsed = mf_list.get_model_runtime(units='seconds')

        # get absolute value of discrepancy
        incr_df['abs_pct_diff'] = np.abs(incr_df['PERCENT_DISCREPANCY'])
    
        # put in time in days for the time steps
        incr_df['dt'] = incr_df.index.to_series().diff().dt.total_seconds().div(3600*24, fill_value=0)

        # area under the curve = abs_pct_diff * stress_period_length
        incr_df['area'] = incr_df['abs_pct_diff'] * incr_df['dt']

        # normalize by the total days as mass balance error
        mass_balance = np.sum(incr_df['area'])/np.sum(incr_df['dt'])

        # set iterations
        iterations = -1

        print('[MASS BALANCE]:', mass_balance)
        print('[SECONDS]:', sec_elapsed)
        print('[TOTAL ITERATIONS]:', iterations)
        return sec_elapsed, iterations, mass_balance
    except:
        print('[ERROR] bad run')
        return INF, -1, INF
