import pandas as pd
import argparse
from pathlib import Path
from os import makedirs, system, remove
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run(
        path_source: Path,
        path_destination: Path,
        fps: int = 10
):
    makedirs(path_destination, exist_ok=True)
    logger.info(f"Reading from {path_source} ..")
    files = sorted(list(f'file {ff}\n' for ff in path_source.rglob('*') if ff.is_file()))

    with open(path_destination / 'imagepaths.txt', 'w') as f:
        f.writelines(files)

    cmd = f'ffmpeg -y -r 1/5 -f concat -safe 0 -i {path_destination / "imagepaths.txt"} -c:v libx264 -vf "fps={fps},format=yuv420p" {path_destination / "output.mp4"}'

    system(cmd)

    remove(path_destination / 'imagepaths.txt')

    print(files)


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
