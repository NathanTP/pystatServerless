# PySat Example Workload for CFFS
This repo contains an example workload for lambda/CFFS based on the pySat
library. It  uses the example code provided
[here](https://pysat.readthedocs.io/en/latest/examples.html#seasonal-occurrence-by-orbit),
which calculates the probability of perturbations in the magnetic field by
lat,long bins over a time window.

## Quick Start
You'll first need to get the dependencies. This is a bit challenging as the
system requires pandas>=0.23,<0.25 which is very old. We provide an anaconda
environment file that should work:

    $ conda env create -f environment.yml

There is also a requirements.txt that should work with python3.7.

You can now run the example local application:

    $ python3 seasonalOccurence.py

The first run will download the dataset which may take a bit of extra time.
Future runs will use the cached version. As output, you will see two images
representing the final data that would be used by a domain expert: agg.png
which represents the partitioned and aggregated data, and full.png which
represents the non-partitioned run. If you open them, you will notice that they
are similar, but not identical. This is due to the simple aggregation strategy
that we use.

## Application Patterns and Overview
Most of the application-specific code is deep in the pysat library
(pysat.ssnl.occur\_prob.by\_orbit2D()), our modifications primarily focus on
how that function gets called and distributed.

### Basic Application Flow
The basic flow of the code is as follows:
1. The publicly available cnofs dataset for some date-time range is downloaded
   to a common datasets directory (datasets/cnofs). This download is cached
   between runs.
1. We decide on a partitioning of the dataset by date-time range (e.g. split by day).
1. Each partition is processed by pysat (processRange()), resulting in a results dict containing
   a matrix of probabilities with one cell for each lat,long bin.
1. The per-partition results are aggregated by multiplying the probabilities.  
1. The aggregated results are plotted and stored to (agg.png)

### Key Datastructures 
The processRange function returns a dictionary with the following fields
(defined by pysat.ssnl.occur\_prob.by\_orbit2D):
* 'bin\_y', 'bin\_x': Vectors containing the latitude and longitude
  (respectively) boundaries for each bin.
* 'count': A matrix containing the number of unique orbit crossings for each
  bin (e.g. the number of unique measurements).
* 'prob': A matrix containing the probability measure for each cell.
  Ultimately, this is what the application wants.

### Caveats
The aggregation strategy we use (multiplying probabilities per-partition) is
not identical to the non-partitioned algorithm. We don't have great visibility
into the core algorithm, but presumably it's doing some additional calculations
across the entire range. However, the results are qualitatively similar and
clearly outputs the same trends, just with less resolution.
