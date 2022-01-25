# Python scripts accessing data Pangeo CMIP6 Gallery

A python script to download cmip6 data from Pangeo and Google cloud storage for given scenarios and models. The original data is available in Pangeo CMIP6 Gallery at http://gallery.pangeo.io/repos/pangeo-gallery/cmip6/index.html.

# Requirements:

Requires installation of several python packages. The packages can be installed through a conda installation. Create a new environment from the yml included in the repository as

```conda env create --name pg_cmip6 --file environment_macos.yml``` for mac

```conda env create --name pg_cmip6 --file environment_linux.yml``` for linux, cluster (e.g., atacama)

The environment can be activated using

```conda activate pg_cmip6```

# Usage:
Run the python script with the input json filename as the argument.

```python get_cmip6.py input.json```

# Options and Settings

The input json includes the following fields.

- metadata_csv: Path to the metadata file for the google data storage. A locally downloaded csv can be used. If empty (""), it will automatically retrieve the metadata from https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv.

- out_dir: Path to the output directory.

- experiments: The experiments for which the data should be downloaded. Each experiment has a list input as [start year, end year] for the period of the data to be downloaded, e.g.,

```json
    historical: [
        1980,
        2010
    ]
```

- variables: The variables to be downloaded in the format ```variable_name: table ID```, e.g., "tas": "Amon".

- target_grid: A setting for the taget spatial resolution as [lat_reso, lon_reso], e.g., [1, 1] to regrid all data to 1 degree by 1 degree spatial resolution. If the list is blank [], the data will not be regridded, and only the original data will be saved.

- regrid_method: The method to be used for spatial regridding based on xESMF (https://xesmf.readthedocs.io/en/latest/index.html). Use one of ```['bilinear', 'conservative', 'nearest_s2d', 'nearest_d2s', 'patch']```.

- download_all: Nuclear option to download all available models and ensemble members for the given variables and experiments. When set to false, only the models and ensemble members given in the data_set section will be downloaded. Naturally, setting download_all to true will be slower than downloading selected data.

- dataset: A list of models and ensembles to be downloaded given as a dictionary block for each model. The key is an unique identifier. source_id is the exact model name, ens_members is a list of ensemble members. Add a block per model for multiple models.

```json
    ipsl: {
        source_id: IPSL-CM6A-LR,
        ens_members: [
            r1i1p1f1
        ]
    }
```

# Disclaimer:

This repository is created to support the download and regriding CMIP6 data for research purposes. Any usage beyond the intended purpose are the responsibility of the users.

The developer does not bear any responsibility for the data quality and correctness. All users should also cite the original data accordingly, and acknowledge the usage of this tool for usage as using:

Koirala, Sujan, Python scripts to access CMIP6 data from Pangeo Gallery, Version 1.0, https://zenodo.org/record/5900393




# License: 

Attribution 4.0 International (CC BY 4.0).

# Useful Links

- http://gallery.pangeo.io/repos/pangeo-gallery/cmip6/basic_search_and_load.html