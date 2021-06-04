import os
import time
import fileinput
from subprocess import call
from shutil import copyfile, rmtree
import argparse
import pandas as pd
from hyperopt import fmin, rand, atpe, tpe, hp, STATUS_OK, Trials
from hyperopt.mongoexp import MongoTrials
import objective

cwd = os.getcwd()
# print(cwd[0:-12])
# for file in os.listdir(os.path.join(cwd[0:-12], 'PROJECT_FILES')):
#     if file.endswith('.nam'):
#         namefile = file

try:
    os.mkdir(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
except:
    rmtree(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
    os.mkdir(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))

hparams = [
    hp.choice('linmeth',
        [
            {'linmeth': 1,
               'maxitinner': hp.quniform('maxitinner', 25, 1000, 1),
               'ilumethod': hp.choice('ilumethod', [1, 2]),
               'levfill': hp.quniform('levfill', 0, 10, 1),
               'stoptol': hp.uniform('stoptol', .000000000001, .00000001),
               'msdr': hp.quniform('msdr', 5, 20, 1)
            },
            {'linmeth': 2,
                'iacl': hp.choice('iacl', [0, 1, 2]),
                'norder': hp.choice('norder', [0, 1, 2]),
                'level': hp.quniform('level', 0, 10, 1),
                'north': hp.quniform('north', 2, 10, 1),
                'iredsys': hp.choice('iredsys', [0, 1]),
                'rrctols': hp.uniform('rrctols', 0., .0001),
                'idroptol': hp.choice('idroptol', [0, 1]),
                'epsrn': hp.uniform('epsrn', .00005, .001),
                'hclosexmd': hp.uniform('hclosexmd', .00001, .001),
                'mxiterxmd': hp.quniform('mxiterxmd', 25,  100, 1)
            }
        ]),
    hp.uniform('headtol', .01, 5.),
    hp.uniform('fluxtol', 5000, 1000000),
    hp.quniform('maxiterout', 100, 400, 1),
    hp.uniform('thickfact', .000001, .0005),
    hp.choice('iprnwt', [0, 2]),
    hp.choice('ibotav', [0, 1]),
    hp.choice('options', ['SPECIFIED']),
    hp.uniform('dbdtheta', .4, 1.),
    hp.uniform('dbdkappa', .00001, .0001),
    hp.uniform('dbdgamma', 0., .0001),
    hp.uniform('momfact', 0., .1),
    hp.choice('backflag', [0, 1]),
    hp.quniform('maxbackiter', 10, 50, 1),
    hp.uniform('backtol', 1., 2.),
    hp.uniform('backreduce', .00001, 1.),
]

def trials2csv(trials):
    df = pd.DataFrame(trials, columns=['result'])
    df.to_csv(os.path.join(os.getcwd(), 'nwt_performance.csv'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull NWTs from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--random', type=bool, required=False, default=True)
    parser.add_argument('--trials', type=int, help='num trials you would like to run')
    args = parser.parse_args()
    trials = MongoTrials('mongo://'+ args.ip + ':'+ args.port + '/db/jobs', exp_key=args.key)
    try:
        os.remove(os.path.join(os.getcwd(), 'nwts/nwtnum.txt'))
    except:
        pass
    with open(os.path.join(os.getcwd(), 'nwts/nwtnum.txt'), 'w+') as f:
        f.write('0')
    if args.random == False:
        bestHp = fmin(fn=objective.objective,
                      space=hparams,
                      algo=tpe.suggest,
                      max_evals=args.trials,
                      trials=trials)
    else:
        bestRandHp = fmin(fn=objective.objective,
                      space=hparams,
                      algo=rand.suggest,
                      max_evals=args.trials,
                      trials=trials)
