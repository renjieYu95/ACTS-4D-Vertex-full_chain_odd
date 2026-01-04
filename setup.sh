# === LCG view (Geant4/DD4hep/ROOT/Pythia8 etc.) ===
source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc13-opt/setup.sh

# === ACTS ===
source /afs/cern.ch/user/r/reyu/public/acts-install/bin/this_acts.sh
#source /afs/cern.ch/user/r/reyu/public/acts-install/python/setup.sh

# === ODD ===
export ODD_PATH=/afs/cern.ch/user/r/reyu/private/acts-main/thirdparty/OpenDataDetector
export LD_LIBRARY_PATH=$ODD_PATH/factory:$LD_LIBRARY_PATH

# === LCG libraries ===
#export LD_LIBRARY_PATH=/cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc13-opt/lib:/cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc13-opt/lib64:$LD_LIBRARY_PATH

# === Python path ===
export PYTHONPATH=/afs/cern.ch/user/r/reyu/public/acts-install/python:$PYTHONPATH
export PYTHONPATH=/eos/user/r/reyu/full_chain_odd/mycommon:$PYTHONPATH
source /afs/cern.ch/user/r/reyu/public/acts-install/bin/this_odd.sh
echo "✅ ACTS + ODD environment ready"

