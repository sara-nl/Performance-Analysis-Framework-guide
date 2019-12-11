#!/bin/bash

source /home/maximem/.local/easybuild/RedHatEnterpriseServer7/2019/software/Extrae/3.6.1-foss-2018b/etc/extrae.sh

export OMP_NUM_THREADS=4
export EXTRAE_CONFIG_FILE=../extrae.xml
export LD_PRELOAD=${EXTRAE_HOME}/lib/libompitrace.so # For C apps
#export LD_PRELOAD=${EXTRAE_HOME}/lib/libompitracef.so # For Fortran apps

## Run the desired program
$*

