# writes a scorep filter file <scorep_filter_file> to include all regions with execution time greater than <min_time_percentage> and (number of visits not greater than <max_visits> or execution time greater than <sufficient_time_percentage>)
# using <include_all_OMP> and <include_all_COM> one can include all OpenMP or Communication regions
# 
# Usage: python write_scorep_filter.py <scorep-score_file> <min_time_percentage> <max_visits> <sufficient_time_percentage> <scorep_filter_file> <include_all_OMP> <include_all_COM>
# example: python write_scorep_filter.py toto.log 0.3 1000000 10 toto.filt
# params:
#   scorep-score_file = IN the output of the 'scorep-score -r' command
#   min_time_percentage = IN minimum percentage of execution time required to include the function (if the other conditions are met)
#   max_visits = IN maximum number of visits of the function to include the function (if the other conditions are met)
#   sufficient_time_percentage = IN minimum  percentage of execution time required to include the function even if the other conditions are not met
#   scorep_filter_file = OUT scorep filter file
#   include_all_OMP = include all regions of type OMP even if time percentage is lower than min_time_percentage - value can be 0 (no) or 1 (yes)
#   include_all_COM = include all regions of type COM even if time percentage is lower than min_time_percentage - value can be 0 (no) or 1 (yes)


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
include_all_OMP=int(sys.argv[6])
include_all_COM=int(sys.argv[7])
print "min_time_percentage = ", min_time_percentage
print "sufficient_time_percentage = ", sufficient_time_percentage
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
    if ( time_percentage >= min_time_percentage and (nb_visits < max_visits or time_percentage >= sufficient_time_percentage) ) or (include_all_OMP==1 and region_type=="OMP") or (include_all_COM==1 and region_type=="COM") :
      function_prototype = words[6]
      tmp1 = function_prototype.split('(',2)
      tmp2 = tmp1[0]
      tmp_name_words = tmp2.split()
      function_name = tmp_name_words[len(tmp_name_words)-1]
#      print "time_percentage = ", time_percentage, "   -   nb_visits = ", nb_visits, "    -    function name = ", function_name
      fp_filter.write("    *%s*\n" % function_name)
fp_score.close()
fp_filter.write("SCOREP_REGION_NAMES_END\n")
fp_filter.close()
