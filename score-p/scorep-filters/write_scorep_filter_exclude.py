# writes a scorep filter file <scorep_filter_file> to exclude all regions with execution time less than <min_time_percentage>
# using <include_all_OMP> and <include_all_COM> one can include all OpenMP or Communication regions
#
# Usage: python write_scorep_filter_exclude.py <scorep-score_file> <min_time_percentage> <scorep_filter_file> <include_all_OMP> <include_all_COM>
# example: python write_scorep_filter_exclude.py toto.log 0.3 toto.filt 1 1
# params:
#   scorep-score_file = IN the output of the 'scorep-score -r' command
#   min_time_percentage = IN minimum percentage of execution time required to include the function (if the other conditions are met)
#   scorep_filter_file = OUT scorep filter file
#   include_all_OMP = include all regions of type OMP even if time percentage is lower than min_time_percentage - value can be 0 (no) or 1 (yes)
#   include_all_COM = include all regions of type COM even if time percentage is lower than min_time_percentage - value can be 0 (no) or 1 (yes)

import sys

print(sys.argv)

fp_filter = open(sys.argv[3], 'w+')
fp_filter.write("SCOREP_REGION_NAMES_BEGIN\n")
fp_filter.write("  EXCLUDE\n")

# include regions COM and OMP ?

fp_score = open(sys.argv[1], 'r')
linecount=0

min_time_percentage=float(sys.argv[2])
include_all_OMP=int(sys.argv[4])
include_all_COM=int(sys.argv[5])
print "min_time_percentage = ", min_time_percentage
print "include_all_OMP = ", include_all_OMP
print "include_all_COM = ", include_all_COM

while True:
  line = fp_score.readline()
  # If line is empty then end of file reached
  if not line :
      break;
  linecount = linecount + 1
  # we ignore the 16 first lines as they contain information about the whole trace/profile and regions
  # but not detailed information about a given function
  if linecount > 16:
    words=line.split(None,6)
    nb_visits_str = words[2]
    nb_visits = int(nb_visits_str.replace(',',''))
    time_percentage = float(words[4])
    region_type = words[0]
    if (time_percentage < min_time_percentage):
      if (include_all_OMP==1 and region_type=="OMP") or (include_all_COM==1 and region_type=="COM")  :
        print "including ", words[6], " because its type is ", region_type
      else:
        function_prototype = words[6]
        tmp1 = function_prototype.split('(',2)
        tmp2 = tmp1[0]
        tmp_name_words = tmp2.split()
        function_name = tmp_name_words[len(tmp_name_words)-1]
        fp_filter.write("    *%s*\n" % function_name)
fp_score.close()
fp_filter.write("SCOREP_REGION_NAMES_END\n")
fp_filter.close()
