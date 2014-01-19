explore_cpu_cache_effect
========================

Understanding my CPU's L3 cache using numpy vectorized operations

The goal is to understand how numpy vectorized operations are effected by L3 cache sizes.

To record the cache effect use:

    $ python measure_cache_effect.py --time <filename>  

To graph the output use:

    $ python measure_cache_effect.py --graph <filename1> [<filnameN>...]  

It'll generate a plot like the following for an unladen machine:

![alt tag](explore_cpu_cache_effect/e6420_nocompetition.png)

If you make two recordings under different situations you can compare them. In this case I'm comparing an unladen machine (nothing but this code running) with one of the recordings made when I ran this process twice simultaneoushly (which would make the L3 cache far more heavily used).

    $ python measure_cache_effect.py --graph <filename1> <filname2> --graphline

![alt tag](e6420_nocompetition_vs_competition_line.png)

