# TODO
<ul>
<li>Standardize driver format in classes</li>
    <ul>
    <li>camera_maxim driver</li>
    <li>filterwheel_maxim driver</li>
    <li>focuser_ascom driver</li>
    <li>autofocus_pwi driver</li>
    <li>weather_winer driver</li>
    <li>roof_winer driver</li>
    <li>wcs_pinpoint driver</li>
    </ul>

<li>telrun</li>
    <ul>
    <li>Change how config files are read</li>
    <li>Add timeout config options for camera, filter wheel, mount focuser, rotator, roof/dome, weather, wcs</li>
    <li>Move observatory connections into the main loop</li>
    <li>Improve the exit handler</li>
    <li>Custom header data as config file variables</li>
    <li>Recentering arguments as config file variables</li>
    <li>Generate summary report of scans statuses</li>
    <li>Update telrun GUI using a new telrun_status class</li>
    <li>Change to astropy coordinates objects for all coordinates</li>
    <li>Fix JPL horizons querying</li>
    </ul>

<li>schedtel</li>
    <ul>
    <li>telrunfile -> telrun_file as class with sanity checks built in</li>
    <li>No edb lines/ephem dependencies</li>
    <li>Write comments to header</li>
    <li>Change ccdcalib argument</li>
    <li>Fix shutter options</li>
    <li>Change tracking to an argument instead of a comment</li>
    <li>Enable priority keyword</li>
    <li>Add support for multiple observers</li>
    <li>Config file</li>
    <li>Check naming conventions, time ordering</li>
    </ul>

<li>Cleanup bin folder</li>

<li>Write new drivers</li>
    <ul>
    <li>camera_ascom driver</li>
    <li>filterwheel_ascom driver</li>
    <li>mount_ascom driver</li>
    <li>roof_ascom/dome_ascom driver</li>
    <li>rotator_ascom driver</li>
    <li>weather_ascom driver</li>
    <li>weather_other? driver</li>
    <li>wcs_astrometrynet driver</li>
    </ul>

<li>Names and options should be config file variables</li>
<li>Write documentation</li>

<li>Write installers:</li>
    <ul>
    <li>telrun</li>
    <li>syncfiles</li>
    <li>Bin tools</li>
    <li>Image reduction/calibration tools</li>
    </ul>

<li>Enable email and text notifications</li>
<li>Rocklister</li>
</ul>

## Done (pull request 2)
<ul>
<li>Resort order of functions</li>
</ul>

## Done (pull request 1)
<ul>
<li>In startup, check for overscan region</li>
<li>Change stow position to park position</li>
<li>Take an unsaved dark at end of night to close shutter</li>
<li>Slew to target early, wait until start time to start exposure</li>
<li>Change filter, set subframe, readout mode, and move focuser (if necessary) while slew is happening</li>
<li>Don't stop tracking at end of exposure, and check if previous scan was the same target and skip slewing if it was</li>
<li>Allow re-centering to use the current filter assuming it is not the grism, narrowbands, etc</li>
<li>Reconsider autofocus scheme</li>
        <ul>
        <li>Perform autofocus at zenith</li>
        <li>Allow scans of same target not to be interrupted by autofocus with interrupt_allowed keyword in sch files</li>
        </ul>
<li>Remove extended action values</li>
<li>Remove external command support</li>
<li>Create a scan conditions section for green-lighting</li>
    <ul>
    <li>CCD temp check</li>
    <li>New telrun file?</li>
    <li>Roof open</li>
    <li>Sun elevation</li>
    </ul>
</ul>