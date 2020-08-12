#!/usr/bin/python
#
# Usage: python ipm-intel_compute_POP-metrics.py prof.dat
# read intel IPM output from an ipm output file (prof.dat)
# and compute POP metrics
#
# Usage2: python ipm-intel_compute_POP-metrics.py prof.dat reference_metrics.txt
# read intel IPM output from an ipm output file (prof.dat)
# compute POP metrics, and compute metrics relative to reference run
#
import sys
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

file = open(str(sys.argv[1]), 'r')
i = 0
first_ipm_line=0
last_ipm_line=0
lines = file.readlines()
ipm_output=[]

# get nb_processes and nb_nodes
nb_processes=0
nb_nodes=0
for ipm_line in lines:
  words=ipm_line.split()
  if len(words)>4 and words[4]=='mpi_tasks':
    nb_processes=int(words[6])
    nb_nodes=int(words[8])
print nb_processes, "MPI processes on ",nb_nodes , " nodes"
# declare interesting values to extracts
max_wallclock=0
total_user=0
avg_user=0
max_user=0
avg_mpi=-1
min_mpi=0
max_mpi=0
# declare pop metrics
load_balance=0
communication_efficiency=0
parallel_efficiency=0

# extract values from ipm output
for ipm_line in lines:
  words=ipm_line.split()
  if len(words)>1 and words[1]=='wallclock':
    max_wallclock=float(words[5])
  elif len(words)>1 and words[1]=='user':
    total_user=float(words[2])
    avg_user=float(words[3])
    max_user=float(words[5])
  elif len(words)>1 and words[1]=='mpi':
    avg_mpi=float(words[3])
    min_mpi=float(words[4])
    max_mpi=float(words[5])
    exit

print "max_wallclock: ", max_wallclock
print "total_user: ", total_user
print "avg_user: ", avg_user
print "max_user: ", max_user
print "avg_mpi: ", avg_mpi
print "min_mpi: ", min_mpi
print "max_mpi: ", max_mpi
# compute pop metrics
load_balance=(avg_user-avg_mpi)/(max_user-min_mpi)
communication_efficiency=(max_user-min_mpi)/max_wallclock     # WARNING: this just gives an upper bound on the communication efficiency, the definition is "CommE = maximum computation time / total runtime"
parallel_efficiency=load_balance*communication_efficiency     # Since the communication efficiency is overestimated, the parallel_efficiency is overestimated too

# print pop metrics
print "load_balance: ", load_balance
print "communication_efficiency: ", communication_efficiency
print "parallel_efficiency: ", parallel_efficiency

# close file
file.close()  

# compute metrics relative to reference run
# this is meant to compare a benchmark run with different core counts
if len(sys.argv)==3:  # this means we pass a file with the metrics for the 'reference' run
  ref_file = open(str(sys.argv[2]), 'r')
  ref_nb_processes=0
  ref_nb_nodes=0
  ref_total_user=0
  ref_max_user=0
  ref_load_balance=0
  ref_communication_efficiency=0
  ref_parallel_efficiency=0
  lines = ref_file.readlines()
  for line in lines:
    words=line.split()
    if len(words)>2 and words[2]=='processes':
      ref_nb_processes=int(words[0])
      ref_nb_nodes=int(words[4])
    elif len(words)>0 and words[0]=='total_user:':
      ref_total_user=float(words[1])
    elif len(words)>0 and words[0]=='max_user:':
      ref_max_user=float(words[1])
    elif len(words)>0 and words[0]=='load_balance:':
      ref_load_balance=float(words[1])
    elif len(words)>0 and words[0]=='communication_efficiency:':
      ref_communication_efficiency=float(words[1])
    elif len(words)>0 and words[0]=='parallel_efficiency:':
      ref_parallel_efficiency=float(words[1])
      
  print ""
  print "# metrics for reference run with ", ref_nb_processes, " on ", ref_nb_nodes, " nodes"
  print "ref_load_balance: ", ref_load_balance
  print "ref_communication_efficiency: ", ref_communication_efficiency
  print "ref_parallel_efficiency: ", ref_parallel_efficiency

  computation_efficiency=ref_total_user/total_user
  global_efficiency=computation_efficiency*parallel_efficiency
  print ""
  print "# metrics compared to reference run:"
  print "computation_efficiency: ", computation_efficiency
  print "global_efficiency: ", global_efficiency

  ref_file.close()  

 
