# IPM
IPM is a portable profiling infrastructure for parallel codes.

It provides a low-overhead performance summary of the computation and communication in a parallel program.
The amount of detailed reported is selectable at runtime via environment variables or through a MPI_Pcontrol interface.

IPM has extremely low overhead, is scalable and easy to use requiring no source code modification.


http://ipm-hpc.sourceforge.net/usage.html

from NERSC userinfo: https://www.nersc.gov/users/software/performance-and-debugging-tools/ipm/
https://docs.nersc.gov/programming/performance-debugging-tools/ipm/

from POP-COE: https://pop-coe.eu/further-information/learning-material/profilingimpi



One can add user-defined regions and events in the source code using 'MPI_Pcontrol' (c.f. http://ipm-hpc.sourceforge.net/usage.html)


#### INTEL
Set
```
export I_MPI_STATS=ipm
```
to enable IPM.

Set
```
export I_MPI_STATS_FILE=prof.dat
```
to specify the file (here 'prof.dat') where to generate the IPM report.

+ use other IPM options if needed


#### FOSS
IPM uses the LD_PRELOAD mechanism.

Loading module `IPM/2.0.6-foss-2018b` sets LD_PRELOAD to the `libipm.so` library.

Then a normal run will use the LD_PRELOAD mechanism and generate an xml file containing the IPM report.


IPM can also collect PAPI metrics.

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





## Collecting of PAPI counters with IPM
*Warning:* PAPI counters are collected for each MPI process, IPM does not support threads.

With a simple matvec example: [matvec.cpp](matvec/matvec.cpp), and a modified version with a lot of cache misses: [matvec_loop-interchange.cpp](matvec/matvec_loop-interchange.cpp), try different setsof PAPI counters.
```
module load 2019
module load foss/2018b
module load IPM/2.0.6-foss-2018b

mpicxx -O0 matvec.cpp -o matvec

export IPM_REPORT=full
export IPM_LOGDIR=matvec_ipm

export IPM_HPM="PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_SP_OPS,PAPI_DP_OPS,PAPI_VEC_SP,PAPI_VEC_DP"
mpirun -np 1 matvec
```


With `export IPM_HPM="PAPI_TOT_INS,PAPI_LD_INS,PAPI_L1_TCM,PAPI_LST_INS"` and `export IPM_HPM="PAPI_TOT_INS,PAPI_L2_TCM,PAPI_L3_TCM,PAPI_L2_TCA,PAPI_L3_TCA"`
Note that:
- "PAPI_LD_INS" (number instructions) stays about the same 8629428590 vs. 8630065425,
- "PAPI_L1_TCM" (total L1 cache misses) goes from  21280135 to 624849188 (almost 30x increase),
- "PAPI_L2_TCM" (total L2 cache misses) goes from  11021593 to 710864014 (more than 60x increase),
- "PAPI_L2_TCA" (total L2 cache accesses) goes from 3523786 to 556664816 (more than 150x increase),
- "PAPI_L3_TCM" (total L3 cache misses) goes from  9980157 to 14652164 (about 1.5x increase),
- "PAPI_L3_TCA" (total L3 cache accesses) goes from 11010723 to 711205301 (more than 60x increase)
*Remark:* the number of L2 cache misses is greater than the number of cache accesses.. How is that possible ?


With `export IPM_HPM="PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_SP_OPS,PAPI_DP_OPS,PAPI_VEC_SP,PAPI_VEC_DP"`, we can see that the loop is not vectorized, as the number of vectorized operations and instructions is almost 0.
