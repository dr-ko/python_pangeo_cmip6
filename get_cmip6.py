# A script to use pangeo data store to download cmip6 data_set
# Developer: Sujan Koirala (skoirala@bgc-jena.mpg.de)
# Date: 2021-02-09
import pandas as pd
import fsspec
import xarray as xr
import xesmf as xe
import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sys

# load the input settings
in_settings = sys.argv[1]
input = json.load(open(in_settings))

# load metadata of the data in pangeo
if len(input['metadata_csv'].strip()) > 0:
    meta_data = pd.read_csv(input['metadata_csv'])
    print("using local metadta from: ", input['metadata_csv'])
else:
    print("using metadta from https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv")
    meta_data = pd.read_csv('https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv')

# prepare the output directory
out_dir = input['out_dir']
os.makedirs(out_dir, exist_ok=True)
data_set=input['dataset']

# check if the download all models option is invoked. If True, all unique models and ensemble members are obtained from metadata
if input['download_all_models']:
    models = meta_data['source_id'].unique()
    all_models = True
else:
    models = data_set.keys()
    all_models = False

# check if the download all ensemble members option is invoked. If True, all unique models and ensemble members are obtained from metadata
if input['download_all_members']:
    ens_members = meta_data['member_id'].unique()
    full_ensemble = True
else:
    ens_members = None
    full_ensemble = False


# check if regrid option is activated and create a lat lon array for target spatial grids
if len(input['target_grid']) == 2:
    regrid_data = True
    tar_lat_int = input['target_grid'][0]
    tar_lon_int = input['target_grid'][1]
    n_lat = int(180./tar_lat_int)
    n_lon = int(360./tar_lon_int)
    lat_min = -90 + tar_lat_int/2.
    lat_max = 90 - tar_lat_int/2.
    lon_max = 360 - tar_lon_int/2.
    lon_min = tar_lon_int/2.
    new_lat = np.linspace(lat_min, lat_max, n_lat, endpoint=True)
    new_lon = np.linspace(lon_min, lon_max, n_lon, endpoint=True)
else:
    regrid_data = False

# loop through the experiments and dataset
for experiment, info in input['experiments'].items():
    start_year = info[0]
    end_year = info[1]
    # loop through the unique models
    for model in models:
        # get models if download_all_models/all_models is False
        if not all_models:
            src = data_set[model]['source_id']
        else:
            src = model

        # get ensemble members if download_all_members/full_ensemble is False
        if not full_ensemble:
            ens_members = data_set[model]['ens_members']
        # loop through the variables
        for variable, table in input['variables'].items():
            # loop through the ensemble
            for variant in ens_members:
                qry = "table_id == '" + table +"' & variable_id == '" + variable + "' & experiment_id == '" + experiment + "' & source_id == '" + src + "' & member_id == '" + variant + "'"
                meta_data_sel = meta_data.query(qry)
                if not meta_data_sel.empty:
                    print("Trying to download: ")
                    print(qry)
                    # print(meta_data_sel)
                    zstore = meta_data_sel.zstore.values[-1]
                    # create a mutable-mapping-style interface to the store
                    mapper = fsspec.get_mapper(zstore)
                    # open it using xarray and zarr
                    ds = xr.open_zarr(mapper, consolidated=True)
                    ds_sel_time = ds.sel(time=slice(str(start_year), str(end_year)))

                    file_name_nc = '{var}_{exp}_{tab}_{sroc}_{vrnt}_{syr}_{eyr}.nc'.format(var=variable, exp=experiment, tab=table, sroc=src, vrnt=variant, syr=str(start_year), eyr=end_year)
                    out_file = os.path.join(out_dir, file_name_nc)
                    ds_sel_time.to_netcdf(out_file)
                    print('saved original resolution: ', out_file)
                    # regrid if the option is invoked
                    if regrid_data:
                        # create dataset with target grid
                        ds_out = xr.Dataset({'lat': (['lat'], new_lat), 'lon': (['lon'], new_lon),})
                        # create regridder object
                        regridder = xe.Regridder(ds_sel_time, ds_out, input['regrid_method'])
                        # regrid data
                        ds_int = regridder(ds_sel_time)
                        # create and save the output
                        file_name_nc_int = '{var}_{exp}_{tab}_{sroc}_{vrnt}_{syr}_{eyr}_{t_lat}x{t_lon}.nc'.format(var=variable, exp=experiment, tab=table, sroc=src, vrnt=variant, syr=str(start_year), eyr=end_year, t_lat=str(tar_lat_int), t_lon=str(tar_lon_int))
                        out_file_int = os.path.join(out_dir, file_name_nc_int)
                        ds_int.to_netcdf(out_file_int)
                        # close dataset
                        ds_int.close()
                        ds_out.close()
                        print('saved regridded data: ', out_file)
                    # close dataset
                    ds_sel_time.close()
                    ds.close()
                else:
                    print(f'Data not found for: {variable}')
                    print(qry)
                print ('---------------------------------------')
            

