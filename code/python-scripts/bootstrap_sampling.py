import xarray as xr
import numpy as np
import sys
import random
from scipy import stats
import glob
from resampling import _resample_iterations_idx
#from definitions import *  # imports all functions from definitions.py

xr.set_options(
    keep_attrs=True, display_style="html"
)  # Attributes of DataArrays will be kept through operations.

alt = [
    70,
    72,
    74,
    76,
    78,
    80,
    82,
    84,
    86,
    88,
    90,
    92,
    94,
    96,
    98,
    100,
    102,
    104,
    106,
    108,
    110,
    112,
    114,
    116,
    118,
    120,
]
root_path = "/home/gemeinsam_tmp/UA_students/data/PW_GW_analysis/"
dir_path = "/home/hochatmstud/bene/"

def g_kde(y, x):
    """Firstly, kernel density estimation of the probability density function of randomized anomalies.
    Secondly, evaluates the estimated pdf on a set of points.

    Args:
        y (np.array): datapoints to estimate from (randomized anomalies)
        x (np.array): datapoints to be evaluated (composite values)
    Returns:
        np.array: the estimated pdf on composite values
    """
    mask = np.isnan(y)
    kde = stats.gaussian_kde(y[~mask])
    return kde(x)

def stat_signific(station, array, climatology):
    time_scale = sys.argv[2]  # 20 or 30 ; input timescale
    its = 10000  # 10000 ; number of samples
    rechunk = True  # allows rechunking in xr.apply_ufunc

    if station == "Leipzig":
        size = 7
    elif station == "Esrange":
        size = 11
    elif station == "Sodankyla":
        size = 4
    elif station == "Sodankyla_Kiruna":
        size = 11
    elif station == "CMOR":
        size = 9
    elif station == "RioGrande":
        size = 3
    elif station == "Davis":
        size = 7

    line_width = 5

    array = array.sel(alt=slice(80, 100)).dropna("days")
    climatology = climatology.sel(alt=slice(80, 100))

    array = array["u0_mean"]

    p = []

    for lag in range(-40, 41, 1):
        # samples generation (loaded from external function)
        rnd_arr = _resample_iterations_idx(
            climatology, its, "time", replace=True, chunk=False, dim_max=size
        )
        print("".ljust(line_width) + "{} samples generated".format(its))

        print(rnd_arr)
        print(array)

        # statistical significance calculation (vectorized g_kde)
        da_kde = xr.apply_ufunc(
            g_kde,
            rnd_arr,
            array.sel(days=lag),
            input_core_dims=[["iteration"], []],
            vectorize=True,
            dask="parallelized",
            exclude_dims=set(("iteration",)),
            output_core_dims=[[]],
            output_dtypes=[array.dtype],
        )
        print("".ljust(line_width) + "p-values calculated")
        da_kde.name = climatology.name

        p.append(da_kde)

    p_comp = xr.concat(p, dim="days")
    p_comp["days"] = range(-40, 40 + 1)

    array.where(p_comp < 0.05).plot(x="days", robust=True)
