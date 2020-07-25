# Santa Clara County COVID-19 Timeseries data

## Motivation

[Santa Clara County DPH](https://www.sccgov.org/sites/phd/Pages/phd.aspx) has [released some excellent data](https://data.sccgov.org/browse?category=COVID-19).  Unfortunately, some of the data is only provided as instantaneous snapshots of the disease's spread.  To fully characterize how the disease is spreading, timeseries data can be very helpful.  This repo contains the tooling to build timeseries data and the actual timeseries data starting from July 22, 2020.

## Using the data

To browse the compiled datasets, install python and a few python packages ([xarray](http://xarray.pydata.org/en/stable/), [scipy](https://www.scipy.org), and [requests](https://requests.readthedocs.io/en/master/)).  Installing [ipython](https://ipython.org) is optional but helpful.

```
% pip install xarray scipy requests
% pip install ipython
% ipython
Python 3.8.0 (default, Nov  3 2019, 10:55:54) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.16.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import requests                                                                                                                                

In [2]: import xarray as xr                                                                                                                            

In [3]: data = xr.open_dataset(requests.get('https://github.com/ttung/scc-covid-timeseries/blob/trunk/netcdf/cases-by-zip.netcdf?raw=true').content)   

In [4]: data                                                                                                                                           
Out[4]: 
<xarray.Dataset>
Dimensions:     (time: 4, zipcode: 57)
Coordinates:
  * zipcode     (zipcode) int32 94022 94024 94040 94041 ... 95139 95140 95148
  * time        (time) datetime64[ns] 2020-07-23T22:00:12 ... 2020-07-24T22:0...
Data variables:
    population  (time, zipcode) int32 ...
    rate        (time, zipcode) float64 ...
    cases       (time, zipcode) float64 ...
```

One could view the data for a particular zipcode across time by selecting that zipcode:

```
In [5]: data.sel(zipcode=95127).cases                                                                                                                 
Out[5]: 
<xarray.DataArray 'cases' (time: 4)>
array([527., 547., 564., 570.])
Coordinates:
    zipcode  int32 95127
  * time     (time) datetime64[ns] 2020-07-21T22:00:16 ... 2020-07-24T22:01:44

In [5]: 
```
