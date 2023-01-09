#!/usr/bin/env python

from PIL import Image, ImageOps
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process(file_in: Path, file_out: Path) -> None:
    logger.info(f"Processing {file_in}")
    img = Image.open(file_in)

    img_expanded = ImageOps.expand(
        image=img,
        border=2,
        fill=(0, 0, 0),
    )
    img_expanded = ImageOps.expand(
        image=img_expanded,
        border=int(img.width * 0.04),
        fill=(255, 255, 255),
    )

    with open(file_out, "wb") as fp:
        img_expanded.save(fp)


def run(
    path_input: Path,
    path_output: Path,
) -> None:

    path_output.mkdir(parents=True, exist_ok=True)

    for file in path_input.glob("*.jpg"):
        process(file_in=file, file_out=path_output / file.name)

    for file in path_input.glob("*.png"):
        process(file_in=file, file_out=path_output / file.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="addborder",
        description="adds a border to each image in the given folder",
    )

    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=False, default=None)

    args = parser.parse_args()

    path_input = Path(args.input_path)
    path_output = (
        Path(args.output_path)
        if args.output_path is not None
        else path_input / "processed"
    )

    run(path_input=path_input, path_output=path_output)
