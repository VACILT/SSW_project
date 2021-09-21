# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import xarray as xr
import xarray.ufuncs as xrf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob

# # Meteor radars

# * Dav        Davis; GW:200501-201912
# * Col         Collm (Leipzig); GW:200408-201903
# * Rio         RioGrande (SAAMER- Argentina); GW:200802-201912
# * Sod        Sodankyla; GW:200810-201912
# * Kir          Kiruna (Sweden ? Esrange); GW:199908-201912
# * CMA      CMOR (Canada ? CMA (CMOR All) triple frequency data); GW:200201-201812
# * SES        Sodankyla ? Esrange merged (assigned either to Esrange or Sodankyla or a virtual center in between); GW:199908-201912

# ## Juliusruh

alt_jul = [
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
root_path = "/home/gemeinsam_tmp/UA_students/data/"

station = "Col"
infiles = f"{root_path}{station}/Meteor_radar_{station}_GW_*.h5"
ds_jul = xr.open_mfdataset(
    infiles, concat_dim="phony_dim_6", group="wind", combine="nested", parallel=True
)
ds_jul = ds_jul.rename({"phony_dim_6": "time", "phony_dim_7": "alt"})
ds_jul["alt"] = alt_jul
ds_jul["alt"].attrs["units"] = "km"
# change time range according to meteor radar station
ds_jul["time"] = pd.date_range(
    start="2004-08-01", end="2019-03-31", periods=ds_jul.time.shape[0]
)
ds_jul

# ### Gravity waves

ds_jul[var]

wvar.plot(x="time", robust=True)

# +
var = "w"
wvar = ds_jul[var]

wvar.plot(x="time", robust=True)
# -

# #### Tagesmittel berechnen

# +
wvar_daily = wvar.resample(time="1D").mean("time")

wvar_daily.plot(x="time", robust=True, size=10)

wvar_daily.time
# -

# #### Linienplot für eine einzelne Höhe mit .sel(alt='Höhe in km').plot.line()

wvar_monthly.sel(alt=80).plot.line(size=8)

# #### Einen bestimmten Zeitpunkt auswählen mit .sel(time = 'zeit')

wvar.sel(time="2016-01-31").plot(x="time")

wvar.sel(alt=slice(None, 80))[:5].plot.line(col="time")

# #### Anomalien vom Jahresverlauf berechnen

climatology = wvar.groupby("time.day").mean("time")
anomalies = wvar.groupby("time.day") - climatology
anomalies.plot(x="time", size=8)
# anomalies.mean("location").to_dataframe()[["tmin", "tmax"]].plot()

var = "u"
da_jul_gwu = ds_jul[var] - ds_jul[f"{var}_fil"]
var = "v"
da_jul_gwv = ds_jul[var] - ds_jul[f"{var}_fil"]
da_jul_gw_total = 0.5 * (da_jul_gwu ** 2 + da_jul_gwv ** 2)  # kinetic energy

da_jul_gw_total.plot(x="time", robust=True, vmax=400, vmin=0)

# #### Climatology calculation

da_jul_gw_total_clim = da_jul_gw_total.groupby("time.month").mean("time").load()
da_jul_gw_total_clim

da_jul_gw_total_clim.plot(x="month", robust=True)

station = "Rio"
infiles = f"{root_path}{station}/Meteor_radar_{station}_GW_*.h5"
ds_jul = xr.open_mfdataset(
    infiles, concat_dim="phony_dim_6", group="wind", combine="nested", parallel=True
)
ds_jul = ds_jul.rename({"phony_dim_6": "time", "phony_dim_7": "alt"})
ds_jul["alt"] = alt_jul
ds_jul["alt"].attrs["units"] = "km"
ds_jul["time"] = pd.date_range(
    start="2008-02-01", end="2019-12-31", periods=ds_jul.time.shape[0]
)
ds_jul

xr.open_dataset(
    "/home/gemeinsam_tmp/UA_students/data/Rio/Meteor_radar_Rio_GW_200802.h5",
    group="info",
)["day"]

var = "u"
da_jul_gwu = ds_jul[var] - ds_jul[f"{var}_fil"]
var = "v"
da_jul_gwv = ds_jul[var] - ds_jul[f"{var}_fil"]
da_jul_gw_total = 0.5 * (da_jul_gwu ** 2 + da_jul_gwv ** 2)
da_jul_gw_total_clim = da_jul_gw_total.groupby("time.month").mean("time").load()
da_jul_gw_total_clim

da_jul_gw_total_clim.plot(x="month", robust=True)

# # GAIA

# ## Rio

root_path = "/home/gemeinsam_tmp/UA_students/data/"
infile = f"{root_path}GAIA_Rio_20080201_20141231_run20200603.nc"
ds = xr.open_dataset(infile, group="GAIA")
ds["time"] = pd.date_range(
    start="2008-02-01", end="2014-12-31", periods=ds.time.shape[0]
)
ds

# ### Tides amplitude in zonal wind (climatology)

# #### Diurnal

temp = ds["A24u"].sel(alt=slice(80, 100)).groupby("time.month").mean("time")
temp.plot.contourf(x="month", robust=True, levels=21)

# #### Semi-diurnal

temp = ds["A12u"].sel(alt=slice(80, 100)).groupby("time.month").mean("time")
temp.plot.contourf(x="month", robust=True, levels=21)

# #### Terdiurnal

temp = ds["A8u"].sel(alt=slice(80, 100)).groupby("time.month").mean("time")
temp.plot.contourf(x="month", robust=True, levels=21)

# ### Gravity waves

var = "u"
da_gwu = ds[var] - ds[f"{var}_fil"]
var = "v"
da_gwv = ds[var] - ds[f"{var}_fil"]
da_gw_total = 0.5 * (da_gwu ** 2 + da_gwv ** 2)
da_gw_total_clim = da_gw_total.groupby("time.month").mean("time")
da_gw_total_clim

da_gw_total.plot(x="time", robust=True)

da_gw_total.sel(alt=slice(60, 120)).plot(x="time", robust=True)

# #### Climatology

da_gw_total_clim.sel(alt=slice(50, 150)).plot(x="month", robust=True)
