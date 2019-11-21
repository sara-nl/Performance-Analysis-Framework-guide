## Introdution to Performance Analysis with the Score-P measurement infrastructure
Scalable Performance Measurement Infrastructure for Parallel Codes

The Score-P measurement infrastructure is a highly scalable and easy-to-use tool suite for profiling, event tracing, and online analysis of HPC applications.

It has been created in the German BMBF project SILC and the US DOE project PRIMA and will be maintained and enhanced in a number of follow-up projects such as LMAC, Score-E, and HOPSA. Score-P is developed under a BSD 3-Clause License and governed by a meritocratic governance model.

Score-P offers the user a maximum of convenience by supporting a number of analysis tools. Currently, it works with Periscope, Scalasca, Vampir, and Tau and is open for other tools. Score-P comes together with the new Open Trace Format Version 2, the Cube4 profiling format and the Opari2 instrumenter.

Score-P is available under the New BSD Open Source license.

Reference : <https://www.vi-hps.org/projects/score-p/>

## Main components of the Score-P measurement infrastructure and compatible performance tools

- **Score-P Instrumentation and Run-Time Measurement:** Score-P is the central component and incorporates all other components. It contains the code instrumentation functionality supporting various methods and it performs the run-time data collection in the parallel environment. <http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/docs/scorep-6.0/html/>
- **OTF2 - The Open Trace Format Version 2:** The Open Trace Format 2 is a highly scalable, memory efficient event trace data format plus support library. It will become the new standard trace format for Scalasca, Vampir, and Tau and is open for other tools. <http://scorepci.pages.jsc.fz-juelich.de/otf2-pipelines/docs/otf2-2.2/html/>
- **Cube 4 Profiling Data Format** and **Cube GUI:** Cube4 is a highly scalable, memory efficient, flexible profile format with support libraries, a set of tools and a GUI. Cube is a generic tool for displaying a multi-dimensional performance space consisting of the dimensions (i) performance metric, (ii) call path, and (iii) system resource. <https://www.scalasca.org/software/cube-4.x/download.html>
- **OPARI2 OpenMP instrumenter:** OPARI2 is a source-to-source instrumentation tool for OpenMP and hybrid codes. It surrounds OpenMP directives and runtime library calls with calls to the POMP2 measurement interface. <http://scorepci.pages.jsc.fz-juelich.de/opari2-pipelines/docs/opari2-2.0.5/html/>
- **Scalasca Trace Tools:** The Scalasca Trace Tools developed at the Jülich Supercomputing Centre are a collection of trace-based performance analysis tools that have been specifically designed for use on large-scale systems featuring hundreds of thousands of CPU cores, but also suitable for smaller HPC platforms. The current focus is on applications using MPI OpenMP, POSIX threads, or hybrid MPI+OpenMP/Pthreads parallelization; support for other parallel programming paradigms may be added in the future. A distinctive feature of the Scalasca Trace Tools is its scalable automatic trace-analysis component which provides the ability to identify wait states that occur, for example, as a result of unevenly distributed workloads. <https://apps.fz-juelich.de/scalasca/releases/scalasca/2.5/docs/manual/>
- **Extra-P:** Extra-P is an automatic performance-modeling tool that supports the user in the identification of scalability bugs. A scalability bug is a part of the program whose scaling behavior is unintentionally poor, that is, much worse than expected. <https://www.scalasca.org/scalasca/software/extra-p/download.html>

## Available modules on Cartesius and Lisa
In the `2019` software stack, Easybuild-based  modules are available: `Score-P/5.0-foss-2018b` and `Score-P/5.0-intel-2018b`.

## Usage on Cartesius
The general workflow for a full Score-P analysis is the following:
1 - **Reference run** and note the runtime.
2 - **Preparation:** instrument target application and set up the measurement environment.
3 - **Profiling run with full instrumentation:** run application with measurement infrastructure enabled.
4 - **Comparison with reference runtime:** compare runtime with the reference runtime to determine the overhead. If the overhead is too high, create a filter file using hints from scorep-score and generate an optimized profile with the filter applied.
5 - **Analysis of generated performance data:** investigate the profile with Cube.
6 - **Preparation of run with tracing:** define (or adjust) the filter file for a tracing run using scorep-score.
7 - **Run with tracing enabled:** Generate a trace with filter applied
8 - **Analysis of generated trace:** Perform in-depth analysis on the trace data with a trace viewer (Vampir, ViTE, ???)

## Full example with gromacs

#### 1 - Reference run
Start from a clean local install:
```
# login on Cartesius
ssh <username>@cartesius.surfsara.nl
# download gromacs
wget http://ftp.gromacs.org/pub/gromacs/gromacs-2019.3.tar.gz
tar xzf gromacs-2019.3.tar.gz
# load modules
cd gromacs-2019.3/
module load 2019
module load foss/2018b
module load CMake/3.12.1-GCCcore-7.3.0

mkdir build
mkdir install
cd build
# build parallel executable gmx_mpi with RelWithDebInfo - optimized for broadwell architecture
# configure
cmake \
    -DCMAKE_INSTALL_PREFIX=$PWD/../install \
    -DCMAKE_SKIP_RPATH=ON \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DGMX_PREFER_STATIC_LIBS=ON \
    -DBUILD_SHARED_LIBS=off \
    -DGMX_EXTERNAL_BLAS=ON \
    -DGMX_BLAS_USER=$EBROOTOPENBLAS/lib/libopenblas.a \
    -DGMX_EXTERNAL_LAPACK=ON \
    -DGMX_LAPACK_USER=$EBROOTOPENBLAS/lib/libopenblas.a \
    -DGMX_BUILD_OWN_FFTW=off \
    -DGMX_FFT_LIBRARY=fftw3 \
    -DGMX_SIMD=AVX2_256 \
    -DCMAKE_C_COMPILER=`which mpicc` \
    -DCMAKE_CXX_COMPILER=`which mpicxx` \
    -DGMX_DOUBLE=off \
    -DGMX_GPU=off \
    -DGMX_MPI=ON \
    -DGMX_THREAD_MPI=OFF \
    -DGMX_OPENMP=on \
    -DGMX_X11=off \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_CXX_FLAGS='-march=broadwell' \
    -DCMAKE_C_FLAGS='-march=broadwell' \
    -DCMAKE_EXE_LINKER_FLAGS='-lgfortran' \
        .. > config.log
# build
make -j24 &> make_24.log
# install
make install &> make_install.log
```
and do a reference run with the test case A from the PRACE Benchmarking Suite (UEABS) and EPI Benchmarking Suite: `ion_channel`.
```
cd
mkdir gromacs_testcase
cd gromacs_testcase
wget https://repository.prace-ri.eu/ueabs/GROMACS/1.2/GROMACS_TestCaseA.tar.gz
tar xzf GROMACS_TestCaseA.tar.gz
```
Download [ion_channel_2N.reference.job](batch_scripts/ion_channel_2N.reference.job) and run the testcase:
```
sbatch ion_channel_reference_run_2N.job
```

##### 2 - Preparation
Build using the `scorep` compiler wrapper to instrument the target application. All other configure options remain identical.
```
# load Score-P module in addition to the previously loaded modules
module load Score-P/5.0-foss-2018b
#
cd ~/gromacs-2019.3/
mkdir build_scorep
mkdir install_scorep
cd build_scorep
# build parallel executable gmx_mpi with RelWithDebInfo - optimized for broadwell architecture
# configure
cmake \
    -DCMAKE_INSTALL_PREFIX=$PWD/../install_scorep \
    -DCMAKE_SKIP_RPATH=ON \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DGMX_PREFER_STATIC_LIBS=ON \
    -DBUILD_SHARED_LIBS=off \
    -DGMX_EXTERNAL_BLAS=ON \
    -DGMX_BLAS_USER=$EBROOTOPENBLAS/lib/libopenblas.a \
    -DGMX_EXTERNAL_LAPACK=ON \
    -DGMX_LAPACK_USER=$EBROOTOPENBLAS/lib/libopenblas.a \
    -DGMX_BUILD_OWN_FFTW=off \
    -DGMX_FFT_LIBRARY=fftw3 \
    -DGMX_SIMD=AVX2_256 \
    -DCMAKE_C_COMPILER=scorep-mpicc \
    -DCMAKE_CXX_COMPILER=scorep-mpicxx \
    -DGMX_DOUBLE=off \
    -DGMX_GPU=off \
    -DGMX_MPI=ON \
    -DGMX_THREAD_MPI=OFF \
    -DGMX_OPENMP=on \
    -DGMX_X11=off \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_CXX_FLAGS='-march=broadwell' \
    -DCMAKE_C_FLAGS='-march=broadwell' \
    -DCMAKE_EXE_LINKER_FLAGS='-lgfortran' \
        .. > config.log
# build
make -j24 &> make_24.log
# install
make install &> make_install.log
```

#### 3 - Profiling run
Run the `ion_channel` test case with the instrumented version of gromacs and profiling enabled.
Set up the measurement environment in the batch script, e.g. to use PAPI metrics (choose PAPI metrics from the list obtained with `papi_avail` on the corresponding hardware):
```
export SCORE_ENABLEP_PROFILING=true
export SCOREP_METRIC_PAPI_METRICS="PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_SP_OPS,PAPI_DP_OPS,PAPI_VEC_SP,PAPI_VEC_DP"
```
Download [ion_channel_2N.scorep_profiling.job](batch_scripts/ion_channel_2N.scorep_profiling.job) and run the testcase:
```
cd ~/gromacs_testcase
sbatch ion_channel_scorep_profiling_run_2N.job
```

#### 4 - Comparison with reference runtime
Compare runtime with the reference runtime to determine the overhead. If the overhead is too high, create a filter file using hints from scorep-score and generate an optimized profile with the filter applied.

Gromacs prints the runtime to the standard output at the end of the execution.

For the reference run, we get (WARNING: Broadwell nodes were too busy, so I used Haswell nodes instead with 2 nodes / 12 MPI processes per node / 4 OpenMP threads per process):
```
               Core t (s)   Wall t (s)        (%)
       Time:     1308.425       27.284     4795.6
                 (ns/day)    (hour/ns)
Performance:       39.592        0.606
```

For the profiling run with Score-P, we get:
```
               Core t (s)   Wall t (s)        (%)
       Time:    43454.774      905.327     4799.9
                 (ns/day)    (hour/ns)
Performance:        1.193       20.118
```

The overhead of Score-P is very high. This is to be expected as Score-P does instrumentation-based profiling, but we can try to reduce the overhead.

Use `scorep-score` to identify the parts causing the overhead, and to get an estimation of the memory requirements for a tracing run.
Regions that are visited a lot with a low execution time can induce a large measurement overhead.
```
$ scorep-score 7162687_gromacs_2N_12P_4T_scorep_profiling/7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/profile.cubex -r
```
```
Estimated aggregate size of event trace:                   196GB
Estimated requirements for largest trace buffer (max_buf): 21GB
Estimated memory requirements (SCOREP_TOTAL_MEMORY):       21GB
(warning: The memory requirements cannot be satisfied by Score-P to avoid
 intermediate flushes when tracing. Set SCOREP_TOTAL_MEMORY=4G to get the
 maximum supported memory or reduce requirements using USR regions filters.)

flt     type     max_buf[B]        visits  time[s] time[%] time/visit[us]  region
         ALL 21,872,117,716 8,135,823,432 83580.19   100.0          10.27  ALL
         USR 21,674,071,211 8,078,671,009 79599.83    95.2           9.85  USR
         OMP    140,107,854    40,240,780  2644.36     3.2          65.71  OMP
         MPI     31,111,579     4,150,042   894.22     1.1         215.47  MPI
         COM     27,673,884    12,761,589   441.69     0.5          34.61  COM
      SCOREP             96            12     0.09     0.0        7818.95  SCOREP

         USR  5,151,192,300 2,402,499,895   214.58     0.3           0.09  T gmx::square(T) [with T = float]
         USR  3,414,117,850   865,821,331    71.05     0.1           0.08  int pbc_dx_aiuc(const t_pbc*, const real*, const real*, real*)
         USR  3,057,697,344   775,617,990   108.24     0.1           0.14  int pbc_rvec_sub(const t_pbc*, const real*, const real*, real*)
         USR  2,087,641,426   837,720,431   141.74     0.2           0.17  float subc_bb_dist2_simd4(int, const nbnxn_bb_t*, int, gmx::ArrayRef<const nbnxn_bb_t>)
         USR    742,573,208   331,242,962    27.10     0.0           0.08  unsigned int get_imask_simd_j8(gmx_bool, int, int)
         USR    737,332,856   333,852,571    28.44     0.0           0.09  void check_cell_list_space
[...]
```
It is possible to define filters to include/exclude regions (or files) to try an limit the overhead and the trace size.
Regions with a lot of visits but a low time percentage are good candidates for exclusion. Another solution is to include only regions with a high time percentage.

Use for example file [scorep-gromacs.filt](scorep-filters/scorep-gromacs.filt), or use the scripts [write_scorep_filter_include.py](scorep-filters/write_scorep_filter_include.py) and [write_scorep_filter_exclude.py](scorep-filters/write_scorep_filter_exclude.py) to filter automatically based on some carefully chosen parameters:
```
scorep-score 7162687_gromacs_2N_12P_4T_scorep_profiling/7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/profile.cubex -r > scorep-score-gromacs.out
python write_scorep_filter_include.py scorep-score-gromacs.out 0.1 1000000 1 scorep-gromacs.filt 1 1
```

Then see the effect of the filter on the size of the output and adjust the filter if needed:
```
$ scorep-score -f scorep-gromacs.filt  7162687_gromacs_2N_12P_4T_scorep_profiling/7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/profile.cubex

Estimated aggregate size of event trace:                   2569MB
Estimated requirements for largest trace buffer (max_buf): 216MB
Estimated memory requirements (SCOREP_TOTAL_MEMORY):       224MB
(hint: When tracing set SCOREP_TOTAL_MEMORY=224MB to avoid intermediate flushes
 or reduce requirements using USR regions filters.)

flt     type     max_buf[B]        visits  time[s] time[%] time/visit[us]  region
 -       ALL 21,872,117,716 8,135,823,432 83580.19   100.0          10.27  ALL
 -       USR 21,674,071,211 8,078,671,009 79599.83    95.2           9.85  USR
 -       OMP    140,107,854    40,240,780  2644.36     3.2          65.71  OMP
 -       MPI     31,111,579     4,150,042   894.22     1.1         215.47  MPI
 -       COM     27,673,884    12,761,589   441.69     0.5          34.61  COM
 -    SCOREP             96            12     0.09     0.0        7818.95  SCOREP

 *       ALL    226,006,147    69,723,880 81848.58    97.9        1173.90  ALL-FLT
 +       FLT 21,646,945,907 8,066,099,552  1731.61     2.1           0.21  FLT
 -       OMP    140,107,854    40,240,780  2644.36     3.2          65.71  OMP-FLT
 -       MPI     31,111,579     4,150,042   894.22     1.1         215.47  MPI-FLT
 *       COM     27,673,884    12,761,589   441.69     0.5          34.61  COM-FLT
 *       USR     27,128,554    12,571,457 77868.23    93.2        6194.05  USR-FLT
 -    SCOREP             96            12     0.09     0.0        7818.95  SCOREP-FLT
```

And finally do the profiling run with Score-P using the filter. (use e.g. [ion_channel_2N.scorep_profiling_filter.job](batch_scripts/ion_channel_2N.scorep_profiling_filter.job)).
In this case we still have a large overhead, but the size of the trace will be more reasonable.

#### 4 bis: selective recording
c.f. http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/docs/scorep-6.0/html/measurement.html

There are 2 options:
1. Manual Region Instrumentation in the source code (http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/docs/scorep-6.0/html/instrumentation.html#manual_instrumentation)
2. Specify recorded regions via a configuration file.

Here we specify recorded regions via a configuration file
We restrict the score-p profiling and tracing to a few time steps, after the reset.

Define a selective recording configuration file [scorep-selective-recording.configuration](scorep-filters/scorep-selective-recording.configuration)
```
gmx_mdrun 600:604
```
And we set the environment variable `SCOREP_SELECTIVE_CONFIG_FILE=scorep-selective-recording.configuration`.

**Remark:** `gmx_mdrun` is called much more than once per time step... Where is the time loop ?
  And the selective recording does not seem to work with just this...


*TODO:* MAKE IT WORK !!!!


#### 5 - Analysis of generated performance data
On Cartesius, we only managed to build CubeGUI with foss, so please use module `CubeGUI/4.4.3-foss-2018b`.
To forward X11 client over ssh and thus allow display, you have to connect to Cartesius using the `-X` flag: `ssh -X <login>@cartesius.surfsara.nl`.

Alternatively, build CubeGUI on your local machine, copy the performance data generated by Score-P to you local machine and open them with cube. This is the recommended workflow.

```
$ scp -r cartesius:~/gromacs_testcase/7162687_gromacs_2N_12P_4T_scorep_profiling/7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/ .scorep.cfg                                                         100% 1738   135.2KB/s   00:00    
MANIFEST.md                                                        100%  717    72.9KB/s   00:00    
profile.cubex                                                      100% 8675KB  89.9MB/s   00:00   
$ cube 7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/profile.cubex &
```

*TODO:* ADD SCREENSHOTS




#### 6 - Preparation of run with tracing
It is usually necessary to use a filter file for a tracing run in order to keep the size of the recorded trace manageable.
Then starting from the setup used for profiling, we only need to enable tracing and set the total memory allocated for Score-P:
```
SCOREP_ENABLE_TRACING=true
SCOREP_TOTAL_MEMORY=1GB
```


#### 7 - Run with tracing enabled
Then using [ion_channel_2N.scorep_tracing.job](batch_scripts/ion_channel_2N.scorep_tracing.job) with an adequate filter, we run the `ion_channel` testcase again to collect the execution trace.
On Cartesius Haswell, this takes the same time as a profiling run with Score-P:
```
Core t (s)   Wall t (s)        (%)
Time:    43624.972      908.922     4799.6
  (ns/day)    (hour/ns)
Performance:        1.210       19.841
```
and generates, in addition to the Score-P profile, a folder `traces` and files `traces.def` and `traces.otf2`.
Here the `traces` folder has a size of 2.2GB.


#### 8 - Analysis of generated trace
First perform an automated trace analysis with Scalasca and/or Casita.
```
$ module load Scalasca/2.5-foss-2018b
$ square -s 7213021_gromacs_2N_12P_4T_scorep_tracing/7213021_gromacs_ion_channel_2N_12P_4T_scorep_tracing/
INFO: Post-processing runtime summarization report (profile.cubex)...
/sw/arch/RedHatEnterpriseServer7/EB_production/2019/software/Score-P/5.0-foss-2018b/bin/scorep-score -r ././profile.cubex > ././scorep.score
INFO: Score report written to ././scorep.score
```

With `square -s`, Scalasca post-processes the output generates
When provided with a Score-P experiment directory, here `7213021_gromacs_2N_12P_4T_scorep_tracing/7213021_gromacs_ion_channel_2N_12P_4T_scorep_tracing/`, `square` post-processes intermediate analysis reports produced by a measurement and/or an automatic trace analysis to derive additional metrics and construct a hierarchy of measured and derived metrics.
One can view this final report using the Cube GUI.

When running `square` without the `-s` flag, then Cube-Gui is autonatically started to view the final report once the post-processing is done.

-> either way give the same result.
*WARNING:* I don't see the critical path analysis, or the late sender/late receiver, etc.
           Should I run gromacs with scan ? (i.e. directly using Scalasca, rather than with Score-P with a subsequent Scalasca analysis)


Alternatively, we can use Casita to perform an automated trace analysis.
-> IS IT BETTER THAN SCALASCA ? IF NOT, WE DO NOT USE IT.


Then perform in-depth analysis on the trace data with a trace viewer (Vampir, ViTE, ???)


#### 9 - Automatic calculation of POP-Coe metrics using Cube-4.5 release preview
