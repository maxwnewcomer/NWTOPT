echo "Removing Pulled NWTs"
rm -rf *_nwts/
echo "Removing Logs"
rm logs/condor_logs/*.log
rm logs/errors/*.txt
rm logs/outputs/*.txt
echo "Done"
