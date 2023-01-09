#!/usr/bin/env python

from pathlib import Path
import shutil
from skimage import io

import logging

logging.basicConfig
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    path_data = Path('.')
    path_target = Path('..') / 'filtered'
    path_target.mkdir(exist_ok=True)

    threshold = 50

    for file in path_data.glob("*.JPG"):
        img = io.imread(file)[:, :, :-1]

        average = img.mean().mean().mean()

        if average < threshold:
            print(f"filtered image: {file} -> {average} ")
            continue

        logger.info(f"copied image: {file} -> {average} ")

        shutil.copy(src=file, dst=path_target / file.name)
