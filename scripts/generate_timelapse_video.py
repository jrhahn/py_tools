from typing import Tuple

import argparse

import numpy as np
from PIL import Image, ExifTags
from pathlib import Path
from os import makedirs, system, remove
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import cv2

# Load the cascade
# source: https://github.com/opencv/opencv/tree/master/data/haarcascades
path_cascade = Path('.').resolve().parents[0] / 'resources' / 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(str(path_cascade))


def detect_face(
        img: Image
) -> Tuple[float, float]:
    open_cv_image = np.array(img.convert('RGB'))
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0:
        left = faces[0][0]
        top = faces[0][1]
        return left, top

    return None, None


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

    face_left, face_top = detect_face(img=img)

    diff_x = img.size[0] - target_width
    diff_y = img.size[1] - target_height

    weight_x = 0.5
    weight_y = 0.5
    if face_left is not None:
        weight_x = face_left / img.size[0]
        weight_y = face_top / img.size[1]

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
) -> Path:
    path_tmp = path_destination / 'tmp'

    # for ff in path_source.rglob('*'):
    #     if not ff.is_file():
    #         continue
    #
    #     logger.info(f"Preparing {ff} ..")
    #
    #     file_out_ = Path(str(ff).replace(str(path_source), str(path_tmp)))
    #
    #     makedirs(file_out_.parents[0], exist_ok=True)
    #
    #     img = Image.open(ff)
    #
    #     img = fix_rotation(img)
    #     img = scale_to_target_size(
    #         img=img,
    #         target_width=target_width,
    #         target_height=target_height
    #     )
    #     logger.info(f"  -> {img.size}")
    #
    #     img.save(file_out_)

    return path_tmp


def generate_file_list(
        path_source: Path,
        path_destination: Path,
        filename: str = 'filelist.txt'
) -> Path:
    path_file = path_destination / filename
    files = sorted(list(f"file '{ff}' \n" for ff in path_source.rglob('*') if ff.is_file()))

    with open(path_file, 'w') as f:
        f.writelines(files)

    return path_file


def run(
        path_source: Path,
        path_destination: Path,
        target_width: int = 1080,
        target_height: int = 1920,
        fps: int = 1
):
    makedirs(path_destination, exist_ok=True)
    logger.info(f"Reading from {path_source} ..")

    path_tmp = preprocess_images(
        path_source=path_source,
        path_destination=path_destination
    )

    path_file_list = generate_file_list(
        path_source=path_tmp,
        path_destination=path_destination
    )

    cmd = f'ffmpeg -y -r {1/fps} -f concat -safe 0 -i {path_file_list} -s {target_width}x{target_height}  -c:v libx264 -vf "fps=fps={fps}" {path_destination / "output.mp4"}'

    system(cmd)

    # remove(path_file_list)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(
    #     description='Sorts all files in a folder recursively according to '
    #                 'the date of creation by adding an index prefix to the filename'
    # )
    # parser.add_argument('--path_source', type=str, required=True, help='root folder of the files')
    # parser.add_argument('--path_destination', type=str, required=True, help='folder where the files will be written to')
    #
    # args = parser.parse_args()

    # path_source = Path(args.path_source)
    # path_destination = Path(args.path_destination)

    path_source = Path('.').resolve().parents[1] / 'py_timelapse'
    path_destination = Path('.').resolve() / 'output'

    run(
        path_source=path_source.resolve(),
        path_destination=path_destination.resolve()
    )
