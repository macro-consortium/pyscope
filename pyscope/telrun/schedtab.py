import configparser
import itertools
import logging
import os

import astroplan
import numpy as np
from astropy import coordinates as coord
from astropy import table
from astropy import time as astrotime
from astropy import units as u

logger = logging.getLogger(__name__)


def blocks_to_table(observing_blocks):
    """Convert a list of observing blocks to an astropy table.

    Parameters
    ----------
    observing_blocks : `list`
        A list of observing blocks.

    Returns
    -------
    table : astropy.table.Table
        An astropy table containing the observing blocks.
    """

    t = table.Table(masked=True)

    unscheduled_blocks_mask = np.array(
        [
            "target" in block and block["start_time"] is None
            for block in observing_blocks
        ]
    )

    open_slots_mask = np.array(
        [not "target" in block for block in observing_blocks]
    )

    t["ID"] = np.ma.array(
        [
            (
                block["ID"]
                if "target" in block
                else astrotime.Time.now().mjd
            )
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    # Populate simple columns
    t["name"] = [
        (
            block["name"]
            if "target" in block
            else (
                "TransitionBlock" if type(block) is not astroplan.Slot else "EmptyBlock"
            )
        )
        for block in observing_blocks
    ]

    t["start_time"] = astrotime.Time(
        np.ma.array(
            [
                (
                    block.start.mjd
                    if type(block) is astroplan.Slot
                    else 0 if block["start_time"] is None else block["start_time"].mjd
                )
                for block in observing_blocks
            ],
            mask=unscheduled_blocks_mask,
        ),
        format="mjd",
    )

    t["end_time"] = astrotime.Time(
        np.ma.array(
            [
                (
                    block.end.mjd
                    if type(block) is astroplan.Slot
                    else 0 if block["end_time"] is None else block["end_time"].mjd
                )
                for block in observing_blocks
            ],
            mask=unscheduled_blocks_mask,
        ),
        format="mjd",
    )
    # print(f"Target to hmsdms: {block.target.to_string('hmsdms')}")
    t["target"] = coord.SkyCoord(
        [
            (
                block["target"].to_string("hmsdms")
                if "target" in block
                else "0h0m0.0s -90d0m0.0s"
            )
            for block in observing_blocks
        ]
    )

    t["priority"] = np.ma.array(
        [
            block["priority"] if "target" in block else 0
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    temp_list = [
        block["observer"] if "target" in block else [""]
        for block in observing_blocks
    ]
    t["observer"] = np.ma.array(
        temp_list, mask=_mask_expander(temp_list, open_slots_mask)
    )

    t["code"] = np.ma.array(
        [
            block["code"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["title"] = np.ma.array(
        [
            block["title"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["filename"] = np.ma.array(
        [
            block["filename"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["type"] = np.ma.array(
        [
            block["type"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["backend"] = np.ma.array(
        [
            block["backend"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["filter"] = np.ma.array(
        [
            block["filter"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["exposure"] = np.ma.array(
        [
            block["exposure"] if "target" in block else 0
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )
    
    t["nexp"] = np.ma.array(
        [
            block["nexp"] if "target" in block else 0
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    temp_list = [
        block["repositioning"] if "target" in block else (0, 0)
        for block in observing_blocks
    ]
    t["repositioning"] = np.ma.array(
        temp_list, mask=_mask_expander(temp_list, open_slots_mask)
    )

    t["shutter_state"] = np.ma.array(
        [
            block["shutter_state"] if "target" in block else False
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["readout"] = np.ma.array(
        [
            block["readout"] if "target" in block else 0
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    temp_list = [
        block["binning"] if "target" in block else (1, 1)
        for block in observing_blocks
    ]
    t["binning"] = np.ma.array(
        temp_list, mask=_mask_expander(temp_list, open_slots_mask)
    )

    temp_list = [
        block["frame_position"] if "target" in block else (0, 0)
        for block in observing_blocks
    ]
    t["frame_position"] = np.ma.array(
        temp_list, mask=_mask_expander(temp_list, open_slots_mask)
    )

    temp_list = [
        block["frame_size"] if "target" in block else (0, 0)
        for block in observing_blocks
    ]
    t["frame_size"] = np.ma.array(
        temp_list, mask=_mask_expander(temp_list, open_slots_mask)
    )

    t["pm_ra_cosdec"] = np.ma.array(
        [
            (
                block["pm_ra_cosdec"].to(u.arcsec / u.hour).value
                if "target" in block
                else 0
            )
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["pm_dec"] = np.ma.array(
        [
            (
                block["pm_dec"].to(u.arcsec / u.hour).value
                if "target" in block
                else 0
            )
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["comment"] = np.ma.array(
        [
            block["comment"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["sch"] = np.ma.array(
        [
            block["sch"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["status"] = np.ma.array(
        [
            block["status"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["message"] = np.ma.array(
        [
            block["message"] if "target" in block else ""
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    t["sched_time"] = np.ma.array(
        [
            (block["sched_time"].mjd if "target" in block else 0)
            for block in observing_blocks
        ],
        mask=open_slots_mask,
    )

    # # Turn the constraints into a list of dicts
    # constraints = np.full(
    #     (
    #         len(observing_blocks),
    #         np.max(
    #             [
    #                 (
    #                     len(block)
    #                     if "target" in block and block is not None
    #                     else 0
    #                 )
    #                 for block in observing_blocks
    #             ]
    #         ),
    #     ),
    #     dict(),
    # )
    # for block_num, block in enumerate(observing_blocks):
    #     constraint_list = np.full(
    #         np.max(
    #             [
    #                 (
    #                     len(block)
    #                     if "target" in block and block is not None
    #                     else 0
    #                 )
    #                 for block in observing_blocks
    #             ]
    #         ),
    #         dict(),
    #     )
    #     if "target" in block and block is not None:
    #         for constraint_num, constraint in enumerate(block):
    #             if type(constraint) is astroplan.TimeConstraint:
    #                 constraint_dict = {
    #                     "type": "TimeConstraint",
    #                     "min": (
    #                         constraint.min.isot if constraint.min is not None else None
    #                     ),
    #                     "max": (
    #                         constraint.max.isot if constraint.max is not None else None
    #                     ),
    #                 }
    #             elif type(constraint) is astroplan.AtNightConstraint:
    #                 constraint_dict = {
    #                     "type": "AtNightConstraint",
    #                     "max_solar_altitude": (
    #                         constraint.max_solar_altitude.to(u.deg).value
    #                         if constraint.max_solar_altitude is not None
    #                         else 0
    #                     ),
    #                 }
    #             elif type(constraint) is astroplan.AltitudeConstraint:
    #                 constraint_dict = {
    #                     "type": "AltitudeConstraint",
    #                     "min": (
    #                         constraint.min.to(u.deg).value
    #                         if constraint.min is not None
    #                         else 0
    #                     ),
    #                     "max": (
    #                         constraint.max.to(u.deg).value
    #                         if constraint.max is not None
    #                         else 90
    #                     ),
    #                     "boolean_constraint": constraint.boolean_constraint,
    #                 }
    #             elif type(constraint) is astroplan.AirmassConstraint:
    #                 constraint_dict = {
    #                     "type": "AirmassConstraint",
    #                     "min": constraint.min if constraint.min is not None else 0,
    #                     "max": constraint.max if constraint.max is not None else 100,
    #                     "boolean_constraint": (
    #                         constraint.boolean_constraint
    #                         if constraint.boolean_constraint is not None
    #                         else False
    #                     ),
    #                 }
    #             elif type(constraint) is astroplan.MoonSeparationConstraint:
    #                 constraint_dict = {
    #                     "type": "MoonSeparationConstraint",
    #                     "min": (
    #                         constraint.min.to(u.deg).value
    #                         if constraint.min is not None
    #                         else 0
    #                     ),
    #                     "max": (
    #                         constraint.max.to(u.deg).value
    #                         if constraint.max is not None
    #                         else 360
    #                     ),
    #                 }
    #             elif constraint is None:
    #                 continue
    #             else:
    #                 logger.warning(
    #                     f"Constraint {constraint} is not supported and will be ignored"
    #                 )
    #                 continue
    
    #             constraint_list[constraint_num] = constraint_dict
    #     constraints[block_num] = constraint_list

    # t["constraints"] = np.ma.array(
    #     constraints, mask=_mask_expander(constraints, open_slots_mask)
    # )

    t.add_index("ID", unique=True)

    # TODO: Change string columns to handle arbitrary length strings instead of truncating

    return t


def table_to_blocks(table):
    blocks = []
    for row in table:
        # parse the constraints
        constraints = []
        for constraint in row["constraints"]:
            try:
                if constraint["type"] == "TimeConstraint":
                    constraints.append(
                        astroplan.TimeConstraint(
                            min=astrotime.Time(constraint["min"]),
                            max=astrotime.Time(constraint["max"]),
                        )
                    )
                elif constraint["type"] == "AtNightConstraint":
                    constraints.append(
                        astroplan.AtNightConstraint(
                            max_solar_altitude=constraint["max_solar_altitude"] * u.deg
                        )
                    )
                elif constraint["type"] == "AltitudeConstraint":
                    constraints.append(
                        astroplan.AltitudeConstraint(
                            min=constraint["min"] * u.deg,
                            max=constraint["max"] * u.deg,
                            boolean_constraint=constraint["boolean_constraint"],
                        )
                    )
                elif constraint["type"] == "AirmassConstraint":
                    constraints.append(
                        astroplan.AirmassConstraint(
                            min=constraint["min"],
                            max=constraint["max"],
                            boolean_constraint=constraint["boolean_constraint"],
                        )
                    )
                elif constraint["type"] == "MoonSeparationConstraint":
                    constraints.append(
                        astroplan.MoonSeparationConstraint(
                            min=constraint["min"] * u.deg,
                            max=constraint["max"] * u.deg,
                        )
                    )
                else:
                    logger.warning("Only time constraints are currently supported")
                    continue
            except:
                constraints.append(None)

        if row["ID"] is None:
            row["ID"] = astrotime.Time.now().mjd

        blocks.append(
            astroplan.ObservingBlock(
                target=astroplan.FixedTarget(row["target"]),
                duration=row["exposure"] * row["nexp"] * u.second,
                priority=row["priority"],
                name=row["name"],
                configuration={
                    "observer": row["observer"],
                    "code": row["code"],
                    "title": row["title"],
                    "filename": row["filename"],
                    "type": row["type"],
                    "backend": row["backend"],
                    "filter": row["filter"],
                    "exposure": row["exposure"],
                    "nexp": row["nexp"],
                    "repositioning": row["repositioning"],
                    "shutter_state": row["shutter_state"],
                    "readout": row["readout"],
                    "binning": row["binning"],
                    "frame_position": row["frame_position"],
                    "frame_size": row["frame_size"],
                    "pm_ra_cosdec": row["pm_ra_cosdec"],
                    "pm_dec": row["pm_dec"],
                    "comment": row["comment"],
                    "sch": row["sch"],
                    "ID": row["ID"],
                    "status": row["status"],
                    "message": row["message"],
                    "sched_time": row["sched_time"],
                },
                constraints=constraints,
            )
        )

    return blocks


def validate(schedule_table, observatory=None):
    logger.info("Validating the schedule table")

    if observatory is None:
        logger.info(
            "No observatory was specified, so validation will only check for basic formatting errors."
        )

    convert_to_blocks = False
    if type(schedule_table) is list:
        logger.info("Converting list of blocks to astropy table")
        schedule_table = blocks_to_table(schedule_table)
        convert_to_blocks = True

    assert (
        type(schedule_table) is table.Table or type(schedule_table) is table.Row
    ), "schedule_table must be an astropy table or row"

    if type(schedule_table) is table.Row:
        schedule_table = table.Table(schedule_table)

    # Check for required columns
    required_columns = [
        "name",
        "start_time",
        "end_time",
        "target",
        "priority",
        "observer",
        "code",
        "title",
        "filename",
        "type",
        "backend",
        "filter",
        "exposure",
        "nexp",
        "repositioning",
        "shutter_state",
        "readout",
        "binning",
        "frame_position",
        "frame_size",
        "pm_ra_cosdec",
        "pm_dec",
        "comment",
        "sch",
        "ID",
        "status",
        "message",
        "sched_time",
        "constraints",
    ]
    for column in required_columns:
        if column not in schedule_table.columns:
            logger.error(f"Column {column} is missing")
            raise ValueError(f"Column {column} is missing")

    # Check dtypes
    for colname in schedule_table.colnames:
        column = schedule_table[colname]
        match colname:
            case (
                "name"
                | "observer"
                | "code"
                | "title"
                | "filename"
                | "type"
                | "filter"
                | "comment"
                | "sch"
                | "status"
                | "message"
            ):
                if not np.issubdtype(column.dtype, np.dtype("U")):
                    logger.error(
                        f"Column '{column.name}' must be of type str, not {column.dtype}"
                    )
                    raise ValueError(
                        f"Column '{column.name}' must be of type str, not {column.dtype}"
                    )
            case "start_time" | "end_time":
                if type(column) is not astrotime.Time:
                    logger.error(
                        f"Column '{column.name}' must be of type astropy.time.Time, not {type(column)}"
                    )
                    raise ValueError(
                        f"Column '{column.name}' must be of type astropy.time.Time, not {type(column)}"
                    )
            case "target":
                if type(column) is not coord.SkyCoord:
                    logger.error(
                        f"Column '{column.name}' must be of type astropy.coordinates.SkyCoord, not {type(column)}"
                    )
                    raise ValueError(
                        f"Column '{column.name}' must be of type astropy.coordinates.SkyCoord, not {type(column)}"
                    )
            # case (
            #     "priority"
            #     | "nexp"
            #     | "readout"
            #     | "frame_position"
            #     | "frame_size"
            #     | "binning"
            #     | "repositioning"
            # ):
            #     if not np.issubdtype(column.dtype, np.dtype("int64")):
            #         logger.error(
            #             f"Column '{column.name}' must be of type int64, not {column.dtype}"
            #         )
            #         raise ValueError(
            #             f"Column '{column.name}' must be of type int64, not {column.dtype}"
            #         )
            case "exposure" | "pm_ra_cosdec" | "pm_dec":
                if not np.issubdtype(column.dtype, np.floating):
                    logger.error(
                        f"Column '{column.name}' must be of a float type, not {column.dtype}"
                    )
                    raise ValueError(
                        f"Column '{column.name}' must be of a float type, not {column.dtype}"
                    )
            case "shutter_state":
                if column.dtype != bool:
                    logger.error(
                        f"Column '{column.name}' must be of type bool, not {column.dtype}"
                    )
                    raise ValueError(
                        f"Column '{column.name}' must be of type bool, not {column.dtype}"
                    )

    # Obs-specific validation
    if observatory is not None:
        logger.info("Performing observatory-specific validation")
        for row in schedule_table:
            logger.info(f"Validating row {row.index}")

            if row["name"] == "TransitionBlock" or row["name"] == "EmptyBlock":
                logger.info(f"Skipping validation of {row['name']}")
                continue

            # Logging to debug and verify the input values
            logger.info(f"Target object: {row['target']}, Type: {type(row['target'])}")
            logger.info(
                f"Start time: {row['start_time']}, Type: {type(row['start_time'])}"
            )

            # Check if target is observable at start time
            altaz_obj = observatory.get_object_altaz(
                obj=row["target"],
                t=row["start_time"],
            )
            logger.info(f"AltAz Object: {altaz_obj}")
            if altaz_obj.alt < observatory.min_altitude:
                logger.error("Target is not observable at start time")
                row["status"] = "I"  # Invalid
                row["message"] = "Target is not observable at start time"
                continue

            # Check if source is observable at end time
            altaz_obj = observatory.get_object_altaz(
                obj=row["target"],
                t=row["end_time"],
            )
            if altaz_obj.alt < observatory.min_altitude:
                logger.error("Target is not observable at end time")
                row["status"] = "I"  # Invalid
                row["message"] = "Target is not observable at end time"
                continue

            # Check filter
            if len(observatory.filters) == 0:
                logger.info("No filters available, no filter check performed")
            elif row["filter"] not in observatory.filters:
                logger.error("Requested filter is not available")
                row["status"] = "I"  # Invalid
                row["message"] = "Requested filter is not available"
                continue

            # Check exposure time
            try:
                current_cam_state = observatory.camera.Connected
                observatory.camera.Connected = True
                if row["exposure"].to(u.second).value > observatory.camera.ExposureMax:
                    logger.error("Exposure time exceeds maximum")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Exposure time exceeds maximum"
                    continue
                elif (
                    row["exposure"].to(u.second).value < observatory.camera.ExposureMin
                ):
                    logger.error("Exposure time is below minimum")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Exposure time is below minimum"
                    continue
                observatory.camera.Connected = current_cam_state
            except:
                logger.warning(
                    "Exposure time range check failed because the driver is not available"
                )

            # Check repositioning, frame position, and frame size
            try:
                current_cam_state = observatory.camera.Connected
                observatory.camera.Connected = True
                if (
                    (
                        row["repositioning"][0] > observatory.camera.CameraXSize
                        or row["repositioning"][1] > observatory.camera.CameraYSize
                    )
                    and row["repositioning"] != [0, 0]
                    and row["repositioning"] != [None, None]
                ):
                    logger.error("Repositioning coordinates exceed camera size")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Repositioning coordinates exceed camera size"
                if (
                    (
                        row["frame_position"][0] + row["frame_size"][0]
                        > observatory.camera.CameraXSize
                        or row["frame_position"][1] + row["frame_size"][1]
                        > observatory.camera.CameraYSize
                    )
                    and row["frame_position"] != [0, 0]
                    and row["frame_size"] != [0, 0]
                ):
                    logger.error("Frame position and size exceed camera size")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Frame position and size exceed camera size"
                observatory.camera.Connected = current_cam_state
            except:
                logger.warning(
                    "Repositioning check failed because the driver is not available"
                )

            # Check readout
            try:
                current_cam_state = observatory.camera.Connected
                observatory.camera.Connected = True
                if row["readout"] >= len(observatory.camera.ReadoutModes):
                    logger.error("Readout mode not available")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Readout mode not available"
                observatory.camera.Connected = current_cam_state
            except:
                logger.warning(
                    "Readout mode check failed because the driver is not available"
                )

            # Check binning
            try:
                current_cam_state = observatory.camera.Connected
                observatory.camera.Connected = True
                if row["binning"][0] > observatory.camera.MaxBinX:
                    logger.error("Binning exceeds maximum in X")
                    row["status"] = "I"  # Invalid
                    row["message"] = "Binning exceeds maximum in X"
                if row["binning"][1] > observatory.camera.MaxBinY:
                    logger.error("Binning exceeds maximum in Y")
                    row["status"] = "I"
                    row["message"] = "Binning exceeds maximum in Y"
                if (
                    row["binning"][0] != row["binning"][1]
                    and not observatory.camera.CanAsymmetricBin
                ):
                    logger.error("Binning must be square")
                    row["status"] = "I"
                    row["message"] = "Binning must be square"
                observatory.camera.Connected = current_cam_state
            except:
                logger.warning(
                    "Binning check failed because the driver is not available"
                )

    if convert_to_blocks:
        logger.info("Converting astropy table back to list of blocks")
        schedule_table = table_to_blocks(schedule_table)
    return schedule_table


def _mask_expander(arr, mask):
    return np.array([[mask[i]] * len(arr[i]) for i in range(len(arr))]).ravel()
