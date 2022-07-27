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

class MF6HParams():

    def __init__(self):
        self.hparams =[
            #OPTIONS PARAMETERS
            hp.choice('no_ptc',
                [
                    'first','all'
                ]), #0
            hp.uniform('ats_outer_maximum_fraction', 0.0, 0.5), #1
            #NONLINEAR PARAMETERS 
            hp.uniform('outer_dvclose', .001, 5.), #2
            hp.quniform('outer_maximum', 1, 500, 1), #3
            hp.choice('under_relaxation', #4
                [
                    {'under_relaxation':'none'},
                    {'under_relaxation': 'simple',
                        'under_relaxation_gamma': hp.uniform('under_relaxation_gamma',0.01,1),

                    },
                    {'under_relaxation': 'cooley',
                        'under_relaxation_gamma': hp.uniform('under_relaxation_gamma',0.0,1)

                    },
                    {'under_relaxation': 'dbd',
                        'under_relaxation_gamma': hp.uniform('under_relaxation_gamma',0.0,1),
                        'under_relaxation_theta': hp.uniform('under_relaxation_theta',0.2,0.99),
                        'under_relaxation_kappa': hp.uniform('under_relaxation_kappa',0.03,0.3),
                        'under_relaxation_momentum': hp.uniform('under_relaxation_momentum',0.03,0.3)

                    }
                ]),
            hp.choice('backtracking_number', #5
                [
                    {'backtracking_number': 0},
                    {'backtracking_number': hp.quniform(1,20,1),
                        'backtracking_tolerance': hp.loguniform('backtracking_tolerance', np.log(1.0), np.log(1.0e6)),
                        'backtracking_reduction_factor': hp.uniform('backtracking_reduction_factor', 0.1, 0.3),
                        'backtracking_residual_limit': hp.uniform('backtracking_residual_limit', 5, 100)                
                    }
                ]),
            #LINEAR PARAMETERS 
            hp.quniform('inner_maximum', 40, 650, 1),#6
            hp.uniform('inner_dvclose', 1.0e-7, 1.0),#7
            hp.uniform('inner_rclose', 1.0e-1, 1.0e7),#8
            # NOTE: skipping rclose_option because very units dependent
            hp.choice('linear acceleration', [ #9
                'CG', 'BICGSTAB'
            ]),
            hp.choice('relaxation_factor', #10
                [
                    {'relaxation_factor':0.0},
                    {'relaxation_factor':hp.uniform('relaxation_factor',0.9,1.0)}
                ]),
            
            hp.choice('preconditioner_drop_tolerance', #11
                [
                    {'preconditioner_drop_tolerance':0.0},
                    {'preconditioner_drop_tolerance':hp.uniform('preconditioner_drop_tolerance',1e-5, 1e-3),
                    'preconditioner_levels':hp.quniform('preconditioner_levels',6,9,1),
                    }
                ]),
            hp.choice('number_orthogonalizations', #12
                [
                    {'number_orthogonalizations':0},
                    {'number_orthogonalizations':hp.quniform('number_orthogonalizations',14,10,1)
                    }
                ]),
            hp.choice('scaling_method', #13
                [
                    'none','diagonal','polcg','l2norm'
                ]),
            hp.choice('reordering_method', #14
                [
                    'none','rcm','md'
                ])
        ]
        
        self.filetype = 'ims'

    def HParam2File(inputHp, filepath):
        with open(filepath) as file:
            # write options block
            file.write('BEGIN OPTIONS\n')
            file.write(f'PRINT_OPTION ALL\nNO_PTC {inputHp[0]}\nATS_OUT_MAXIMUM_FRACTION {inputHp[1]}\n')
            file.write('END OPTIONS\n')

            # write NONLINEAR BLOCK
            file.write('BEGIN NONLINEAR\n')
            file.write(f'OUTER_DVCLOSE {inputHp[2]}\nOUTER_MAXIMUM {inputHp[3]}\n')
            # write out all the options under under_relaxation
            [file.write(f'{k.upper()} {val}\n') for k,val in inputHp[4].items()]
            # write out all the options under backtracking_number
            [file.write(f'{k.upper()} {val}\n') for k,val in inputHp[5].items()]
            file.write('END NONLINEAR\n')

            # write LINEAR block
            file.write('BEGIN LINEAR\n')
            file.write(f'INNER_MAXIMUM {inputHp[6]}\nINNER_DVCLOSE {inputHp[7]}\n')
            file.write(f'INNER_RCLOSE{inputHp[8]}\nLINEAR_ACCELERATION {inputHp[9]}\n')
            # write out all the options under relaxation_factor
            [file.write(f'{k.upper()} {val}\n') for k,val in inputHp[10].items()]        
            # write out all the options under preconditioner_drop_tolerance
            [file.write(f'{k.upper()} {val}\n') for k,val in inputHp[11].items()]        
            # write out all the options under number_orthogonalizations
            [file.write(f'{k.upper()} {val}\n') for k,val in inputHp[12].items()]        
            file.write(f'SCALING_METHOD{inputHp[13]}\REORDERING_METHOD {inputHp[14]}\n')
            file.write('END LINEAR\n')
            
        # print('[INFO] pulling nwt from', os.path.join(cwd, 'nwts', ('nwt_{}.nwt'.format(SOLNUM))))
        return filepath
