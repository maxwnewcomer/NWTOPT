"""
Optimization Script used to define hyperparameter space, and manage optimization

[usage]: python3 optimize_NWT.py --ip {mongodb ip} --port {mongodb port} --key {mongodb job key}
    --random {set True if random hyperparameter generation is desired}
    --trials {number of trials to run}
"""
# Disabling pylint snake_case warnings, import error warnings, and
# redefining out of scope warnings, too many local variables
# too many branches, too many statements
#
# pylint: disable = E0401, C0103, W0621, R0914, R0912, R0915, R0915


import os
from shutil import rmtree
import argparse
from hyperopt import fmin, rand, tpe, hp
from hyperopt.mongoexp import MongoTrials
import objective

cwd = os.getcwd()

# create nwt directory used by objective.py
try:
    os.mkdir(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
except FileExistsError:
    rmtree(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))
    os.mkdir(os.path.join(os.path.join(cwd[0:-12], 'PROJECT_FILES'), 'nwts'))

# defining hyperparameter hyperparameter space
# this is editable if you know what range of
# values you are looking to optimize on
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

if __name__ == '__main__':
    # get arguments
    parser = argparse.ArgumentParser(description='Pull NWTs from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--random', type=bool, required=False, default=False)
    parser.add_argument('--trials', type=int, help='num trials you would like to run')
    args = parser.parse_args()

    # connect to database
    trials = MongoTrials('mongo://'+ args.ip + ':'+ args.port + '/db/jobs', exp_key=args.key)
    try:
        os.remove(os.path.join(os.getcwd(), 'nwts/nwtnum.txt'))
    except Exception:
        pass

    # track number of trials ran
    with open(os.path.join(os.getcwd(), 'nwts/nwtnum.txt'), 'w+') as f:
        f.write('0')
    # run random optimization
    if args.random is False:
        print('TPE Run')
        bestHp = fmin(fn=objective.objective,
                      space=hparams,
                      max_queue_len=3,
                      algo=tpe.suggest,
                      max_evals=args.trials,
                      trials=trials)
    # run tpe optimization
    else:
        bestRandHp = fmin(fn=objective.objective,
                      space=hparams,
                      max_queue_len=3,
                      algo=rand.suggest,
                      max_evals=args.trials,
                      trials=trials)
