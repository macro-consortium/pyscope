#!/usr/bin/env python

"""
This script demonstrates how to build a pointing model using the
HTTP interface for PWI4.

It is necessary to implement the take_image() function to provide
an image from your camera upon request. The implementation could be
as simple as waiting for an image to be manually taken and for the
FITS image to be placed in the requested location.

This script also requires the PlateSolve library and star catalog.
Please contact PlaneWave Instruments for details.
"""

import time

import pwi4_client
from platesolve import platesolve

# NOTE: Replace this with the estimated arcseconds per pixel
# for an image taken with your camera.
# For PWI4 Virtual Camera, the default is 1.0 arcsec/pixel.
IMAGE_ARCSEC_PER_PIXEL = 1.0


def main():
    pwi4 = pwi4_client.PWI4()

    print("Checking connection to PWI4")
    status = pwi4.status()

    if not status.mount.is_connected:
        print("Connecting to mount")
        pwi4.mount_connect()

    status = pwi4.status()
    if not status.mount.axis0.is_enabled:
        print("Enabling axis 0")
        pwi4.mount_enable(0)
    if not status.mount.axis1.is_enabled:
        print("Enabling axis 1")
        pwi4.mount_enable(1)

    # Construct a grid of 3 x 6 = 18 Alt-Az points
    # ranging from 20 to 80 degrees Altitude, and from
    # 5 to 355 degrees Azimuth.
    points = create_point_list(3, 20, 80, 6, 5, 355)

    for alt, azm in points:
        map_point(pwi4, alt, azm)

    print("DONE!")


def create_point_list(num_alt, min_alt, max_alt, num_azm, min_azm, max_azm):
    """
    Build a grid of target points in alt-az coordinate space.
    """

    points = []

    for i in range(num_azm):
        azm = min_azm + (max_azm - min_azm) * i / float(num_azm)

        for j in range(num_alt):
            alt = min_alt + (max_alt - min_alt) * j / float(num_alt - 1)

            points.append((alt, azm))

    return points


def take_image(filename, pwi4):
    # TODO: Replace this with your own routine to take an image
    # with your camera and save a FITS file to "image.fits"
    take_image_virtualcam(filename, pwi4)


def take_image_virtualcam(filename, pwi4):
    """
    Take an artificial image using PWI4's virtual camera.
    The starfield in the image will be based on the telescope's
    current coordinates.

    (NOTE: Depends on the Kepler star catalog being installed
    in the right place!)
    """

    pwi4.virtualcamera_take_image_and_save(filename)


def map_point(pwi4, alt_degs, azm_degs):
    """
    Slew to the target Alt-Az, take an image,
    PlateSolve it, and (if successful) add to the model
    """

    print("Slewing to Azimuth %.3f, Altitude %3f..." % (azm_degs, alt_degs))
    pwi4.mount_goto_alt_az(alt_degs, azm_degs)

    while True:
        status = pwi4.status()
        if not status.mount.is_slewing:
            break
        time.sleep(0.1)

    # Confirm that we actually reached our target.
    # If, for example, the user clicked Stop in the GUI during
    # the slew, we probably don't want to continue building the model.
    status = pwi4.status()

    azm_error = abs(status.mount.azimuth_degs - azm_degs)
    alt_error = abs(status.mount.altitude_degs - alt_degs)

    if azm_error > 0.1 or alt_error > 0.1:
        raise Exception(
            "Mount stopped at azimuth %.4f, altitude %.4f, which is too far from the target %.4f, %.4f."
            % (
                status.mount.azimuth_degs,
                status.mount.altitude_degs,
                azm_degs,
                alt_degs,
            )
        )

    # Mount will be stopped after an alt-az slew, so turn
    # on sidereal tracking before taking an image
    pwi4.mount_tracking_on()

    print("Taking image...")

    take_image("image.fits", pwi4)

    print("Saved FITS image")

    print("Running PlateSolve...")
    try:
        match = platesolve("image.fits", IMAGE_ARCSEC_PER_PIXEL)
    except Exception as ex:
        print(ex.message)
        return

    pwi4.mount_model_add_point(match["ra_j2000_hours"], match["dec_j2000_degrees"])
    print("Added point")


if __name__ == "__main__":
    main()
