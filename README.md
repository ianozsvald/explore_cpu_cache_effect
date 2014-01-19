explore_cpu_cache_effect
========================

Understanding my CPU's L3 cache using numpy vectorized operations

The goal is to understand how numpy vectorized operations are affected by L3 cache sizes. An array of increasing length is investigated, an inplace operation is performed and the execution time on the array is recorded. The execution time is plotted against the number of bytes in the array as seen below.

The execution time is normalised to the number of bytes so if arbitrary length arrays 'cost' the same amount of time to process per byte, we'd see a flat line. Instead we see a sigmoid with higher costs for larger arrays.

To record the cache effect use:

    $ python measure_cache_effect.py --time <filename>  

To graph the output use:

    $ python measure_cache_effect.py --graph <filename1> [<filnameN>...]  

It'll generate a plot like the following for an unladen machine:

![alt tag](e6420_nocompetition.png)

If you make two recordings under different situations you can compare them. In this case I'm comparing an unladen machine (nothing but this code running) with one of the recordings made when I ran this process twice simultaneoushly (which would make the L3 cache far more heavily used).

    $ python measure_cache_effect.py --graph <filename1> <filname2> --graphline

![alt tag](e6420_nocompetition_vs_competition_line.png)

Other notes
-----------

* http://stackoverflow.com/questions/14674463/why-doesnt-perf-report-cache-misses

    $ perf stat -B -e cache-references,cache-misses,cycles,instructions,branches,faults,migrations python measure_cache_effect.py --time dummy.pickle

perf stat can measure cache misses, running the non-competitive version yields:

 Performance counter stats for 'python measure_cache_effect.py --time dummy.pickle':

     9,350,375,599 cache-references                                            
     2,047,742,205 cache-misses              #   21.900 % of all cache refs    
   556,478,747,432 cycles                    #    0.000 GHz                    
 1,707,414,165,292 instructions              #    3.07  insns per cycle        
   190,501,416,729 branches                                                    
           254,142 faults                                                      
                13 migrations                                                  
     253.529216753 seconds time elapsed

For two at the same time (competitive):


 Performance counter stats for 'python measure_cache_effect.py --time dummy.pickle':

    12,201,926,851 cache-references                                            
     3,596,505,964 cache-misses              #   29.475 % of all cache refs    
   729,108,789,427 cycles                    #    0.000 GHz                    
 1,707,483,701,009 instructions              #    2.34  insns per cycle        
   190,514,623,535 branches                                                    
           254,141 faults                                                      
                10 migrations                                                  
     332.255561372 seconds time elapsed

