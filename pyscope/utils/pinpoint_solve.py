import logging
import os
import platform
import time

import click

logger = logging.getLogger(__name__)


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
@click.option(
    "-v",
    "--verbose",
    count=True,
    type=click.IntRange(0, 1),
    default=0,
    help="""Verbosity level. -v prints info messages""",
)
def pinpoint_solve_cli(input_dir, output_dir=None, verbose=-1):
    """Platesolve images in input_dir and save them to output_dir using PinPoint in MaxIm. \b

    Platesolve images in input_dir and save them to output_dir. If output_dir is not specified, solved images will be saved to the same directory as the input images.
    
    CLI Usage: `python pinpoint_solve.py -i input_dir -o output_dir`

    .. Note::
        This script requires MaxIm DL to be installed on your system, as it uses the PinPoint solver in MaxIm DL. \b

    Parameters
    ----------
    input_dir : str
        Directory containing images to solve.
    output_dir : str (optional)
        Directory to save solved images to. If not specified, solved images will be saved to the same directory as the input images.
    verboxe : int (optional), default=-1
        Verbosity level. -v prints info messages

    Returns
    -------
    None

    Examples
    --------
    File directory structure::

        cwd/
            test_images/
                image1.fit
                image2.fit
                image3.fit
            solved_images/

    Command
        `python pinpoint_solve.py -i "test_images" -o "solved_images"`

    .. Note::
        You may also pass in absolute paths for `input_dir` and `output_dir`.
    """
    if verbose > -1:
        logger.setLevel(int(10 * (2 - verbose)))
        logger.addHandler(logging.StreamHandler())
    logger.debug(f"Starting pinpoint_solve_cli({input_dir}, {output_dir})")
    if platform.system() != "Windows":
        raise Exception("PinPoint is only available on Windows.")
    else:
        from win32com.client import Dispatch
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

    logger.debug(f"Finished pinpoint_solve_cli({input_dir}, {output_dir})")


pinpoint_solve = pinpoint_solve_cli.callback


# if __name__ == "__main__":
#     pinpoint_solve_cli()
