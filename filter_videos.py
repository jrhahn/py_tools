#!/bin/python

from pathlib import Path
import shutil
import cv2
import numpy as np
from skimage import io

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

    print(f"copied image: {file} -> {average} ")

    shutil.copy(src=file, dst=path_target / file.name)
