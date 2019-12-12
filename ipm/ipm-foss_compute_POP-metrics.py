#!/usr/bin/python
#
# Usage: python ipm-foss_compute_POP-metrics.py job_ipm_foss.out
# read IPMv2.0.6-foss output from a job output files (job_ipm_foss.out)
# and compute POP metrics
#
# Usage2: python ipm-foss_compute_POP-metrics.py job_ipm_foss.out reference_metrics.txt
# read IPMv2.0.6-foss output from a job output files (job_ipm_foss.out)
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

for line in lines:
  i=i+1
  if line == '##IPMv2.0.6########################################################\n':
    first_ipm_line=i
  elif line == '###################################################################\n' and first_ipm_line!=0:
    last_ipm_line=i
  elif first_ipm_line!=0 and last_ipm_line==0 and line[0]=='#':
    ipm_output.append(line)
    
#print(ipm_output)


# get nb_processes and nb_nodes
nb_processes=0
nb_nodes=0
for ipm_line in ipm_output:
  words=ipm_line.split()
  if len(words)>1 and words[1]=='mpi_tasks':
    nb_processes=int(words[3])
    nb_nodes=int(words[5])
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
for ipm_line in ipm_output:
  words=ipm_line.split()
  if len(words)>1 and words[1]=='wallclock':
    max_wallclock=float(words[6])
    # with IPM-foss there is no 'user' and 'system' lines, so I use the 'wallclock' line instead
    total_user=float(words[3])
    avg_user=float(words[4])
    max_user=float(words[6])
  elif len(words)==7 and words[1]=='MPI' and avg_mpi==-1:
    avg_mpi=float(words[4])
    min_mpi=float(words[5])
    max_mpi=float(words[6])
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
communication_efficiency=(max_user-min_mpi)/max_wallclock
parallel_efficiency=load_balance*communication_efficiency

# these metrics are meant to compare a benchmark with different core counts
#computational_efficiency=reference_total_user/total_user
#global_efficiency=computational_efficiency*parallel_efficiency
#print("computational_efficiency: ", computational_efficiency)
#print("global_efficiency: ", global_efficiency)

print "load_balance: ", load_balance
print "communication_efficiency: ", communication_efficiency
print "parallel_efficiency: ", parallel_efficiency

file.close()   
