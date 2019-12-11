# Performance analysis with Extrae - Paraver - Dimemas


## General information
[Extrae](https://tools.bsc.es/extrae) is the package that generates Paraver-trace files for a post-mortem analysis.

The default behaviour of Extrae is using the LD_PRELOAD mechanism, but other interposition mechanisms are available such as DynInst (not available through our current modules on Lisa and Cartesius, as it requires dyninst to be installed first).

Extrae does not only offer the possibility to instrument the application code, but also offers to use sampling mechanisms to gather performance data. While adding monitors into specific location of the application produces insight which can be easily correlated with source code, the resolution of such data is directly related with the application control flow. Adding sampling capabilities into Extrae allows providing performance information of regions of code which has not been instrumented.

Extrae uses the PAPI and the PMAPI interfaces to collect information regarding the microprocessor performance

Supported programming models: MPI,OpenMP (Intel, GNU or IBM runtimes), CUDA, OpenCL, pthreads, OmpSs, Java, Python.

Official Extrae documentation: https://tools.bsc.es/doc/html/extrae/.


## Available modules on Cartesius and Lisa in the 2019 software stack
On Cartesius, Easybuild-based modules are available for intel and foss toolchains: `Extrae/3.6.1-foss-2018b` and `Extrae/3.6.1-intel-2018b`.

On Lisa, an Easybuild-based modules is available for the foss toolchain: `Extrae/3.6.1-foss-2018b`.

## General workflow
The general workflow for trace generation with Extrae is the following:
1. **Tune the Extrae configuration file** The configuration of Extrae is highly customizable through the [xml file](https://tools.bsc.es/doc/html/extrae/xml.html).
2. **Run job with Extrae instrumentation through LD_PRELOAD**
3. **Adapt the Extrae configuration file and re-run the job, or filter the generated trace if needed** The complete generated trace can be too large to be viewed with paraver.
4. **Analyse the generated trace with Paraver**
5. **Generate a trace with a simulated hardware configuration using Dimemas** This helps evaluate the hardware components that are stressed and have a high impact on the performance.

In the following, we use Gromacs ion_channel example as a use case for a performance analysis with Extrae - Paraver - Dimemas.


## Trace generation with Extrae

#### Tuning the Extrae configuration file
First choose an appropriate xml configuration file template and tracing library for the programming model used.
Templates can be found in `${EBROOTEXTRAE}/share/example/`.

For an hybrid OpenMP+MPI application:
- start from the template configuration file [${EBROOTEXTRAE}/share/example/MPI+OMP/extrae.xml](extrae_cfgs/extrae_mpi-omp.xml), and adapt the configuration to select e.g. the hardware counters to collect, or to enable sampling.
- start from [${EBROOTEXTRAE}/share/example/MPI+OMP/ld-preload/trace.sh](extrae_cfgs/trace_mpi-omp.sh) to set the appropriate values for the environment variable for the target application (e.g. the path to the Extrae config file, the number of threads, and the Extrae library to be used).

*Warning:* Extrae has different libraries different programming models.


## Running a job with Extrae instrumentation using the LD_PRELOAD mechanism
Run your job using a modified command of the type: `srun -N $NNODES -n $NPROC ./trace.sh ./<your_executable`.

A full example of a job script using Extrae for GROMACS can be found here: [ion_channel_2N.extrae_ldpreload.job](batch_scripts/ion_channel_2N.extrae_ldpreload.job).

*Warning:* For this particular example, we get warnings: `Extrae: WARNING! omp_get_thread_num_real is a NULL pointer. Did the initialization of this module trigger? Retrying initialization...`. This does not seem to compromise the trace generation or the execution.

Once the job finishes, 3 files are generated:
```
-rw-r--r-- 1 maximem maximem 372K Dec  5 15:28 gmx_mpi.pcf
-rw-r--r-- 1 maximem maximem  14G Dec  5 15:29 gmx_mpi.prv
-rw-r--r-- 1 maximem maximem 2.0K Dec  5 15:29 gmx_mpi.row
```
These are the merged files that will be read later with paraver.

However here the size of the trace is to large to be viewed with Paraver: the paraver trace file `gmx_mpi.prv` is 14GB.
So it is necessary to either re-run the jobs, limiting the size of the generated trace, or use filters in Paraver to e.g. select only a subpart of the trace or filter out some events.


## Limiting the size of the generated trace

#### Limiting the size of the generated trace with periodicity detection
The [Periodicity detection](https://tools.bsc.es/doc/html/extrae/online.html#periodicity-detection) mechanism of Extrae allows to detect iterative patterns over a wide region of time, and precisely delimit where the iterations start.
The periodicity detection can be enabled when using the [On-line module](https://tools.bsc.es/doc/html/extrae/online.html#configuration) I add the following in the extrae xml configuration file

However, on-line analysis are not enabled in our Extrae modules, as they use `synapse` which is not installed on Lisa and Cartesius.


#### Limiting the size of the generated trace by filtering out events
Start Paraver on your local machine:
```
export PARAVERDIR=~/localinstalls/wxparaver-4.8.1/INSTALLDIR
${PARAVERDIR}/bin/wxparaver &
```
and load the trace: File>Load Trace

When you open a trace with Paraver that is larger than the limit, a dialog opens.
- Choose *Yes* in *Reduce size* dialog,
- click on *Filters*, and use [filter.useful.xml](paraver_cfgs/filter.useful.xml) file,
- Paraver will scan the original trace and generate a new one named after the original plus a ".filter#.prv" extension,
- As directed by `filter_useful.xml`, this file will essentially contain computation burst longer than 5*10^6 ns.

With GROMACS ion_channel example, the filtered trace file `gmx_mpi.filter1.prv` is only 430MB.
However this filters is very drastic, and there is almost nothing left in the filtered trace, notably all MPI events are filtered out

So the filter should be customized to select the relevant events and computation bursts. See [bsc-tuto-6_trace-preparation](bsc-tutorial/bsc-tuto-6_trace-preparation.pdf) for more information.

#### Limiting the size of the generated trace by extracting a representative subtrace

Start Paraver on your local machine:
```
export PARAVERDIR=~/localinstalls/wxparaver-4.8.1/INSTALLDIR
${PARAVERDIR}/bin/wxparaver &
```

When you open a trace with Paraver that is larger than the limit, a dialog opens.
- Choose *Yes* in *Reduce size* dialog,
- click on *new single timeline window* button or load configuration [useful_duration.cfg](../../paraver_cfgs/useful_duration.cfg) to identify when the actual computations started,
- click on the *scissors* icon,
- tick the *1.- Cutter* box, and click on *Select Region...*, then the part of execution trace that you are interested in, e.g. time from *6013738026.599049* to *6923223098.522979*,
- tick *Don't break states* and *Keep boundary events*, then click "Apply".

The default name of the new reduced trace is `gmx_mpi.chop1.prv`.

We then use the trace on this subregion only for the analysis.


## Analysing the trace with Paraver
The `stats` command from Paraver should compute various statistics from the trace, such as inclusive time of routine calls, and output a .dat and a .gnuplot files.
```
${PARAVERDIR}/bin/stats gmx_mpi.prv -o statsfile
```
However it does not generate anything for me... (on my laptop and on Cartesius)
```
$ stats gmx_mpi.chop1.prv -o toto gmx_mpi.chop1.stats
Processing trace 100%
$ ls -lrt
total 5653628
-rw-r--r-- 1 maximem maximem     380828 dec  3 13:27 gmx_mpi.chop1.pcf
-rw-r--r-- 1 maximem maximem       2035 dec  3 13:27 gmx_mpi.chop1.row
-rw-r--r-- 1 maximem maximem 2042859435 dec  3 13:27 gmx_mpi.chop1.prv
```

## Analysing the trace with Paraver GUI
Start Paraver on your local machine:
```
export PARAVERDIR=~/localinstalls/wxparaver-4.8.1/INSTALLDIR
${PARAVERDIR}/bin/wxparaver &
```
and load the trace: File>Load Trace

Then load predefined configuration files to analyse the trace:
- `${PARAVERDIR}/cfgs/mpi/analysis/mpi_stats.cfg` to measure the parallel efficiency
- `${PARAVERDIR}/cfgs/mpi/analysis/2dh_usefulduration.cfg` to measure the computation time distribution

*Warning:* make sure to click on "histogram zoom" button to see the information in the histogram view

*Warning:* in the "trace view", right click>info panel then in Colors the legend should appear (strangely it does not on Cartesius... but it does on my laptop).


##### On Tiny workflow (ion_channel example with only 1000 time steps), the trace that is generated is 1.8GB
We extract a representative subtrace to get rid of the initialization and finalization phases: Folowing the above described instructions, we extract a subtrace based on time from *6013738026.599049* to *6923223098.522979*,

Then we use the trace on this subregion only for the analysis, and we use the methodology described in [bsc-tuto-4_methodology-of-analysis.pdf](../../bsc-tuto-4_methodology-of-analysis.pdf).

1. Load [parallel_efficiency.cfg](../../paraver_cfgs/methodology/parallel_efficiency.cfg) -> [paraver_parallel-efficiency_gromacs-tiny.png](../../captions/paraver_parallel-efficiency_gromacs-tiny.png)
    - The entry “Average” towards the end of the second column tells you how much parallel efficiency you are getting. 100% would be ideal. 90% would mean you are loosing 10% of potential performance.
    - The entry “Maximum” in this same column measures communication efficiency, how much of that performance loss is due due to MPI. A value of 100% means that MPI and communication in general is NOT limiting the application performance. a value of 90% means that you are loosing 10% because of the communication
    - The value at the end of the second column (Avg/Max) actually measures the degree of global load imbalance in the application. A value of one is perfect load balance. A value of 0.9 means you are loosing 10 % of performance with respect to an ideally balanced execution. You can see the distribution of the percentage of useful computation by the different threads in the corresponding
entries of this column.
    - The parallel efficiency is actually the product of these two factors.

2. If the application does show some load imbalance, you may wonder whether it is computational load imbalance or due to other factors. To check the computational load imbalance, load [instructions_profile.cfg](../../paraver_cfgs/methodology/instructions_profile.cfg) -> [paraver_instructions-profile_gromacs-tiny.png](../../captions/paraver_instructions-profile_gromacs-tiny.png)
    - The entry “Avg/Max” at the end of the second column tells you how well is the computational load (number of instructions) balanced across processors. A value of. 1 would represent ideal balance. A value of 0.9 would mean you would be loosing 10% of potential performance if IPC was uniform across all processes due to computational
load imbalance.

3. An important metric to look at reports the performance of the sequential computation phases. If the parallel efficiency is good, this may be the limiting factor. If it is not good, imbalances in IPC may cause the imbalance in execution time. Sometimes, imbalance in IPC may compensate computational load imbalance. Load [IPC_profile.cfg](../../paraver_cfgs/methodology/IPC_profile.cfg) and [IPC_histogram.cfg](../../paraver_cfgs/methodology/IPC_histogram.cfg) -> [paraver_IPC_profile_histogram_gromacs-tiny.png](../../captions/paraver_IPC_profile_histogram_gromacs-tiny.png) [paraver_IPC_profile_trace_gromacs-tiny.png](../../captions/paraver_IPC_profile_trace_gromacs-tiny.png)
    - The second column reports the average IPC achieved by each process in the computation bursts.
    - The entry “Avg/Max” measures the imbalance in IPC. A value of 1 is ideal. a value of 0.9 would mean you would loose 10% of potential performance if the application was perfectly balanced from the computational point of view.

4. If the IPC is not good or well balanced, you may want to look at cache misses.
    - If the communication time seems to be a problem it may actually not be due to communication but to local (or microscopic) load imbalances or serialization.
    - In order to identify this effect, a Dimemas simulation is required.

5. If parallel efficiency is bad due to load imbalance and you want to know how that load imbalance is  distributed and where it shows up: load [computation_duration_histogram.cfg](../../paraver_cfgs/methodology/computation_duration_histogram.cfg) -> [paraver_useful-duration-histogram_gromacs-tiny.png](../../captions/paraver_useful-duration-histogram_gromacs-tiny.png)
    - Ideally, vertical lines should appear, showing that all processes spend take same time for all computation phases.
    - If you pop up the control window you will see the time distribution.
    - If you are interested on a special range of durations where the histogram shows a wide stripe where the duration of a computation phase is different for different processors you may click on the “Open Control Window Zoom 2D” and select the range of durations and processors you are interested. You will get a timeline for only the range of durations and processors you have selected.

See [paraver reference guide](https://tools.bsc.es/doc/html/extrae/xml.html#subsec-processorperformancecounters) for more information about Extrae performance counters.

**Warning:** Some architectures do not allow grouping some performance counters in the same set. On Cartesius Broadwell, there are compatibility problems with PAPI_TOT_CYC which can make getting the IPC metric complicated. With only PAPI_TOT_CYC,PAPI_TOT_INS,PAPI_LD_INS,PAPI_SR_INS we get the IPC.

**Remark:** It could be interesting to get the cache misses too, e.g. PAPI_L1_LDM, PAPI_L1_STM,PAPI_L1_TCM, PAPI_L2_TCM, but they seem incompatible with PAPI_TOT_CYC, so they should be in a different set of counters, and then alternate between the two sets during execution.

**Remark:** sampling can be enable to gather information each time a specified counter reaches a specific value, for example every 100M cycles.


##### Simulating hardware with Dimemas
First convert the trace file to Dimemas format:
```
$ module load 2019
$ module load Dimemas/5.4.1-foss-2018b
$ cd ~/gromacs_testcase/7240432_gromacs_2N_16P_4T_extrae-ldpreload
#
$ prv2dim gmx_mpi.chop2.prv gmx_mpi.chop2.dimemas.dim
```

From the [Dimemas tutorial](https://tools.bsc.es/sites/default/files/documentation/2.introduction_to_dimemas.tar.gz), we can get examples of Dimemas configuration files. Read the `index.pdf` file for Dimemas usage instructions.

Here we use the configuration file to simulate an ideal machine with infinite bandwidth and 0 latency: [ideal.cfg](../../dimemas_cfgs/ideal.cfg).
```
$ Dimemas -p gmx_mpi.chop2.dimemas-ideal.prv ../../dimemas_cfgs/ideal.cfg --dim gmx_mpi.chop2.dimemas.dim
```

Then
- Load [parallel_efficiency.cfg](../../paraver_cfgs/methodology/parallel_efficiency.cfg) on the trace generated with the ideal Dimemas simulation, `gmx_mpi.dimemas-ideal.prv` -> [paraver_parallel-efficiency_gromacs-tiny_ideal-network.png](../../captions/paraver_parallel-efficiency_gromacs-tiny_ideal-network.png)
- The entry “Maximum” in the second column specifies the actual value of Microscopic load balance.
- The actual value of communication efficiency can be computed by dividing the elapsed time of the ideal Dimemas simulation to the elapsed time of the original Paraver trace:  1821121293 ns / 910560646 ns = 2

-> THIS IS WRONG !!! and an impossible value
So I try on the whole trace
```
$ prv2dim gmx_mpi.prv gmx_mpi.dimemas.dim
$ Dimemas -p gmx_mpi.dimemas-ideal.prv ../../dimemas_cfgs/ideal.cfg --dim gmx_mpi.dimemas.dim
-> Simulator configuration to be read ../../dimemas_cfgs/ideal.cfg
-> Loading default random values
-> Loading default scheduler configuration
   * Machine 0. Policy: FIFO
   * Loading default communications configuration
-> Loading initial memory status
-> Loading initial semaphores status
-> Loading default file sytem configuration

0.000000000: START SIMULATION

..10%..   ..20%..   30.000000000: END SIMULATION

**** Application 0 (gmx_mpi.dimemas.dim) ****

**** Total Statistics ****

Execution time:	24.023932089
Speedup:	5.75
CPU Time:	138.070962874
[...]
```
and the time as seen in Paraver is 24023932090 ns. (vs. 11914445761 ns. for the original trace), so it does not make sense either...


#### Instrumenting user functions
It is possible to give a list of functions to be [instrumented](https://tools.bsc.es/doc/html/extrae/xml.html#xml-section-user-functions) by Extrae.
In extrae.xml:
  ```
  <user-functions enabled="no" list="/home/bsc41/bsc41273/user-functions.dat" exclude-automatic-functions="no">
    <counters enabled="yes" />
  </user-functions>    
  ```
The application must first be recompiled with `-finstrument-functions` (for GNU and Intel compilers), then the list of routines must point to a list with the format: ``<HEX_addr>#<F_NAME>``, where ``<HEX_addr>`` refers to the hexadecimal address of the function in the binary file.


#### Sampling
Extrae has time-based [sampling](https://tools.bsc.es/doc/html/extrae/xml.html#xml-section-sampling) capabilities.
Every sample contains processor performance counters (if enabled in section [Processor performance](https://tools.bsc.es/doc/html/extrae/xml.html#subsec-processorperformancecounters) counters and either PAPI or PMAPI are referred at configure time) and callstack information (if enabled in section [XML Section](https://tools.bsc.es/doc/html/extrae/xml.html#sec-xmlsectioncallers): Callers and proper dependencies are set at configure time).
In extrae.xml, sampling can be enabled in the following line:
```
  <sampling enabled="no" type="default" period="50m" variability="10m" />
```

#### Trace analysis with Paramedir
Paramedir packs two sets of features, some that process the trace to compute some data and some that transform the trace, usually to reduce its size.

There are examples of filters and cutters in `${PARAVERDIR}share/filters-config/`.

```
${PARAVERDIR}/bin/paramedir -e -s gmx_mpi.prv ${PARAVERDIR}/cfgs/mpi/analysis/mpi_stats.cfg
```
-> it need a xml file, but I cannot find any doc about what to put in this file...
