## Introdution to TAU 

TAU (Tuning and Analysis Utility) is profiling tool for performance analysis of programs written in C, C++, Java and Python couple with MPI and OpenMP. TAU maintains performance data of each thread, context and node in use by an application. TAU supports dynamic instrumentation (automatic ), source code and compiler instrumentation (manual )based on PDT (Program DataBase Toolkit). 

TAU's visualization tool, paraprof, provides graphical displays of all the performance analysis results, in aggregate and single node/context/thread forms. The user can quickly identify sources of performance bottlenecks in the application using the graphical interface. In addition, TAU can generate event traces that can be displayed with the Vampir or Paraver trace visualization tools

Reference : <https://www.cs.uoregon.edu/research/tau/tau-referenceguide.pdf>

### Compilation

TAU compilation is a different process for each kind of profiling and it also depends on application to profile. Below are some example as a guide for compilation process. For more details please  

##### Download the source code. 

1. Download TAU from <https://www.cs.uoregon.edu/research/tau/downloads.php>
2. cd /path/to/TAU
3. mkdir build

##### Software Environment (Basic)

1. MPI : **OpenMPI/3.1.1-GCC-7.3.0-2.30**
2. PAPI (Performance API) : **PAPI/5.7.0-GCCcore-7.3.0**
3. PDT (Program DataBase Toolkit) : **PDT/3.25-foss-2018b**
4. CMake (>= 3.12) : **CMake/3.12.1-GCCcore-7.3.0**

*Diagram to come here to explain TAU working*

##### Preparing TAU compilation for MPI + OpenMP analysis

`./configure -prefix=/home/<path to>/tau-2.28.2/build -mpi -ompt=download -papi=$EBROOTPAPI -pdt=$EBROOTPDT`

`make -j 12`

[![asciicast](https://asciinema.org/a/1peXkVDvSfPjI0HvFjFENSMiW.svg)](https://asciinema.org/a/1peXkVDvSfPjI0HvFjFENSMiW)
 
##### Preparing TAU compilation for MPI + OpenMP + CUDA analysis

##### Preparing TAU compilation for MPI + OpenMP + CUDA + Python analysis 

### Benchmark Applications

#### Install paraprof on your laptop 

Instructions : <https://www.cs.uoregon.edu/research/tau/downloads.php>

###### Benchmark application for MPI + OpenMP : Gromacs (CPU only)
###### Benchmark application for MPI + OpenMP + CUDA : Gromacs (CPU + GPU)
###### Benchmark application for MPI + OpenMP + CUDA + Python : Tensorflow with Horovod + MPI with CUDA support 




