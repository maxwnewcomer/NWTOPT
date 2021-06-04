#!/bin/bash
# file name: nwtopt.sh
date
pwd
echo ................................
echo
mkdir nwtenv
mv nwtenv.tgz nwtenv/
cd nwtenv
tar xfz nwtenv.tgz
cd -
source nwtenv/bin/activate
echo
conda-unpack
echo ...Changed Python Environment...
echo
mv NWT_SUBMIT/NWTOPT_FILES/objective.py nwtenv/bin/objective.py
mv NWT_SUBMIT/NWTOPT_FILES/mfnwt NWT_SUBMIT/PROJECT_FILES/mfnwt
mkdir NWT_SUBMIT/PROJECT_FILES/nwts
mv NWT_SUBMIT/NWTOPT_FILES/nwtnum.txt NWT_SUBMIT/PROJECT_FILES/nwts/nwtnum.txt
echo ...Moved Necessary Files.....
echo
ls
dir=$(pwd)
${dir}/nwtenv/bin/hyperopt-mongo-worker --mongo=$1 --poll-interval=$2
