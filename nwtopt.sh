#!/bin/bash
# file name: nwtopt.sh
LD_LIBRARY_PATH=/cxfs/projects/root/opt/wine/lib64
PATH=/cxfs/projects/root/opt/wine/bin:$PATH
_LMFILES_=/etc/modulefiles/wine/1.8
INCLUDE=/cxfs/projects/root/opt/wine/include
wine64 --version
export WINEPREFIX=$_CONDOR_SCRATCH_DIR
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
python3 --version
pip freeze
echo ...Changed Python Environment...
echo
mv NWT_SUBMIT/NWTOPT_FILES/objective.py nwtenv/bin/objective.py
mv run.sh NWT_SUBMIT/PROJECT_FILES/run.sh
mv NWT_SUBMIT/NWTOPT_FILES/mfnwt NWT_SUBMIT/PROJECT_FILES/mfnwt
mkdir NWT_SUBMIT/PROJECT_FILES/nwts
mv NWT_SUBMIT/NWTOPT_FILES/nwtnum.txt NWT_SUBMIT/PROJECT_FILES/nwts/nwtnum.txt
echo ...Moved Necessary Files.....
echo
ls
dir=$(pwd)
${dir}/nwtenv/bin/hyperopt-mongo-worker --mongo=$1 --poll-interval=$2
