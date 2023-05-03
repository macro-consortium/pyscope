# TODO
<ul>
<li>Add wcs_astrometrynet driver</li>
<li>Add observatory config option for rotator reverse</li>
<li>Add config file defaults for autofocus, recenter, flat/dark sequence</li>
<li>Add support for multi-color cameras</li>
<li>Slew to target should support solar system objects, moon</li>
<li>Add a current target variable</li>
<li>Add a last exposure shutter status variable</li>
<li>ObservingConditions updating thread</li>
<li>De-rotation thread, add to header</li>
<li>"Status" thread for slewing, dome, focuser moving, etc.</li>
<li>Complete other helper functions</li>

<li>telrun</li>
    <ul>
    <li>Add timeout config options for camera, filter wheel, mount focuser, rotator, roof/dome, weather, wcs</li>
    <li>Improve the exit handler</li>
    <li>Generate summary report of scans statuses</li>
    <li>Update telrun GUI using a new telrun_status class</li>
    <li>Change to astropy coordinates objects for all coordinates</li>
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