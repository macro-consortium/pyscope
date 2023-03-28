# TODO
<ul>
<li>telrun.py</li>
    <ul>
    <li>Change how config files are read</li>
    <li>Move observatory connections into the main loop and allow for arguments</li>
    <li>Improve the exit handler</li>
    <li>Change the sun_elevation_func and get_weather_func access functions so they aren't passed as arguments, allow for forced update on every scan</li>
    <li>Create a scan conditions section for green-lighting</li>
        <ul>
        <li>CCD temp check</li>
        <li>New telrun file?</li>
        <li>Roof open</li>
        <li>Sun elevation</li>
        </ul>
    <li>Resort order of functions</li>
    <li>Fix JPL horizons querying</li>
    <li>Change stow position to park position</li>
    <li>Take an unsaved dark at end of night to close shutter</li>
    <li>Generate summary report of scans statuses</li>
    <li>Reconsider autofocus scheme</li>
        <ul>
        <li>Perform autofocus at zenith</li>
        <li>Allow scans of same target not to be interrupted by autofocus</li>
        </ul>
    <li>Slew to target early, wait until start time to start exposure</li>
    <li>Change filter, set subframe, readout mode, and move focuser (if necessary) while slew is happening</li>
    <li>Change to astropy coordinates objects for all coordinates</li>
    <li>Separate filter switch and focuser offset functions</li>
    <li>Allow re-centering to use the current filter assuming it is not the grism, narrowbands, etc</li>
    <li>Verify that header data is not being written twice (temp, alt/az, etc)</li>
    <li>Integrate re-centering and wcs solution into single function external to telrun</li>
    <li>Recentering arguments as config file variables</li>
    <li>Don't stop tracking at end of exposure, and check if previous scan was the same target and skip slewing if it was</li>
    <li>Remove external command support</li>
    </ul>

<li>schedule sls files</li>
    <ul> 
    <li>Add support for multiple observers</li>
    <li>Write comments to header</li>
    <li>No edb lines/ephem dependencies</li>
    <li>Remove ccdcalib argument</li>
    <li>Fix shutter options</li>
    <li>Remove extended action values</li>
    <li>Enable priority keyword</li>
    <li>Change tracking to an argument instead of a comment</li>
    </ul>

<li>Standardize driver format</li>
<li>Enable email and text notifications</li>
<li>Turn all options and names into config file variables or options</li>
<li>Cleanup bin folder</li>
<li>Write documentation</li>
<li>Write installers:</li>
    <ul>
    <li>telrun</li>
    <li>synfiles</li>
    <li>Bin tools</li>
    <li>Image reduction/calibration tools</li>
    </ul>

</ul>