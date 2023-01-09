#!/usr/bin/env python

from pathlib import Path
from os import system

if __name__ == "__main__":
    path_data = Path(".")

    threshold = 50

    with open("files.txt", "w") as fp:
        for file in path_data.glob("*.JPG"):
            fp.write(f"file {file}\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i files.txt -c:v libx264 -vf "fps=fps=30,format=yuv420p" out.mp4'

    system(cmd)
