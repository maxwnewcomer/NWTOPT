import os
import pandas as pd
import time
from hyperopt import Trials
from hyperopt.mongoexp import MongoTrials
from hyperopt.exceptions import AllTrialsFailed
import argparse

def inputHp2nwt(inputHp, NWTNUM, args):
    cwd = os.getcwd()
    with open(os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'w') as file:
        file.write(('{} {} {} {} {} {} {} {} CONTINUE {} {} {} {} {} {} {} {}'.format(inputHp['headtol'][0], inputHp['fluxtol'][0], int(inputHp['maxiterout'][0]),
        inputHp['thickfact'][0], inputHp['linmeth'][0] + 1, inputHp['iprnwt'][0], inputHp['ibotav'][0], 'SPECIFIED', inputHp['dbdtheta'][0],
        inputHp['dbdkappa'][0], inputHp['dbdgamma'][0], inputHp['momfact'][0], inputHp['backflag'][0], int(inputHp['maxbackiter'][0]), inputHp['backtol'][0],
        inputHp['backreduce'][0])) + '\n')
    if inputHp['linmeth'][0] + 1 == 1:
        with open(os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
           file.write(('{} {} {} {} {}'.format(int(inputHp['maxitinner'][0]), inputHp['ilumethod'][0], int(inputHp['levfill'][0]), inputHp['stoptol'][0], int(inputHp['msdr'][0]))))
    elif inputHp['linmeth'][0] + 1 == 2:
        with open(os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM))), 'a') as file:
           file.write(('{} {} {} {} {} {} {} {} {} {}'.format(inputHp['iacl'][0], inputHp['norder'][0], int(inputHp['level'][0]),
                      int(inputHp['north'][0]), inputHp['iredsys'][0], inputHp['rrctols'][0],
                      inputHp['idroptol'][0], inputHp['epsrn'][0], inputHp['hclosexmd'][0],
                      int(inputHp['mxiterxmd'][0]))))
    return os.path.join(cwd, args.key + '_nwts', ('nwt_{}.nwt'.format(NWTNUM)))

def pullNWTs(ip, port, key, args):
    if args.verbose:
        print('[INFO] pulling trials')
    try:
        trials = MongoTrials('mongo://' + ip + ':' + port + '/db/jobs', exp_key=key)
    except:
        print('[ERROR] invalid ip, port, or key')
        return
    if args.verbose:
        print('[INFO] generating nwts and performance files')
    try:
        inputHp2nwt(trials.best_trial.get('misc').get('vals').to_dict(), args.key + '_best', args)
    except AllTrialsFailed as e:
        print('[INFO] no trials to pull')
    for i in range(len(trials.trials)):
        inputHp2nwt(trials.trials[i].get('misc').get('vals').to_dict(), i, args)

    results = []
    minLoss = 9999
    for i in range(len(trials.trials)):
        trial = trials.trials[i].get('result').to_dict()
        try:
            if trial['loss'] < minLoss:
                minLoss = trial['loss']
            results.append([i, trial['eval_time'], trial['finish_time'], trial['loss'], trial['mass_balance'], trial['sec_elapsed'], trial['iterations'], minLoss])
        except:
            pass
    df = pd.DataFrame(results, columns=['NWT Number', 'Start Time', 'Finish Time', 'Loss', 'Mass Balance', 'Seconds Elapased', '# of Iterations', 'Min Loss'])
    df.to_csv(os.path.join(os.getcwd(), args.key + '_nwts', 'nwt_performance.csv'), index = False)
    if args.verbose:
        print('[DONE] you can find your nwts at ' + os.path.join(os.getcwd(), args.key + '_nwts', 'nwt_performance.csv'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull NWTs from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--loop', type=bool, required=False, default=False)
    parser.add_argument('--verbose', type=bool, required=False, default=True)
    args = parser.parse_args()
    try:
        os.mkdir(os.path.join(os.getcwd(), args.key + '_nwts'))
    except:
        pass
    if args.loop == True:
        while True:
            print('[BACKUP] backing up already tested NWTs')
            pullNWTs(args.ip, args.port, args.key, args)
            time.sleep(60)
    else:
        pullNWTs(args.ip, args.port, args.key, args)
