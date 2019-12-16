#include <iostream>
#include <mpi.h>
#include <utmpx.h>
using namespace std;

void parallelinit( int** localA, int* localb, int* localc, int size, int localsize )
{
  int id;
  MPI_Comm_rank(MPI_COMM_WORLD, &id);
  for ( int i = 0; i < localsize; ++i )
  {
    for ( int j = 0; j < size; ++j )
    {
        localA[i][j] = j+localsize*id+i;
    }
  }
  for ( int i = 0; i < size; ++i )
  {
        localb[i] = 1;
  }
}

void parallelmatvec( int** A, int* b, int* c, int size, int localsize )
{
    int id;
    int nproc;
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &nproc);
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int processor_name_len;
    MPI_Get_processor_name(processor_name, &processor_name_len);
    std::cout << "Hello from P" << id << " / " << nproc << " - hostname " << processor_name << " - cpu = " << sched_getcpu() << std::endl;
    for ( int i = 0; i < localsize; ++i )
    {
        c[i] = 0;
    }
    for ( int i = 0; i < localsize; ++i )
    {
        for ( int j = 0; j < size; ++j )
        {
            c[i] += A[i][j]*b[j];
        }
    }
}

int main(int argc, char ** argv) {
  double t1, t2;
  int nproc, id;
  int n = 12048;
  int* c = new int[n];
  // init MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &nproc); // get totalnodes
  MPI_Comm_rank(MPI_COMM_WORLD, &id);
  int nlocal = n/nproc;
  int** localA = new int*[nlocal];
  for ( int i = 0; i < nlocal; ++i )
  {
    localA[i] = new int[n];
  }
  int* localb = new int[n];
  int* localc = new int[nlocal];
  if ( nlocal*nproc != n )
  {
    std::cerr << "ERROR: totalsize of the matrix " << n << " is not a multiple of the number of processes !" << std::endl;
    //    exit(0);
  }
  int* displs = new int[nproc];
  int* recvcnts = new int[nproc];
  displs[0] = 0;
  recvcnts[0]=nlocal;
  for ( int i=1; i<nproc; ++i )
  {
    displs[i] = displs[i-1]+nlocal;
    recvcnts[i]=nlocal;
  }
  if (id == 0) {
    t1 = MPI_Wtime();
  }
  // init A and b
  parallelinit(localA, localb, localc, n, nlocal);
  // compute
  parallelmatvec(localA, localb, localc, n, nlocal);
  MPI_Gatherv( localc, nlocal, MPI_INT, c, recvcnts, displs, MPI_INT, 0, MPI_COMM_WORLD);

  MPI_Barrier(MPI_COMM_WORLD);
  if (id == 0) {
    t2 = MPI_Wtime();
    std::cout << "time elapsed: " << (t2 - t1) << endl;
  }

  delete[] recvcnts;
  delete[] displs;
  delete[] localb;
  delete[] localc;
  for ( int i = 0; i < nlocal; ++i )
  {
    delete[] localA[i];
  }
  delete[] localA;
  MPI_Finalize();
  // delete global var
  delete[] c;

  return 0;
}
