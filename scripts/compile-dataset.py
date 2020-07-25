#!/usr/bin/env python

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, MutableMapping, OrderedDict, Sequence, Set, Tuple

import numpy as np
import xarray as xr


def read_files(path: Path) -> Tuple[Mapping[datetime, Sequence[OrderedDict[str, Any]]], Set[str], Set[str], Set[str]]:
    assert path.is_dir()

    results: MutableMapping[datetime, Sequence[OrderedDict[str, Any]]] = {}
    all_field_names = set()
    for csvpath in path.glob("*.csv"):
        headerspath = csvpath.parent / f"{csvpath.stem}.headers"

        with headerspath.open("r") as fh:
            for line in fh.readlines():
                splitted = line.strip().split(": ", maxsplit=2)
                if len(splitted) != 2:
                    continue
                if splitted[0] == "Last-Modified":
                    now = datetime.strptime(splitted[1], "%a, %d %b %Y %H:%M:%S %Z")
                    break
            else:
                raise ValueError(f"Could not find Last-Modified header in {headerspath}")

        with csvpath.open("r") as fh:
            reader = csv.DictReader(fh, quoting=csv.QUOTE_NONNUMERIC)
            csv_contents = [row for row in reader]
            all_field_names.update(reader.fieldnames)

        results[now] = csv_contents

    str_field_names: Set[str] = set()
    int_field_names: Set[str] = set()
    float_field_names: Set[str] = set()
    # go through every column and try to cast to numeric.
    for column in all_field_names:
        is_int = True

        try:
            for result in results.values():
                for row in result:
                    if len(row[column]) == 0:
                        is_int = False
                        continue
                    try:
                        int(row[column])
                    except ValueError:
                        is_int = False
                    float(row[column])
        except ValueError:
            # something failed the cast to numeric
            str_field_names.add(column)
            continue

        for result in results.values():
            for row in result:
                if is_int:
                    row[column] = int(row[column])
                elif len(row[column]) == 0:
                    row[column] = np.nan
                else:
                    row[column] = float(row[column])
        if is_int:
            int_field_names.add(column)
        else:
            float_field_names.add(column)

    return results, str_field_names, int_field_names, float_field_names


def build_dataset(
        raw_data: Mapping[datetime, Sequence[OrderedDict[str, Any]]],
        str_field_names: Set[str],
        int_field_names: Set[str],
        float_field_names: Set[str],
        dim_field_names: Set[str],
        coord_to_dim_field_mappings: Mapping[str, str],
) -> xr.Dataset:
    data_vars: MutableMapping[str, Any] = {}
    coords: MutableMapping[str, Any] = {}

    # timestamp and fields marked as dims (i.e., zipcode) are interpreted as one dimensional coordinate variable along
    # the same dimension as it’s name.
    coords['time'] = sorted([timestamp for timestamp in raw_data.keys()])
    for dim_field_name in dim_field_names:
        coords[dim_field_name] = sorted(set(
            row[dim_field_name]
            for csv_contents in raw_data.values()
            for row in csv_contents
        ))

    for coord_field_name, dim_field_name in coord_to_dim_field_mappings.items():
        # pull the dim data and build a mapping from dim value to coord value.
        dim_values = coords[dim_field_name]
        coord_values = [None for _ in range(len(dim_values))]
        for ix, dim_value in enumerate(dim_values):
            for csv_contents in raw_data.values():
                for row in csv_contents:
                    if row[dim_field_name] == dim_value:
                        # found it!
                        coord_value = row[coord_field_name]
                        assert (coord_values[ix] is None
                                or coord_values[ix] == coord_value
                                or (np.isnan(coord_values[ix]) and np.isnan(coord_value)))
                        coord_values[ix] = coord_value

        coords[coord_field_name] = (dim_field_name, coord_values)

    dims = {
        coord_name: coord_values
        for coord_name, coord_values in coords.items()
        if not isinstance(coord_values, tuple)
    }
    for field_name in int_field_names:
        if field_name in dim_field_names or field_name in coord_to_dim_field_mappings:
            continue
        data_vars[field_name] = (
            list(dims.keys()),
            np.zeros(
                shape=[len(dim_values) for dim_values in dims.values()],
                dtype=np.int,
            ),
        )
    for field_name in float_field_names:
        if field_name in dim_field_names or field_name in coord_to_dim_field_mappings:
            continue
        data_vars[field_name] = (
            list(dims.keys()),
            np.full(
                shape=[len(dim_values) for dim_values in dims.values()],
                fill_value=np.nan,
                dtype=np.float64,
            ),
        )

    ds = xr.Dataset(data_vars, coords)

    field_names_to_update = int_field_names.union(float_field_names).difference(dim_field_names).difference(coord_to_dim_field_mappings.keys())
    for timestamp, csv_contents in raw_data.items():
        for row in csv_contents:
            selectors = {'time': timestamp}
            for dim_name in dims.keys():
                if dim_name == 'time':
                    continue
                selectors[dim_name] = row[dim_name]

            for field_name in field_names_to_update:
                ds[field_name].loc[selectors] = row[field_name]

    return ds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--interact", action="store_true")
    parser.add_argument("-o", "--output")
    parser.add_argument("--dim", action="append", default=[])
    parser.add_argument("--coord-to-dim", action="append", default=[])

    args = parser.parse_args()

    dims = set(args.dim)
    coords_to_dims = dict(coord_to_dim.split(":") for coord_to_dim in args.coord_to_dim)

    data, str_field_names, int_field_names, float_field_names = read_files(Path(args.path))
    ds = build_dataset(data, str_field_names, int_field_names, float_field_names, dims, coords_to_dims)

    if args.interact:
        from IPython.terminal.embed import InteractiveShellEmbed
        shell = InteractiveShellEmbed()
        shell()

    if args.output:
        ds.to_netcdf(args.output)


if __name__ == "__main__":
    main()
