"""
Demonstrates iterating over an instrument data set by orbit and determining
the occurrent probability of an event occurring.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import datetime
import argparse
import subprocess as sp

if os.path.exists('/tmp/cffs'):
    # in docker
    rootDir = pathlib.Path('/tmp/cffs/dockerSandbox/')
    inDocker = True
else:
    # on host
    rootDir = (pathlib.Path('..') / 'hostSandbox').resolve()
    rootDir.mkdir(mode=0o771, exist_ok=True)
    inDocker = False

# This is due to a limitation of pysat that insists on putting files in your
# home directory which is not always writeable (e.g. on lambda)
os.environ['HOME'] = str(rootDir)
import pysat

# Data Directory
dataDir = rootDir / 'datasets'
if not dataDir.exists():
    dataDir.mkdir(mode=0o771)

pysat.utils.set_data_dir(str(dataDir))

# set the directory to save plots to
resultsDir = rootDir / 'results'

# define function to remove flagged values
def filter_vefi(inst):
    idx, = np.where(inst['B_flag'] == 0)
    inst.data = inst.data.iloc[idx]
    return

def getVefiInstrument():
    # select vefi dc magnetometer data, use longitude to determine where
    # there are changes in the orbit (local time info not in file)
    orbit_info = {'index': 'longitude', 'kind': 'longitude'}
    vefi = pysat.Instrument(platform='cnofs', name='vefi', tag='dc_b',
                            clean_level=None, orbit_info=orbit_info)

    vefi.custom.add(filter_vefi, 'modify')
    return vefi

def probsRange(start, stop):
    """Calculate the probability info for a range of time. This assumes that
    data is available in dataDir.

    This function is intended to eventually go into separate programs, so it's
    as self-contained as possible.
    """

    vefi = getVefiInstrument()

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
    """Perform an average of a list of results from probsRange.
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
    
    if not resultsDir.exists():
        resultsDir.mkdir(mode=0o771)

    plt.savefig(resultsDir / name)
    plt.close()

def processDay(day):
    probs = probsRange(day, day)
    plotProb(probs, day.strftime("%y-%m-%d"))

def faasLambda(event, context):
    """An AWS lambda compatible function.
    Assumes that the appropriate days are available in dataDir.
    There are two modes: 'baseline' and 'cffs'
        'baseline' will return results in an AWS-native way (XXX need to decide what this is)
        'cffs' will simply write the results into the results/ directory under
        the assumption that a shared filesystem is mounted there.

    Argument is a dictionary with the following fields:
        'nday' - the number of days to process
        'mode' - either 'baseline' or 'cffs'
    """
    dates = [ startDate + datetime.timedelta(days=day) for day in range(event['nday']) ]
    for date in dates:
        processDay(date)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate plots of a statistical analysis of the cnofs vefi satelite dataset')
    parser.add_argument('-p', '--parallel', type=int, default=1, help='degree of parallelism to use')
    parser.add_argument('-n', '--nday', type=int, default=1, help='Number of days to process (starting from 5-9-2010)')
    parser.add_argument('-l', '--lambda', dest='useLambda', action='store_true', default=False, help='Use lambda to run the application instead of local processes')

    args = parser.parse_args()

    if args.useLambda:
        print("Running with Lambda")

        if 'AWS_DEFAULT_REGION' not in os.environ:
            os.environ['AWS_DEFAULT_REGION'] = 'none'

        import lambdamultiprocessing.lambdamultiprocessing as mp
    else:
        print("Running with local processes")
        import multiprocessing as mp

    startDate = pysat.datetime(2010, 5, 9)

    # Download the dataset for the date range this is not parallelized and is
    # expected to be cached under normal circumstances
    vefiDir = dataDir / 'cnofs' / 'vefi' / 'dc_b'
    vefi = getVefiInstrument()
    def download(day):
        date = startDate + datetime.timedelta(days=day)
        print("Downloading data for " + date.strftime("%y-%m-%d"))
        fname = 'cnofs_vefi_bfield_1sec_' + date.strftime("%Y%m%d") + "_v05.cdf"
        if not (vefiDir / fname).exists():
            vefi.download(date, date)

    pool = mp.Pool(args.parallel)

    # XXX This currently doesn't work on lambda
    # pool.map(download, range(args.nday))

    # Serial download on manager
    for day in range(args.nday):
        download(day)

    dates = [ startDate + datetime.timedelta(days=day) for day in range(args.nday) ]
    if args.parallel == 1:
        # Generate graphs for each day
        for date in dates:
            processDay(date)
    else:
        pool.map(processDay, dates)
