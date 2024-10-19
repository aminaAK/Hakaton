#include "mpi.h"
#include <math.h>
#include <stdio.h>
#include <unistd.h>
int main(int argc, char **argv)
{
  int rank, size,j ,i;
  double  time_start, time_finish;
  MPI_Init(&argc,&argv);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  int N =10000;
  int buf[N];
  char name[MPI_MAX_PROCESSOR_NAME];
  int len;
  MPI_Get_processor_name(name, &len);
  i = rank;
  time_start = MPI_Wtime();
  MPI_Send(buf, N, MPI_INT, (i-1+size)%size, 0, MPI_COMM_WORLD);
  MPI_Send(buf, N, MPI_INT, (i+1)%size, 0, MPI_COMM_WORLD);
  MPI_Recv(buf, N, MPI_INT, (i-1+size)%size, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  MPI_Recv(buf, N, MPI_INT, (i+1)%size, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
  time_finish = MPI_Wtime();
  printf("%lf\n",(time_finish - time_start)/2);
  MPI_Finalize();
  return 0;
}