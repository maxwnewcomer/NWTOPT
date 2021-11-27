"""
Script used to pull nwt values from MongoDB

Requires MongoDB to be running

[usage]: python3 pull_nwts.py --ip {mongodb ip} --port {mongodb port} --key {mongodb job key}
    --loop {set True if persistant pulling is desired} --verbose {True if verbosity desired}
"""
# Disabling pylint snake_case warnings, import error warnings, and
# redefining out of scope warnings, too many local variables
# too many branches, too many statements
#
# pylint: disable = E0401, C0103, W0621, R0914, R0912, R0915, R0915

import os
import time
import argparse
import pandas as pd
from hyperopt.mongoexp import MongoTrials
from hyperopt.exceptions import AllTrialsFailed

def inputHp2nwt(inputHp, NWTNUM, args):
    """
    Converts MongoTrials dictionary hyperparameters to *.nwt file

    inputHp - MongoTrials dictionary formatted hyperparameters
    NWTNUM - NWT Number
    args - Run arguments

    returns path to new *.nwt file
    """
    cwd = os.getcwd()
    # write hyperparameters to file
    with open(os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'w') as file:
        file.write(('{} {} {} {} {} {} {} {} CONTINUE {} {} {} {} {} {} {} {}'.format(
            inputHp['headtol'][0],
            inputHp['fluxtol'][0],
            int(inputHp['maxiterout'][0]),
            inputHp['thickfact'][0],
            inputHp['linmeth'][0] + 1,
            inputHp['iprnwt'][0],
            inputHp['ibotav'][0],
            'SPECIFIED',
            inputHp['dbdtheta'][0],
            inputHp['dbdkappa'][0],
            inputHp['dbdgamma'][0],
            inputHp['momfact'][0],
            inputHp['backflag'][0],
            int(inputHp['maxbackiter'][0]),
            inputHp['backtol'][0],
            inputHp['backreduce'][0])) + '\n')
    # based on linmeth, append file we just wrote to with necessary params
    if inputHp['linmeth'][0] + 1 == 1:
        with open(os.path.join(cwd, args.key+'_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
            file.write(('{} {} {} {} {}'.format(int(inputHp['maxitinner'][0]),
                                                inputHp['ilumethod'][0],
                                                int(inputHp['levfill'][0]),
                                                inputHp['stoptol'][0],
                                                int(inputHp['msdr'][0]))))
    elif inputHp['linmeth'][0] + 1 == 2:
        with open(os.path.join(cwd, args.key+'_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
            file.write(('{} {} {} {} {} {} {} {} {} {}'.format(inputHp['iacl'][0],
                                                            inputHp['norder'][0],
                                                            int(inputHp['level'][0]),
                                                            int(inputHp['north'][0]),
                                                            inputHp['iredsys'][0],
                                                            inputHp['rrctols'][0],
                                                            inputHp['idroptol'][0],
                                                            inputHp['epsrn'][0],
                                                            inputHp['hclosexmd'][0],
                                                            int(inputHp['mxiterxmd'][0]))))
    # return path to nwt
    return os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM)))

def pullNWTs(args):
    """
    Pulls NWTs from MongoDB, converts them to *.nwt files and compiles
    them into a nwt_performance.csv file which contains run trial information

    args - runtime arguments

    calls:
        inputHp2nwt

    outputs:
        nwt_performance.csv
    """
    # check verbosity
    if args.verbose:
        print('[INFO] pulling trials')
    # pull trials
    try:
        trials = MongoTrials('mongo://' + args.ip + ':' + args.port + '/db/jobs', exp_key=args.key)
    except Exception:
        print('[ERROR] invalid ip, port, or key')
        return
    if args.verbose:
        print('[INFO] generating nwts and performance files')
    # get best trial from run
    try:
        inputHp2nwt(trials.best_trial.get('misc').get('vals').to_dict(), args.key + '_best', args)
    except AllTrialsFailed:
        print('[INFO] no trials to pull')
    # get the rest of the trials
    for i in range(len(trials.trials)):
        inputHp2nwt(trials.trials[i].get('misc').get('vals').to_dict(), i, args)

    # get results of each trial and compile them into a list
    results = []
    minLoss = 9999
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
    # to nwt_performance.csv
    df = pd.DataFrame(results, columns=['NWT Number',
                                        'Start Time',
                                        'Finish Time',
                                        'Loss',
                                        'Mass Balance',
                                        'Seconds Elapased',
                                        '# of Iterations',
                                        'Min Loss'])
    df.to_csv(os.path.join(os.getcwd(), args.key + '_nwts', 'nwt_performance.csv'), index = False)
    if args.verbose:
        print('[DONE] you can find your nwts at ' +
                os.path.join(os.getcwd(), args.key + '_nwts', 'nwt_performance.csv'))

if __name__ == '__main__':
    # get arguments
    parser = argparse.ArgumentParser(description='Pull NWTs from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--loop', type=bool, required=False, default=False)
    parser.add_argument('--verbose', type=bool, required=False, default=True)
    args = parser.parse_args()
    # create directory to store nwts and nwt_performance file
    try:
        os.mkdir(os.path.join(os.getcwd(), args.key + '_nwts'))
    except FileExistsError:
        pass
    # if loop re-run every minute
    if args.loop is True:
        while True:
            print('[BACKUP] backing up already tested NWTs')
            pullNWTs(args)
            time.sleep(60)
    else:
        pullNWTs(args)
