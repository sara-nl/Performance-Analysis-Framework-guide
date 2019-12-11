## Introdution to trace generation with Extrae
Extrae is the package that generates Paraver-trace files for a post-morten analysis. Installed on cca/ccb
The default behaviour of Extrae is using the LD_PRELOAD mechanism, but other interposition mechanisms are available such as DynInst (c.f. https://tools.bsc.es/extrae).

Extrae does not only offer the possibility to *instrument* the application code, but also offers to use *sampling* mechanisms to gather performance data. While adding monitors into specific location of the application produces insight which can be easily correlated with source code, the resolution of such data is directly related with the application control flow. Adding sampling capabilities into Extrae allows providing performance information of regions of code which has not been instrumented.

Extrae uses the PAPI and the PMAPI interfaces to collect information regarding the microprocessor performance

Supported programming models: MPI,OpenMP (Intel, GNU or IBM runtimes), CUDA, OpenCL, pthreads, OmpSs, Java, Python.

Official documentation: https://tools.bsc.es/extrae
https://confluence.ecmwf.int/display/UDOC/How+to+use+Extrae+and+Paraver

## Available modules on Cartesius and Lisa
On Cartesius, in the `2019` software stack, Easybuild-based modules are available for intel and foss toolchains: `Extrae/3.6.1-foss-2018b` and `Extrae/3.6.1-intel-2018b`.
On Lisa, ,in the `2019` software stack, an Easybuild-based modules is available for the foss toolchain: `Extrae/3.6.1-foss-2018b`.

## Usage on Cartesius

The general workflow for trace generation with Extrae is the following:
1 - **Tune the Extrae configuration file** Extrae uses a xml file for the configuration. Default xml configuration files can be found in `${EBROOTEXTRAE}/share/example/`. For an hybrid MPI+OpenMP configuration, choose `${EBROOTEXTRAE}/share/example/MPI+OMP/extrae.xml`. Choose the tracing library depending on the application type (sequential, MPI, OpenMP, CUDA, etc.), for an hybrid MPI+OpenMP configuration, choose `${EBROOTEXTRAE}/share/example/MPI+OMP/ld-preload/trace.sh`.
2 - **Choose between LD_PRELOAD and DynInst based run**
3 - **Run**




#### Trace generation with Extrae

##### Full example with gromacs using LD_PRELOAD
In the xml configuration files, select e.g.:
- which hardware counters are measure
- trace buffer size
- enable sampling

The submit the job. Full example of a GROMACS job using Extrae:
[ion_channel_2N.extrae_ldpreload.job](batch_scripts/ion_channel_2N.extrae_ldpreload.job)

*Warning:* I get warnings: `Extrae: WARNING! omp_get_thread_num_real is a NULL pointer. Did the initialization of this module trigger? Retrying initialization...`
-> I try to rebuild enabling heterogeneous tracing

Once finished you will have the trace (3 files):
```
gmx_mpi.prv
gmx_mpi.row
gmx_mpi.pcf
```
These are the merged files that will be read later with paraver.

However the size of the trace is to large to be viewed with Paraver:
```
-rw-r--r-- 1 maximem maximem  14G Nov 27 18:03 gmx_mpi.prv
```
So it is necessary to use filters with Paraver, or to limit the size of the trace.



To restrict the max size of the trace and tune extrae configuration options:
```
# change papi metrics
sed -i -e 's/PAPI_BR_INS,PAPI_BR_MSP,//g' extrae.xml
# buffer size
sed -i -e 's/"yes">5000000/"yes">500000/g' extrae.xml
```
-> does it do anything ?



Or use [Periodicity detection](http://gensoft.pasteur.fr/docs/extrae/3.6.1/online.html#periodicity-detection).
Following http://gensoft.pasteur.fr/docs/extrae/3.6.1/online.html#sec-onlineconfiguration, I add the following in the extrae xml configuration file.
```
<online enabled="yes"
        analysis="clustering"
        frequency="auto"
        topology="auto">
```
-> does not help, the trace is still 14 GB



##### Full example with gromacs using DynInst


#### Trace viewing and analysis with Paraver
Open Paraver
```
export PARAVERDIR=~/localinstalls/wxparaver-4.8.1/INSTALLDIR
${PARAVERDIR}/bin/wxparaver &
```

Load the trace: File>Load Trace
Then load predefined configuration files to analyse the trace:
- `${PARAVERDIR}/cfgs/mpi/analysis/mpi_stats.cfg` to measure the parallel efficiency
- `${PARAVERDIR}/cfgs/mpi/analysis/2dh_usefulduration.cfg` to measure the computation time distribution

*Warning:* make sure to click on "histogram zoom" button to see the information in the histogram view
*Warning:* in the "trace view", right click>info panel then in Colors the legend should appear (strangely it does not on Cartesius... but it does on my laptop).

```
${PARAVERDIR}/bin/stats gmx_mpi.prv -o stats
```
to obtain various statistics from Paraver traces in a .dat and a .gnuplot files.
E.g. inclusive time of routine calls.
-> it does not generate anything for me... (on my laptop and on Cartesius)
```
$ stats gmx_mpi.chop1.prv -o toto gmx_mpi.chop1.stats
Processing trace 100%
$ ls -lrt
total 5653628
-rw-r--r-- 1 maximem maximem 2584293689 dec  3 13:27 gmx_mpi.chop1.dimemas.dim
-rw-r--r-- 1 maximem maximem     380568 dec  3 13:27 gmx_mpi.chop1.dimemas-out.pcf
-rw-r--r-- 1 maximem maximem 1160297159 dec  3 13:27 gmx_mpi.chop1.dimemas-out.prv
-rw-r--r-- 1 maximem maximem     694738 dec  3 13:27 gmx_mpi.chop1.dimemas-out.row
-rw-r--r-- 1 maximem maximem       2035 dec  3 13:27 gmx_mpi.chop1.dimemas.row
-rw-r--r-- 1 maximem maximem     380828 dec  3 13:27 gmx_mpi.chop1.dimemas.pcf
-rw-r--r-- 1 maximem maximem     380828 dec  3 13:27 gmx_mpi.chop1.pcf
-rw-r--r-- 1 maximem maximem       2035 dec  3 13:27 gmx_mpi.chop1.row
-rw-r--r-- 1 maximem maximem 2042859435 dec  3 13:27 gmx_mpi.chop1.prv
```





#### Trace analysis with Paramedir
Or use `paramedir` to
"paramedir packs two sets of features, some that process the trace to compute some data and some that transform the trace, usually to reduce its size."

There are examples of filters and cutters in `${PARAVERDIR}share/filters-config/`.

```
${PARAVERDIR}/bin/paramedir -e -s gmx_mpi.prv ${PARAVERDIR}/cfgs/mpi/analysis/mpi_stats.cfg
```
-> it need a xml file, but I cannot find any doc about what to put in this file...


#### select a representative region for a large trace that cannot be loaded into memory.
https://tools.bsc.es/sites/default/files/documentation/6.paraver_trace_preparation.tar.gz


#### Dimemas
We use the Paraver trace that we generated with Extrae.
```
module load 2019
module load Dimemas/5.4.1-foss-2018b
cd ~/gromacs_testcase/7240432_gromacs_2N_16P_4T_extrae-ldpreload
```

The first step is to convert the Paraver trace into a Dimemas file using `prv2dim`.
```
# for the full trace (very large)
prv2dim gmx_mpi.prv gmx_mpi.dim

# for a smaller trace (only a portion of the whole execution)
prv2dim gmx_mpi.chop1.prv gmx_mpi.chop1.dimemas.dim
```
From the [Dimemas tutorial](https://tools.bsc.es/sites/default/files/documentation/2.introduction_to_dimemas.tar.gz), we can get examples of Dimemas configuration files. Read the `index.pdf` file for Dimemas usage instructions.
```
# simulate ideal machine: infinite bandwidth and 0 latency
Dimemas -p gmx_mpi.dimemas-out.prv -C --bandwidth 9999999 --latency 0     # ??????????? not sure this works
# or use  `Dimemas -p gmx_mpi.dimemas-out.prv -C --config-file ${EBROOTDIMEMAS}/share/cfgs/ideal.cfg`
Dimemas -p gmx_mpi.dimemas-out.prv ${EBROOTDIMEMAS}/share/cfgs/ideal.cfg --dim gmx_mpi.dim

# with the smaller trace
Dimemas -p gmx_mpi.chop1.dimemas-out.prv ${EBROOTDIMEMAS}/share/cfgs/ideal.cfg --dim gmx_mpi.chop1.dimemas.dim


```
