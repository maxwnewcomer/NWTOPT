## Welcome to NWTOPT for MODFLOW-NWT

NWTOPT is a Linux based, hyperparameter optimization and tuning system for steady-state and transient models ran by MODFLOW-NWT. NWTOPT is a distributed, parallel compute, and MODFLOW-NWT specific extension of the hyperparameter optimization [Hyperopt](https://github.com/hyperopt/hyperopt) framework. While you can run NWTOPT on any system of Linux computers, NWTOPT also comes with specific support for [HTCondor](https://research.cs.wisc.edu/htcondor/), a High Throughput Computing system for large collections of distributively owned computing resources.

### Links to resources
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Your First Time Using NWTOPT](#your-first-time-using-nwtopt)
- [Common Issues and Fixes](#common-issues-and-fixes)
- [Future Work](#future-work)

### How It Works

The optimization approach we’ve coded in NWTOPT is a distributed, parallel compute, and MODFLOW specific extension of [Hyperopt](https://github.com/hyperopt/hyperopt). Hyperopt provides a Tree of Parzen Estimators (TPE) hyperparameter optimization algorithm, a worker script, and a Python interface used to communicate with workers through a persistent database that tracks and synthesizes the workers’ results.  NWTOPT includes extensions to Hyperopt that facilitate optimization of MODFLOW Newton-Raphson solver settings in a high-throughput computing environment.

### Requirements

NWTOPT is meant to be ran on Linux systems. NWTOPT also requires [Anaconda](anaconda.org) on both the worker and master systems. If you would like to enable easy parallelization, HTCondor job management is supported but not required.

### Installation

To install, simply:
```
git clone https://github.com/maxwnewcomer/NWTOPT.git
```

Once you have cloned the repository, you need to create the Python environment that NWTOPT and it's workers use. 

```
conda env create -n <env_name> -f conda_requirements.yml
conda activate <env_name>
```

Then, you will need to pack the environment into something that can be sent to each worker. To do this we will use conda pack:

```
conda pack -n <env_name> -o nwtenv.tgz
```

Next you will need to create the mongodb database folder so your information can be stored persistently and accessed by NWTOPT

```
mkdir mongodb/db
```

If you will be using HTCondor to distribute your runs, make sure you create the log directories as follows:
```
mkdir logs
cd logs
mkdir condor_logs; mkdir errors; mkdir outputs
```

You should now be ready to run your first optimization. Continue to the next section to see how you can start using NWTOPT.


### Your First Time Using NWTOPT

To start using NWTOPT all you will need is your model's files and it's run command.

Put all of your model's files, including the executable you would like to run, in NWTOPT/NWT_SUBMIT/PROJECT_FILES/

Then edit the NWTOPT/run.sh script to specify the run command you would like to execute on each worker. At the bottom of the run.sh script you can enter a trial timeout (in minutes). If left blank no timeout will be implemented.

Finally run the below code to start the DB, Condor Submission, and the Optimization:

```
python NWTOPT.py --ip <database ip> --port <database port> --key <unique optimization run id> --trials <number of trials to run> --enable_condor <True if condor run> --workers <number of condor workers to spawn>
```

NWTOPT will then start recording the best trial on the STDOUT and give you some run progress information. When all trials are finished the NWTOPT.py process will automatically terminate.

This script will also place all the nwts in NWTOPT/\<unique optimization run id>_nwts and will also compile a nwt_performance.csv which records all Mass Balance and Time Elapsed information for each trial. A typical workflow includes starting all the process as stated above (using a screen session for optimize_NWT.py and the MongoDB process) and then running pull_nwts.py with loop set to True.

### Common Issues and Fixes
If you are encounterring MongoDB errors due to linking try running:
```
cd mongodb
(cd bin && { for F in ../mongodb-linux-x86_64-2.2.2/bin/* ; do echo "linking $F" ; ln -s $F ; done } )
```
  
If all of your HTCondor runs seem to be dropping, check the logs/errors/*_errors.txt files.

If there seem to be database connection problems either try changing your database port or try lowering the number of HTCondor workers you send out in your nwtopt.sub file

Any other errors should be printed in the logs/errors/*_errors.txt files, and should be diagnosable from there.

### Future Work

- [x] Transient model support
- [x] WINE support
- [ ] MODFLOW-6 support
- [x] GSFLOW support
- [ ] Automatic insight generation
- [x] Master NWTOPT script
