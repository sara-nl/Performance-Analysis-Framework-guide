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
Download [ion_channel_reference_run_2N.job](batch_scripts/ion_channel_reference_run_2N.job) and run the testcase:
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
export SCOREP_PROFILING=true
export PAPI_METRICS="PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_REF_CYC,PAPI_SP_OPS,PAPI_DP_OPS,PAPI_VEC_SP,PAPI_VEC_DP"
```
Download [ion_channel_scorep_profiling_run_2N.job](batch_scripts/ion_channel_scorep_profiling_run_2N.job) and run the testcase:
```
cd ~/gromacs_testcase
sbatch ion_channel_scorep_profiling_run_2N.job
```
```
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

The overhead of Score-P is very high, so we need to use a filter to generate a more adequate profile.

Use `scorep-score` to identify the parts causing the overhead.
```
scorep-score 7162687_gromacs_ion_channel_2N_12P_4T_scorep_profiling/profile.cubex
```
Then use a filter to exclude the functions with a lot of visits but a low time percentage.






#### 5 - Analysis of generated performance data
On Cartesius, we only managed to build CubeGUI with foss, so please use module `CubeGUI/4.4.3-foss-2018b`.
Alternatively, build CubeGUI on your local machine (recommended).

#### 6 - Preparation of run with tracing
define (or adjust) the filter file for a tracing run using scorep-score.

#### 7 - Run with tracing enabled
Generate a trace with filter applied

#### 8 - Analysis of generated trace
Perform in-depth analysis on the trace data with a trace viewer (Vampir, ViTE, ???
