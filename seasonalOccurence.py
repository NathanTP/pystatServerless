"""
Demonstrates iterating over an instrument data set by orbit and determining
the occurrent probability of an event occurring.
"""

import os
import pysat
import matplotlib.pyplot as plt
import numpy as np
import pathlib

dataDir = pathlib.Path('datasets')
# Data Directory
pysat.utils.set_data_dir(str(dataDir))

# set the directory to save plots to
results_dir = '.'


# define function to remove flagged values
def filter_vefi(inst):
    idx, = np.where(inst['B_flag'] == 0)
    inst.data = inst.data.iloc[idx]
    return


def processRange(start, stop):
    """Calculate the probability info for a range of time. This assumes that
    data is available in dataDir.

    This function is intended to eventually go into separate programs, so it's
    as self-contained as possible.
    """

    # select vefi dc magnetometer data, use longitude to determine where
    # there are changes in the orbit (local time info not in file)
    orbit_info = {'index': 'longitude', 'kind': 'longitude'}
    vefi = pysat.Instrument(platform='cnofs', name='vefi', tag='dc_b',
                            clean_level=None, orbit_info=orbit_info)

    vefi.custom.add(filter_vefi, 'modify')

    # if there is no vefi dc magnetometer data on your system, then run command
    # below where start and stop are pandas datetimes (from above)
    # pysat will automatically register the addition of this data at the end of
    # download
    if not (dataDir / 'cnofs').exists():
        vefi.download(start, stop)

    # leave bounds unassigned to cover the whole dataset (comment out lines below)
    vefi.bounds = (start, stop)

    # perform occurrence probability calculation
    # any data added by custom functions is available within routine below
    ans = pysat.ssnl.occur_prob.by_orbit2D(vefi, [0, 360, 144], 'longitude',
                                           [-13, 13, 104], 'latitude', ['dB_mer'],
                                           [0.], returnBins=True)

    # a dict indexed by data_label is returned
    # in this case, only one, we'll pull it out
    return ans['dB_mer']


def aggregateResults(results):
    """Perform an average of a list of results from processRange.
    Returns a dictionary with matching bin_x and bin_y, the sum of count, prob,
    and the number of probabilities in the sum per cell.
    
    This function is useful for hierarchically aggregating probabilities for a
    global average calculation."""
    counts = []
    probs = []
    nprob = np.zeros(results[0]['prob'].shape)
    for r in results:
        counts.append(r['count'].copy())
        probs.append(r['prob'].copy())

    # Everything has the same x,y so we just copy it from the first
    agg = { 'bin_x' : results[0]['bin_x'].copy(), 'bin_y' : results[0]['bin_y'].copy() }

    agg['count'] = np.sum(counts, axis=0)
    agg['prob'] = np.nanprod(probs, axis=0)

    return agg


def plotProb(ans, name='ssnl_occurrence_by_orbit_dem'):
    # plot occurrence probability
    f, axarr = plt.subplots(2, 1, sharex=True, sharey=True)
    masked = np.ma.array(ans['prob'], mask=np.isnan(ans['prob']))
    im = axarr[0].pcolor(ans['bin_x'], ans['bin_y'], masked)
    axarr[0].set_title('Occurrence Probability Delta-B Meridional > 0')
    axarr[0].set_ylabel('Latitude')
    axarr[0].set_yticks((-13, -10, -5, 0, 5, 10, 13))
    axarr[0].set_ylim((ans['bin_y'][0], ans['bin_y'][-1]))
    plt.colorbar(im, ax=axarr[0], label='Occurrence Probability')

    im = axarr[1].pcolor(ans['bin_x'], ans['bin_y'], ans['count'])
    axarr[1].set_title('Number of Orbits in Bin')
    axarr[1].set_xlabel('Longitude')
    axarr[1].set_xticks((0, 60, 120, 180, 240, 300, 360))
    axarr[1].set_xlim((ans['bin_x'][0], ans['bin_x'][-1]))
    axarr[1].set_ylabel('Latitude')
    plt.colorbar(im, ax=axarr[1], label='Counts')

    f.tight_layout()
    plt.savefig(os.path.join(results_dir, name))
    plt.close()


# Do entire range in one shot
fullAns = processRange(pysat.datetime(2010, 5, 9), pysat.datetime(2010, 5, 15))

# Do range in partitions and aggregate the results. This doesn't seem to be
# perfect, but the results are similar.
ndays = 7
perDay = []
for i in range(ndays):
    perDay.append(processRange(pysat.datetime(2010, 5, 9 + i), pysat.datetime(2010, 5, 9 + i)))

agg = aggregateResults(perDay)

plotProb(fullAns, name='full')
plotProb(agg, name='agg')
