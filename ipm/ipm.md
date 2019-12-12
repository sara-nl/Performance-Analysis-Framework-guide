# IPM
http://ipm-hpc.sourceforge.net/usage.html

from NERSC userinfo: https://www.nersc.gov/users/software/performance-and-debugging-tools/ipm/
https://docs.nersc.gov/programming/performance-debugging-tools/ipm/

from POP-COE: https://pop-coe.eu/further-information/learning-material/profilingimpi

#### INTEL
with Intel: easy to use, just set
export I_MPI_STATS=ipm
export I_MPI_STATS_FILE=prof.dat
to export the report in file 'prof.dat'
and use function 'MPI_Pcontrol' in source code to define code regions and events
+ use other IPM options if needed


#### FOSS
IPM uses the LD_PRELOAD mechanism.
Loading module `IPM/2.0.6-foss-2018b` sets LD_PRELOAD to the `libipm.so` library.

Then a normal run will use the LD_PRELOAD mechanism and generate an xml file containing the IPM report.

IPM can collects PAPI metrics.
In our module, the default set of PAPI metrics that are gathered is:
```
IPM_HPM="PAPI_TOT_INS,PAPI_L1_DCM,PAPI_LST_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_RES_STL,PAPI_STL_ICY,PAPI_STL_CCY"
```
This can be tuned by modifying the environment variable `IPM_HPM`.


IPM accepts a few options:
```
export IPM_REPORT=full
export IPM_LOGDIR=$RESULTDIR
export IPM_HPM="PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_SP_OPS,PAPI_DP_OPS,PAPI_VEC_SP,PAPI_VEC_DP"
```


#### automatic computation of the POP metrics
use my python scripts:
[ipm-foss_compute_POP-metrics.py](ipm-foss_compute_POP-metrics.py)
[ipm-intel_compute_POP-metrics.py](ipm-intel_compute_POP-metrics.py)
