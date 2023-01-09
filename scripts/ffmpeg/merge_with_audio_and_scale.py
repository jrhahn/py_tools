#!/usr/bin/env python 

from os import system

if __name__ == "__main__":"
    cmd = "ffmpeg -y -i out.mp4 -i before.mp3 -shortest -c:v copy -c:a aac final.mp4"

    system(cmd)

    cmd = "ffmpeg -y -i final.mp4 -crf 20 -preset slow -c:a copy -vf scale=1920:-1 final_scaled.mp4"

    system(cmd)