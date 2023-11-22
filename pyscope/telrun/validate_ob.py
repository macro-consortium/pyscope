import configparser
import logging
import os

from astropy import coordinates as coord
from astropy import time as astrotime
from astropy import units as u

logger = logging.getLogger(__name__)


def validate_ob(block, observatory=None):
    logger.info("Validating observation block")

    if observatory is None:
        logger.warning(
            "No observatory was specified, so validation will only check for basic formatting errors."
        )

    # Check main entries
    block["target"] = str(block["target"])
    block["start time (UTC)"] = astrotime.Time(
        block["start time (UTC)"], format="iso", scale="utc"
    )
    block["end time (UTC)"] = astrotime.Time(
        block["end time (UTC)"], format="iso", scale="utc"
    )
    block["duration (minutes)"] = astrotime.TimeDelta(
        float(block["duration (minutes)"]) * u.minute
    )
    block["ra"] = coord.Angle(block["ra"], unit=u.hour)
    block["dec"] = coord.Angle(block["dec"], unit=u.deg)

    # Check standard text entry fields
    block["configuration"]["observer"] = str(block["configuration"]["observer"])
    block["configuration"]["code"] = str(block["configuration"]["code"])
    block["configuration"]["title"] = str(block["configuration"]["title"])

    if block["configuration"]["filename"] is None:
        block["configuration"]["filename"] = ""
    else:
        block["configuration"]["filename"] = str(block["configuration"]["filename"])

    # Check filter
    block["configuration"]["filter"] = str(block["configuration"]["filter"])
    if len(block["configuration"]["filter"]) > 1:
        logger.error("Filter must be a single character")
        raise ValueError("Filter must be a single character")

    # Check exposure settings
    block["configuration"]["exposure_time"] = float(
        block["configuration"]["exposure_time"]
    )
    block["configuration"]["n_exp"] = int(block["configuration"]["n_exp"])
    block["configuration"]["do_not_interrupt"] = bool(
        block["configuration"]["do_not_interrupt"]
    )
    if do_not_interrupt:
        if (
            60 * block["duration (minutes)"]
            < block["configuration"]["exposure"] * block["configuration"]["n_exp"]
        ):
            logger.error("Insufficient time to complete exposures allocated.")
            raise ValueError("Insufficient time to complete exposures allocated.")
        else:
            if (
                block["configuration"]["exposure"] != 60 * block["duration (minutes)"]
                or block["configuration"]["n_exp"] != 1
            ):
                logger.error(
                    "n_exp must be 1 and exposure must be equal to duration if do_not_interrupt is False."
                )
                raise ValueError(
                    "n_exp must be 1 and exposure must be equal to duration if do_not_interrupt is False."
                )

    # Check repositioning
    if type(block["configuration"]["repositioning"]) is tuple:
        block["configuration"]["repositioning"] = (
            float(block["configuration"]["repositioning"][0]),
            float(block["configuration"]["repositioning"][1]),
        )
    else:
        block["configuration"]["repositioning"] = bool(
            block["configuration"]["repositioning"]
        )

    # Check more camera settings
    block["configuration"]["shutter_state"] = bool(
        block["configuration"]["shutter_state"]
    )
    block["configuration"]["readout"] = int(block["configuration"]["readout"])

    # Check binning
    block["configuration"]["binning"] = (
        int(block["configuration"]["binning"][0]),
        int(block["configuration"]["binning"][1]),
    )

    # Check frame position
    block["configuration"]["frame_position"] = (
        int(block["configuration"]["frame_position"][0]),
        int(block["configuration"]["frame_position"][1]),
    )

    # Check frame_size
    block["configuration"]["frame_size"] = (
        int(block["configuration"]["frame_size"][0]),
        int(block["configuration"]["frame_size"][1]),
    )

    # Check proper motion
    block["configuration"]["pm_ra_cosdec"] = u.Quantity(
        block["configuration"]["pm_ra_cosdec"], unit=u.arcsec / u.hour
    )
    block["configuration"]["pm_dec"] = u.Quantity(
        block["configuration"]["pm_dec"], unit=u.arcsec / u.hour
    )

    # Check final status values
    block["configuration"]["comment"] = str(block["configuration"]["comment"])
    block["configuration"]["status"] = str(block["configuration"]["status"])
    block["configuration"]["message"] = str(block["configuration"]["message"])

    if observatory is not None:
        logger.info("Performing observatory-specific validation")

        # Check if source is observable
        altaz_obj = observatory.get_object_altaz(
            ra=block["ra"],
            dec=block["dec"],
            t=block["start time (UTC)"],
        )
        if altaz_obj.alt < observatory.min_altitude:
            logger.error("Target is not observable at start time")
            raise ValueError("Target is not observable at start time")

        # Check if source is observable at end time
        altaz_obj = observatory.get_object_altaz(
            ra=block["ra"],
            dec=block["dec"],
            t=block["end time (UTC)"],
        )
        if altaz_obj.alt < observatory.min_altitude:
            logger.error("Target is not observable at end time")
            raise ValueError("Target is not observable at end time")

        # Check filter
        if block["configuration"]["filter"] not in observatory.filters:
            logger.error("Filter not available")
            raise ValueError("Filter not available")

        # Check exposure time
        try:
            current_cam_state = observatory.camera.Connected
            observatory.camera.Connected = True
            if block["configuration"]["exposure_time"] > observatory.camera.ExposureMax:
                logger.error("Exposure time exceeds maximum")
                raise ValueError("Exposure time exceeds maximum")
            elif (
                block["configuration"]["exposure_time"] < observatory.camera.ExposureMin
            ):
                logger.error("Exposure time is below minimum")
                raise ValueError("Exposure time is below minimum")
            observatory.camera.Connected = current_cam_state
        except:
            logger.warning(
                "Exposure time range check failed because the driver is not available"
            )

        # Check repositioning, frame position, and frame size
        try:
            current_cam_state = observatory.camera.Connected
            observatory.camera.Connected = True
            if type(block["configuration"]["repositioning"]) is tuple:
                if (
                    block["configuration"]["repositioning"][0]
                    > observatory.camera.CameraXSize
                    or block["configuration"]["repositioning"][1]
                    > observatory.camera.CameraYSize
                ):
                    logger.error("Repositioning coordinates exceed camera size")
                    raise ValueError("Repositioning coordinates exceed camera size")
            if (
                block["configuration"]["frame_position"][0]
                + block["configuration"]["frame_size"][0]
                > observatory.camera.CameraXSize
                or block["configuration"]["frame_position"][1]
                + block["configuration"]["frame_size"][1]
                > observatory.camera.CameraYSize
            ):
                logger.error("Frame position and size exceed camera size")
                raise ValueError("Frame position and size exceed camera size")
            observatory.camera.Connected = current_cam_state
        except:
            logger.warning(
                "Repositioning check failed because the driver is not available"
            )

        # Check readout
        try:
            current_cam_state = observatory.camera.Connected
            observatory.camera.Connected = True
            if block["configuration"]["readout"] < len(observatory.camera.ReadoutModes):
                logger.error("Readout mode not available")
                raise ValueError("Readout mode not available")
            observatory.camera.Connected = current_cam_state
        except:
            logger.warning(
                "Readout mode check failed because the driver is not available"
            )

        # Check binning
        try:
            current_cam_state = observatory.camera.Connected
            observatory.camera.Connected = True
            if block["configuration"]["binning"][0] > observatory.camera.MaxBinX:
                logger.error("Binning exceeds maximum in X")
                raise ValueError("Binning exceeds maximum in X")
            if block["configuration"]["binning"][1] > observatory.camera.MaxBinY:
                logger.error("Binning exceeds maximum in Y")
                raise ValueError("Binning exceeds maximum in Y")
            if (
                block["configuration"]["binning"][0]
                != block["configuration"]["binning"][1]
                and not observatory.camera.CanAsymmetricBin
            ):
                logger.error("Binning must be square")
                raise ValueError("Binning must be square")
            observatory.camera.Connected = current_cam_state
        except:
            logger.warning("Binning check failed because the driver is not available")

    return block