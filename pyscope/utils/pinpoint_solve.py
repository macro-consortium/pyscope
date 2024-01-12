import logging
import os
import time

import click
from win32com.client import Dispatch

# Remove default stream handler
logging.getLogger().handlers = []

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
logger.propagate = False


def setup_logger():
    # Add a StreamHandler to log to the console
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)


def save_image(filepath):
    maxim.SaveFile(filepath, 3, False, 1)


def open_image(filepath):
    maxim.OpenFile(filepath)


def platesolve_image(filepath, new_filepath):
    open_image(filepath)
    maxim.PinPointSolve()
    logger.info(f"Attempting to solve {filepath}")
    try:
        while maxim.PinPointStatus == 3:
            time.sleep(0.1)
        if maxim.PinPointStatus == 2:
            logger.info("Solve successful")
        else:
            logger.info("Solve failed")
            maxim.PinPointStop()
    except Exception as e:
        logger.error(f"Solve failed: {e}, saving unsolved image")
    save_image(new_filepath)
    logger.info(f"Saved to {new_filepath}")


@click.command()
@click.option(
    "-i",
    "input_dir",
    type=click.Path(exists=True),
    help="""Directory containing images to solve.""",
)
@click.option(
    "-o",
    "--out-dir",
    "output_dir",
    default=None,
    type=click.Path(),
    help="""Directory to save solved images to. If not specified, solved images will be saved to the same directory as the input images.""",
)
def pinpoint_solve(input_dir, output_dir=None):
    # Add input_dir to the end of the current working directory if it is not an absolute path
    if not os.path.isabs(input_dir):
        input_dir = os.path.join(os.getcwd(), input_dir)
    if output_dir is None:
        output_dir = input_dir
    else:
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.getcwd(), output_dir)
    day_images = os.listdir(input_dir)
    day_filepaths = [os.path.join(input_dir, filename) for filename in day_images]
    new_filepaths = [os.path.join(output_dir, filename) for filename in day_images]

    global maxim
    maxim = Dispatch("Maxim.Document")

    # Create end_dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filepath, new_filepath in zip(day_filepaths, new_filepaths):
        platesolve_image(filepath, new_filepath)


if __name__ == "__main__":
    setup_logger()
    pinpoint_solve()
