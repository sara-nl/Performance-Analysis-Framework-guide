# Usage: python write_scorep_filter.py <scorep-score_file> <min_time_percentage> <max_visits> <sufficient_time_percentage> <scorep_filter_file>
# example: python write_scorep_filter.py toto.log 0.1 1000000 1 toto.filt
# params:
#   scorep-score_file = IN the output of the 'scorep-score -r' command
#   min_time_percentage = IN minimum percentage of execution time required to include the function (if the other conditions are met)
#   max_visits = IN maximum number of visits of the function to include the function (if the other conditions are met)
#   sufficient_time_percentage = IN minimum  percentage of execution time required to include the function even if the other conditions are not met
#   scorep_filter_file = OUT scorep filter file

import sys

print(sys.argv)

fp_filter = open(sys.argv[5], 'w+')
fp_filter.write("SCOREP_REGION_NAMES_BEGIN\n")
fp_filter.write("  EXCLUDE *\n")
fp_filter.write("  INCLUDE\n")
# include regions COM and OMP ?

fp_score = open(sys.argv[1], 'r')
linecount=0

min_time_percentage=float(sys.argv[2])
max_visits=int(sys.argv[3].replace(',',''))
sufficient_time_percentage=float(sys.argv[4])
print "min_time_percentage = ", min_time_percentage
print "sufficient_time_percentage = ", sufficient_time_percentage

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
    if time_percentage >= min_time_percentage and (nb_visits < max_visits or time_percentage >= sufficient_time_percentage):
      function_prototype = words[6]
      tmp1 = function_prototype.split('(',2)
      tmp2 = tmp1[0]
      tmp_name_words = tmp2.split()
      function_name = tmp_name_words[len(tmp_name_words)-1]
      print "time_percentage = ", time_percentage, "   -   nb_visits = ", nb_visits, "    -    function name = ", function_name
      fp_filter.write("    *%s*\n" % function_name)
fp_score.close()
fp_filter.write("SCOREP_REGION_NAMES_END\n")
fp_filter.close()

