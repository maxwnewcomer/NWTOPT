from hyperopt import hp

class MF5HParams():
    def __init__(self):
        self.hparams = [
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
        self.filetype = 'nwt'
    def HParam2File(self, inputHp, filepath):
        """
        Converts MongoTrials dictionary hyperparameters to *.nwt file

        inputHp - MongoTrials dictionary formatted hyperparameters
        filepath - path to file to write to

        returns path to new *.nwt file
        """
        # write hyperparameters to file
        with open(filepath, 'w') as file:
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
            with open(filepath, 'a') as file:
                file.write(('{} {} {} {} {}'.format(int(inputHp['maxitinner'][0]),
                                                    inputHp['ilumethod'][0],
                                                    int(inputHp['levfill'][0]),
                                                    inputHp['stoptol'][0],
                                                    int(inputHp['msdr'][0]))))
        elif inputHp['linmeth'][0] + 1 == 2:
            with open(filepath, 'a') as file:
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
        return filepath
        
