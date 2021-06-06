import pandas as pd
import argparse

from PIL import Image, ExifTags
from pathlib import Path
from os import makedirs, system, remove
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def rotate_images(
        path_source: Path,
        path_destination: Path
) -> Path:
    path_tmp = path_destination / 'tmp'

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    for ff in path_source.rglob('*'):
        if not ff.is_file():
            continue

        file_out_ = Path(str(ff).replace(str(path_source), str(path_tmp)))

        makedirs(file_out_.parents[0], exist_ok=True)

        img = Image.open(ff)

        exif = img._getexif()

        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)

        img.save(file_out_)

    return path_tmp


def generate_file_list(
        path_source: Path,
        path_destination: Path,
        filename: str = 'filelist.txt'
) -> Path:
    path_file = path_destination / filename
    files = sorted(list(f'file {ff}\n' for ff in path_source.rglob('*') if ff.is_file()))

    with open(path_file, 'w') as f:
        f.writelines(files)

    return path_file


def run(
        path_source: Path,
        path_destination: Path,
        fps: int = 10
):
    makedirs(path_destination, exist_ok=True)
    logger.info(f"Reading from {path_source} ..")

    path_tmp = rotate_images(
        path_source=path_source,
        path_destination=path_destination
    )

    path_file_list = generate_file_list(
        path_source=path_tmp,
        path_destination=path_destination
    )

    cmd = f'ffmpeg -y -f concat -safe 0 -i {path_file_list} -c:v libx264 -vf "fps=fps={fps},format=yuv420p" {path_destination / "output.mp4"}'

    system(cmd)

    remove(path_file_list)


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
