#!/usr/bin/env python

import argparse
import logging
from os import makedirs, system, remove
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from PIL import Image, ExifTags

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load the cascade
# source: https://github.com/opencv/opencv/tree/master/data/haarcascades
path_cascade = Path('.').resolve().parents[0] / 'resources' / 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(str(path_cascade))


def detect_face(
        img: Image
) -> Tuple[float, float, float, float]:
    open_cv_image = np.array(img.convert('RGB'))
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(
        image=gray,
        minSize=(int(img.size[1] / 5), int(img.size[1] / 5)),
        maxSize=(img.size[1], img.size[1])
    )

    if len(faces) > 0:
        left = min([ff[0] for ff in faces])
        right = max([ff[0] + ff[2] for ff in faces])
        top = min([ff[1] for ff in faces])
        bottom = max([ff[1] + ff[3] for ff in faces])
        return left, top, right, bottom

    return None


def scale_to_target_size(
        img: Image,
        target_width: float,
        target_height: float
) -> Image:
    img_size = img.size
    aspect = img_size[1] / img_size[0]

    aspect_tgt = target_height / target_width

    if aspect > aspect_tgt:
        # align on width and crop height
        img = img.resize((target_width, int(aspect * target_width)))
    else:
        # align on height and crop on width
        img = img.resize((int(target_height / aspect), target_height))

    face_area = detect_face(img=img)

    diff_x = img.size[0] - target_width
    diff_y = img.size[1] - target_height

    weight_x = 0.5
    weight_y = 0.5

    if face_area is not None:
        weight_x = face_area[0] / img.size[0]
        weight_y = face_area[1] / img.size[1]

    if diff_x < 0:
        raise ValueError("diffX is negative")

    if diff_y < 0:
        raise ValueError("diffY is negative")

    img_crop = img.crop(
        (
            int(diff_x * weight_x),
            int(diff_y * weight_y),
            int(diff_x * weight_x) + target_width,
            int(diff_y * weight_y) + target_height
        )
    )

    return img_crop


def fix_rotation(img: Image) -> Image:
    exif = img._getexif()

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    if exif[orientation] == 3:
        img = img.rotate(180, expand=True)
    elif exif[orientation] == 6:
        img = img.rotate(270, expand=True)
    elif exif[orientation] == 8:
        img = img.rotate(90, expand=True)

    return img


# todo make image size constant
def preprocess_images(
        path_source: Path,
        path_destination: Path,
        target_width: int = 1080,
        target_height: int = 1920
):
    for ff in path_source.rglob('*'):
        if not ff.is_file():
            continue

        logger.info(f"Preparing {ff} ..")

        file_out_ = Path(str(ff).replace(str(path_source), str(path_destination)))

        makedirs(file_out_.parents[0], exist_ok=True)

        img = Image.open(ff)

        img = fix_rotation(img)
        img = scale_to_target_size(
            img=img,
            target_width=target_width,
            target_height=target_height
        )
        logger.info(f"  -> {img.size}")

        img.save(file_out_)


def generate_file_list(
        path_source: Path,
        path_file_list: Path
) -> int:
    files = sorted([ff for ff in path_source.rglob('*') if ff.is_file()])
    lines = [f"file '{ff}' \n" for ff in files]

    num_files = len(files)

    with open(path_file_list, 'w') as f:
        f.writelines(lines)

    return num_files


def run(
        path_source: Path,
        path_destination: Path,
        path_to_music: Path,
        target_width: int = 1080,
        target_height: int = 1920,
        fps: int = 3
):
    makedirs(path_destination, exist_ok=True)
    logger.info(f"Reading from {path_source} ..")

    path_file_list = path_destination / 'filelist.txt'

    preprocess_images(
        path_source=path_source,
        path_destination=path_destination / 'tmp'
    )

    num_files = generate_file_list(
        path_source=path_destination / 'tmp',
        path_file_list=path_file_list
    )

    cmd = f'ffmpeg -y -r {fps} -f concat -safe 0 -i {path_file_list} -s {target_width}x{target_height} -c:v libx264 -vf fps=fps={fps} {path_destination / "output.mp4"}'
    system(cmd)

    duration_in_seconds = num_files / fps

    cmd = f"ffmpeg -ss 00:00:00  -t {duration_in_seconds} -i {path_destination / 'output.mp4'} -ss 0:00:00 -t {duration_in_seconds} -i {path_to_music} -map 0:v:0 -map 1:a:0 -y {path_destination / 'output_with_music.mp4'}"
    system(cmd)

    cmd = f"ffmpeg -y -i {path_destination / 'output_with_music.mp4'} -vf scale=720:1280 -c:v libx264 -crf 42 -preset veryslow -c:a copy  {path_destination / 'output_with_music_low_res.mp4'}"
    system(cmd)

    remove(path_file_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sorts all files in a folder recursively according to '
                    'the date of creation by adding an index prefix to the filename'
    )
    parser.add_argument('--path_source', type=str, required=True, help='root folder of the files')
    parser.add_argument('--path_destination', type=str, required=True, help='folder where the files will be written to')
    parser.add_argument('--path_to_music', type=str, required=True, help='filename and path to mp3 file')

    args = parser.parse_args()

    path_source = Path(args.path_source)
    path_destination = Path(args.path_destination)
    path_to_music = Path(args.path_to_music)

    run(
        path_source=path_source.resolve(),
        path_destination=path_destination.resolve(),
        path_to_music=path_to_music
    )
