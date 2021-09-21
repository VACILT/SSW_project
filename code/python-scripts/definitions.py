# Here all definitions and functions shall be stated for the analysis_per_station.ipynb - Notebook
import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import colors

# +
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

# global root_path
# root_path = root_path_list[1][index] #"/home/gemeinsam_tmp/UA_students/data/PW_GW_analysis/"
dir_path = "/home/hochatmstud/bene/"


# -

def read_group(gruppe, loc, root_path):

    station_name = loc

    infiles = f"{root_path}{station_name}_solar_cycle.h5"

    ds_info = xr.open_dataset(f"{root_path}{station_name}_solar_cycle.h5", group="info")
    ds_info = ds_info.rename({"phony_dim_7": "alt"})

    if gruppe == "wind":
        ds = xr.open_dataset(f"{root_path}{station_name}_solar_cycle.h5", group="wind")
        ds = ds.rename({"phony_dim_10": "time", "phony_dim_11": "alt"})
    elif gruppe == "waves":
        ds = xr.open_dataset(f"{root_path}{station_name}_solar_cycle.h5", group="waves")
        ds = ds.rename({"phony_dim_8": "time", "phony_dim_9": "alt"})

    s_year = int(ds_info["year"].values[0][0])
    s_month = int(ds_info["month"].values[0][0])
    s_day = int(ds_info["day"].values[0][0])

    ds = ds.assign_coords(
        {
            "alt": ds_info["alt"].squeeze(),
            "time": pd.date_range(
                f"{s_year}-{s_month}-{s_day}", freq="D", periods=ds.time.shape[0]
            ),
        }
    )
    ds["alt"].attrs["units"] = "km"  # dimension 'alt' gets unit 'km'
    ds["alt"].attrs[
        "long_name"
    ] = "altitude"  # displayed name of dimension 'alt' (e.g. in plots) will now be 'altitude'

    return ds


def read_var(gruppe, var):
    varout = gruppe[var]

    temp = varout.attrs
    varout.attrs["units"] = list(temp.values())[0].split(" / ")[-1]
    # varout.attrs['units'] = unit
    return varout


def anomalie(step, var):
    string = "time." + step
    climatology = var.groupby(string).mean("time")
    anomalies = var.groupby(string) - climatology

    return anomalies


def plotting_routine(array, var, log=False):
    if log == False:

        if var == "GWD":
            lower_boundary = 82
            upper_boundary = 98
        else:
            lower_boundary = 77
            upper_boundary = 101

        p = (
            array[f"{var}_mean"]
            .sel(alt=slice(lower_boundary, upper_boundary))
            .plot.contourf(x="days", size=9, robust=True, levels=41, aspect=4)
        )
        axs = p.ax
        nl = 11
        ax1 = (
            array[f"{var}_std"]
            .sel(alt=slice(lower_boundary, upper_boundary))
            .plot.contour(
                x="days",
                robust=True,
                levels=nl,
                colors="k",
                ax=axs,
                linewidths=np.linspace(0.1, 5, nl),
            )
        )
    elif log == True:

        if var == "GWD":
            lower_boundary = 82
            upper_boundary = 98
        else:
            lower_boundary = 77
            upper_boundary = 101

        levs = np.logspace(1, 2.75, num=21)
        p = (
            array[f"{var}_mean"]
            .sel(alt=slice(lower_boundary, upper_boundary))
            .plot.contourf(
                x="days",
                size=9,
                levels=levs,
                norm=colors.LogNorm(),
                vmin=10,
                vmax=750,
                extend="both",
                aspect=4,
            )
        )
        axs = p.ax
        nl = 11
        ax1 = (
            array[f"{var}_std"]
            .sel(alt=slice(lower_boundary, upper_boundary))
            .plot.contour(
                x="days",
                robust=True,
                levels=nl,
                colors="k",
                ax=axs,
                linewidths=np.linspace(0.1, 5, nl),
            )
        )

        p.colorbar.set_ticks([10, 100, 1000])
        p.colorbar.set_ticklabels(["10", "100", "1000"])


# Superposed epoch analysis
def sea(days_period, station_name, var):
    df_dates = pd.read_csv(
        dir_path
        + "dates/without_final_warmings/ssw_dates_without_final_warmings_"
        + station_name
        + ".csv"
    )  # you can load SSWs from a csv file like attached
    dates = df_dates.set_index("BeginDate")

    xa_ls = []
    max_lag = days_period
    for il, days in enumerate(range(-max_lag, max_lag + 1)):
        sel_dates = pd.to_datetime(dates.index) + pd.Timedelta(str(days) + " days")
        mask = np.in1d(var.time.dt.floor("1D"), sel_dates)
        comp_m = var.sel(time=mask).mean("time")
        comp_s = var.sel(time=mask).std("time")
        comp_m.name = f"{var.name}_mean"  # Variable Mittelwert umbenennen
        comp_s.name = f"{var.name}_std"  # Variable Standardabweichung umbenennen
        comp_m.attrs["units"] = var.attrs["units"]

        xa_ls.append(
            xr.merge([comp_m, comp_s])
        )  # Merge arrays of mean and standard deviation in one data array

    xa_comp = xr.concat(xa_ls, dim="days")
    xa_comp["days"] = range(-max_lag, max_lag + 1)

    return xa_comp
