#!/usr/bin/env python

import argparse
from pathlib import Path
from shutil import copy

from os import makedirs
from typing import List, Dict

import numpy as np

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def sort_files(files: List[Path]) -> Dict[Path, Path]:
    indices = np.argsort([f.stat().st_ctime for f in files])
    files_sorted = [files[ii] for ii in indices]

    return {f: f.parents[0] / f"{(ii) + 1:02d}_{f.name}" for ii, f in enumerate(files_sorted)}


def iterate_path(path_source: Path) -> Dict[Path, Path]:
    d_out = {}
    files_in_folder = []
    for file in path_source.glob('*'):

        if file.is_file():
            files_in_folder.append(file)
        else:
            d_out.update(iterate_path(path_source=file))

    d_out.update(sort_files(files_in_folder))

    return d_out


def run(
        path_source: Path,
        path_destination: Path
):
    file_mapping = iterate_path(path_source=path_source)

    for src, tgt in file_mapping.items():
        tgt_ = Path(f"{str(tgt).replace(str(path_source), str(path_destination))}")

        makedirs(tgt_.parents[0], exist_ok=True)

        logger.info(f"Copy {src} to {tgt_}")

        copy(src, tgt_)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sorts all files in a folder recursively according to '
                    'the date of creation by adding an index prefix to the filename'
    )
    parser.add_argument('--path_source', type=str, required=True, help='root folder of the files')
    parser.add_argument('--path_destination', type=str, required=True, help='folder where the files will be written to')

    args = parser.parse_args()

    path_source = Path(args.path_source)
    path_destination = Path(args.path_destination)

    run(
        path_source=path_source.resolve(),
        path_destination=path_destination.resolve()
    )
