#!/bin/python

#!/bin/python

from pathlib import Path
import shutil
import cv2
import numpy as np
from os import system
from skimage import io

path_data = Path('.')

threshold = 50

with open("files.txt", "w") as fp:        
    for file in path_data.glob("*.JPG"):
        fp.write(f"file {file}\n")


cmd = f'ffmpeg -y -f concat -safe 0 -i files.txt -c:v libx264 -vf "fps=fps=30,format=yuv420p" out.mp4'

system(cmd)
