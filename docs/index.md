## Welcome to NWTOPT for MODFLOW-NWT

NWTOPT is a Linux based, hyperparameter optimization and tuning system for steady-state and transient models ran by MODFLOW-NWT. NWTOPT is a distributed, parallel compute, and MODFLOW-NWT specific extension of the hyperparameter optimization [Hyperopt](https://github.com/hyperopt/hyperopt) framework. While you can run NWTOPT on any system of Linux computers, NWTOPT also comes with specific support for [HTCondor](https://research.cs.wisc.edu/htcondor/), a High Throughput Computing system for large collections of distributively owned computing resources.

### Links to resources
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Your First Time Using NWTOPT](#your-first-time-using-nwtopt)
- [NWTOPT Arguments](#nwtopt-arugments)
- [Example Results](#example-results)
- [FAQ](#faq)

### How It Works

The optimization approach we’ve coded in NWTOPT is a distributed, parallel compute, and MODFLOW specific extension of [Hyperopt](https://github.com/hyperopt/hyperopt). Hyperopt provides a Tree of Parzen Estimators (TPE) hyperparameter optimization algorithm, a worker script, and a Python interface used to communicate with workers through a persistent database that tracks and synthesizes the workers’ results.  NWTOPT includes extensions to Hyperopt that facilitate optimization of MODFLOW Newton-Raphson solver settings in a high-throughput computing environment.

### Requirements

NWTOPT is meant to be ran on Linux systems. NWTOPT also requires [Anaconda](anaconda.org) on both the worker and master systems. If you would like to enable easy parallelization, HTCondor job management is supported but not required.

### Installation

To install, simply:
```
git clone https://github.com/maxwnewcomer/NWTOPT.git
```

Once you have cloned the repository, you need to create the Python environment that NWTOPT and it's workers use. To do this either:

```
#Conda Environment Installation (recommended)
conda create --name <env_name> --file conda_requirements.txt
conda activate <env_name>

#Pip Environment Installation
python3 -m pip install -r pip_requirements.txt
```

Then, you will need to pack the environment into something that can be sent to each worker. To do this we will use conda pack:

```
conda pack -n <env_name> -o nwtenv.tgz
```

You should now be ready to run your first optimization. Continue to the next section to see how you can start using NWTOPT.


### Your First Time Using NWTOPT

To start using NWTOPT all you will need is your model's files and it's run command.

Put all of your model's files, including the executable you would like to run, in NWTOPT/NWT_SUBMIT/PROJECT_FILES/

Then edit the NWTOPT/run.sh script to specify the run command you would like to execute on each worker. At this time, ignore the timeout section of this script, as the following command will overwrite whatever timeout you put in.

Next, all you need to do is run

```
python3 NWTOPT.py --trials <num_trials> --workers <num_workers> --key <job_key>
```
and your jobs will be sent out through condor to your specified ```<num_workers>```, train for ```<num_trials>```, and store that data in the MongoDB under your ```<job_key>```. During optimization the NWTs generated will be pulled into a folder called ```<job_key>```_nwts. In there you can find all the NWTs used in training as well as a nwt_performance.csv which goes into detailed performance reporting.


## NWTOPT Arguments

| Argument | Description | Default | Required |
| -------  | ----------- | ------- | -------- |
| --ip     | The ip address for the MongoDB | Current IP address | No |
| --port   | The port that the MongoDB will be accessible at | 27017 | No |
| --key    | The key that the MongoDB will use to store the results of the optimization** | None | Yes |
| --workers | The number of workers you would like to start (if using HTCondor) | 0 | No |
| --random | Set to True to switch from TPE optimization algorithm to Random Search | False | No |
| --trials | The number of optimization trials you would like to run | None | Yes |
| --poll_interval | The amount of time (in seconds) each HTCondor worker polls the MongoDB for a new set of hyperparameters | 240 | No
| --enable-condor | Set to False to disable sending out the run through HTCondor | True | No |
| --timeout | The amount of time (in minutes) for a model run to be considered failed | None | No |

** use the same key to resume progress on an optimization run

## Example Results


## FAQ


## Future Work

- [x] Transient model support
- [x] WINE support
- [ ] MODFLOW-6 support
- [ ] GSFLOW support
- [ ] Automatic insight generation
