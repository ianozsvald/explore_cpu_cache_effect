import time
import cPickle
import argparse
import numpy as np
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

# Intention:
# Measure cache speed on a CPU using a single numpy array with some in-place
# operations. We measure the cache speed by increasing the size of the array,
# starting small enough to fit entirely in the cache and growing until the
# majority of the array must stay in RAM
# Usage:
# python measure_cache_effect.py --help  # show help
# python measure_cache_effect.py --time <filename>  # make recordings, write to
# filename
# python measure_cache_effect.py --graph <filename1> [<filnameN>...]  # read
# the record timings and plot on a graph
# --graphline  # switch from boxplot (default) to labelled line output (for
# comparing multiple runs)


def get_cpu_info():
    """Attempt to make sensible titles from processor info"""
    cpu_model = "Unknown CPU model"
    #cpu_cache_size = "Unknown cache size"
    cpu_cache_bytes = 1  # unknown indicated by 1 byte
    cpu_cache_alignment = "Unknown cache alignment"
    try:
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        # convert lines like the following from /proc/cpuinfo into strings
        # 'model name\t: Intel(R) Core(TM) i7-2720QM CPU @ 2.20GHz\n',
        # 'cache size\t: 6144 KB\n',
        # 'cache_alignment\t: 64\n',
        cpu_model = [line for line in lines if 'model name' in line][0].strip().split(':')[1].strip()
        cpu_cache_size = [line for line in lines if 'cache size' in line][0].strip().split(':')[1].strip()
        if ' KB' in cpu_cache_size:
            # assuming it looks like '6144 KB'
            cpu_cache_bytes = int(cpu_cache_size.split()[0]) * 1000
        cpu_cache_alignment = [line for line in lines if 'cache_alignment' in line][0].strip().split(':')[1].strip()
    except IOError:
        pass
    return cpu_model, cpu_cache_bytes, cpu_cache_size, cpu_cache_alignment


# L2 cache but it looks odd?
# Core i7-2720QM
#max_length = 64000
#increment_by = 4000
#nbr_repeated_operations = 20000
#box_width = 25000

# good for L3 cache
# http://en.wikipedia.org/wiki/List_of_Intel_Core_i7_microprocessors#.22Sandy_Bridge_.28quad-core.29.22_.2832_nm.29
# Core i7-2720QM, 4*256KB L2, 6MB L3
max_length = 1.8e6
max_length = 268000  # very short plot
increment_by = 50000
nbr_repeated_operations = 100
box_width = 200000

# Core 2 Duo P7350 3MB cache
# Macbook Core 2 Duo with L2 3MB cache
#max_length = 600000
#increment_by = 20000
#box_width = 100000

# labels for this laptop
cpu_model, cpu_cache_bytes, cpu_cache_size, cpu_cache_alignment = get_cpu_info()
print cpu_model, cpu_cache_bytes, cpu_cache_alignment

#laptop_label = "Core i7-2720QM, 4*256KB L2, 6MB L3"  # graph title
#cache_label = "6MB L3 cache"  # text of red line marker for the graph
laptop_label = cpu_model
cache_location = cpu_cache_bytes  # 6e6  # position of cache_label on the graph
cache_label = cpu_cache_size

trials = 30

starting_length = increment_by
array_length = starting_length
dtype = np.int_

OUT_FILE_NAME = 'pi_numpy_benefitsvectorization.pickle'


parser = argparse.ArgumentParser(description='Project description')
parser.add_argument('--time', type=str, help="Time cache behaviour, write output to <filename>")
parser.add_argument('--graph', nargs="*", type=str, help="Graph cache behaviour, read output from <filename>")
parser.add_argument('--graphline', action="store_true", default=False, help='By default plot uses boxplot, with graphline it plots a single line')
args = parser.parse_args()
print "Args:", args

if args.time:
    nbytes = []
    all_deltas = []
    while array_length < max_length:
        deltas = []
        a = np.ones(array_length, dtype=dtype)
        print "array_length {}, nbytes {}, ".format(array_length, a.nbytes)
        nbytes.append(a.nbytes)
        for t in xrange(trials):
            a = np.ones(array_length, dtype=dtype)
            t1 = time.time()
            # loop on some basic operations, in-place
            # a number of times so we have something to measure
            for inner_loop in xrange(nbr_repeated_operations):
                a *= a
                a += 1
            delta = time.time() - t1
            delta /= float(a.nbytes)  # normalise to time per byte
            deltas.append(delta)
        all_deltas.append(deltas)
        array_length += increment_by

    all_deltas = np.array(all_deltas)
    nbytes = np.array(nbytes)
    timings = all_deltas

    print "Writing to:", args.time
    with open(args.time, 'wb') as f:
        dumped_data = {'timings': timings,
                       'nbytes': nbytes}
        cPickle.dump(dumped_data, f)


if args.graph:
    # make sure matplotlib has been imported
    if 'plt' in dir():
        plt.figure(1)
        plt.clf()

        graph_filenames = args.graph
        for graph_filename in graph_filenames:
            print "Loading data from", graph_filename
            with open(graph_filename, 'rb') as f:
                dumped_data = cPickle.load(f)
                timings = dumped_data['timings']
                nbytes = dumped_data['nbytes']

            timings_averaged = np.average(timings, axis=1)

            if args.graphline:
                plt.plot(nbytes, timings_averaged, label=graph_filename)
            else:
                plt.boxplot(timings.T, positions=nbytes, widths=box_width)
            plt.ylabel("Time per byte (seconds)")
            plt.xticks(plt.xticks()[0], ["{:,}".format(int(xb / 1000.0)) for xb in nbytes], rotation=45)
            plt.xlabel("Total array size (kB)")

        # annotate the cache location
        plt.vlines(cache_location, plt.ylim()[0], plt.ylim()[1], colors='r')
        plt.annotate(cache_label, (cache_location, np.max(timings)))

        plt.title(laptop_label)
        plt.grid()

        if args.graphline:
            plt.legend()
        plt.show()
    else:
        print "matplotlib must be installed to generate a graph"
