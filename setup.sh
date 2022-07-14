#! /bin/bash
echo "Enter an environment name:"
read envname
read -p "Press enter to create new environment $envname"
conda env create -n $envname -f conda_requirements.yml
read -p "Press enter to activate $envname"
conda activate $envname
read -p "Press enter to pack environment"
conda pack -n <env_name> -o nwtenv.tgz
read -p "Press enter to create necessary directories"
mkdir mongodb/db
mkdir logs
mkdir logs/condor_logs; mkdir logs/errors; mkdir logs/outputs