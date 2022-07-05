from hyperopt import hp
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
