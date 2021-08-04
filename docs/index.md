## Welcome to NWTOPT for MODFLOW-NWT

NWTOPT is a Linux based, hyperparameter optimization and tuning system for steady-state and transient models ran by MODFLOW-NWT. NWTOPT is a distributed, parallel compute, and MODFLOW-NWT specific extension of the hyperparameter optimization [Hyperopt](https://github.com/hyperopt/hyperopt) framework. While you can run NWTOPT on any system of Linux computers, NWTOPT also comes with specific support for [HTCondor](https://research.cs.wisc.edu/htcondor/), a High Throughput Computing system for large collections of distributively owned computing resources.

### Links to resources
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Your First Time Using NWTOPT](#your-first-time-using-nwtopt)
- [Examples](#examples)
- [FAQ](#faq)

### How It Works
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras consectetur turpis eu felis gravida, et posuere erat eleifend. Integer neque tortor, dictum at magna vel, gravida imperdiet dolor. Duis aliquet tortor ac urna maximus, porttitor interdum erat interdum. Etiam id lobortis nisl. Morbi sit amet imperdiet augue. Fusce rutrum est lorem, a placerat erat pulvinar a. Sed consectetur aliquam lorem, a vestibulum justo gravida rhoncus. Maecenas pharetra dui ut nisl vehicula porttitor. Praesent sed enim eget sapien dignissim porttitor. Mauris lectus libero, rutrum nec vulputate eget, sollicitudin nec massa. Donec at suscipit tortor. Mauris vel vestibulum augue.
### Requirements
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras consectetur turpis eu felis gravida, et posuere erat eleifend. Integer neque tortor, dictum at magna vel, gravida imperdiet dolor. Duis aliquet tortor ac urna maximus, porttitor interdum erat interdum. Etiam id lobortis nisl. Morbi sit amet imperdiet augue. Fusce rutrum est lorem, a placerat erat pulvinar a. Sed consectetur aliquam lorem, a vestibulum justo gravida rhoncus. Maecenas pharetra dui ut nisl vehicula porttitor. Praesent sed enim eget sapien dignissim porttitor. Mauris lectus libero, rutrum nec vulputate eget, sollicitudin nec massa. Donec at suscipit tortor. Mauris vel vestibulum augue.

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
and your jobs will be sent out through condor to your specified ```<num_workers```, train for ```<num_trials>```, and store that data in the MongoDB under your ```<job_key>```. During optimization the NWTs generated will be pulled into a folder called ```<job_key>```_nwts. In there you can find all the NWTs used in training as well as a nwt_performance.csv which goes into detailed performance reporting.


### Examples



Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras consectetur turpis eu felis gravida, et posuere erat eleifend. Integer neque tortor, dictum at magna vel, gravida imperdiet dolor. Duis aliquet tortor ac urna maximus, porttitor interdum erat interdum. Etiam id lobortis nisl. Morbi sit amet imperdiet augue. Fusce rutrum est lorem, a placerat erat pulvinar a. Sed consectetur aliquam lorem, a vestibulum justo gravida rhoncus. Maecenas pharetra dui ut nisl vehicula porttitor. Praesent sed enim eget sapien dignissim porttitor. Mauris lectus libero, rutrum nec vulputate eget, sollicitudin nec massa. Donec at suscipit tortor. Mauris vel vestibulum augue.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras consectetur turpis eu felis gravida, et posuere erat eleifend. Integer neque tortor, dictum at magna vel, gravida imperdiet dolor. Duis aliquet tortor ac urna maximus, porttitor interdum erat interdum. Etiam id lobortis nisl. Morbi sit amet imperdiet augue. Fusce rutrum est lorem, a placerat erat pulvinar a. Sed consectetur aliquam lorem, a vestibulum justo gravida rhoncus. Maecenas pharetra dui ut nisl vehicula porttitor. Praesent sed enim eget sapien dignissim porttitor. Mauris lectus libero, rutrum nec vulputate eget, sollicitudin nec massa. Donec at suscipit tortor. Mauris vel vestibulum augue.


### FAQ
