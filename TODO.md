# TODO
<ul>

<li>drivers</li>
    <ul>
    <li>autofocus_pwi</li>
    <li>observing_conditions_winer</li>
    <li>safety_monitor_winerroof</li>
    <li>SBIGUniversal</li>
    <li>wcs_pinpoint</li>
    </ul>

<li>observatory</li>
    <ul>
    <li>Double check optional ASCOM methods and properties have exception handling</li>
    <li>Set a default logging and allow for init argument/config var to change</li>
    <li>Write ObservingConditions thread method</li>
    <li>Write SafetyMonitor thread method</li>
    <li>Write de-rotation thread method, add to header</li>
    <li>Write autofocus method</li>
    <li>Write property and method docstrings</li>
    <li>Support multiple WCS solvers</li>
    <li>Maxim integration</li>
    <li>TheSkyX integration</li>
    <li>Add support for Nasymth telescopes (two backends)</li>
    </ul>

<li>Write tests</li>

<li>telrun</li>
    <ul>
    <li>Add timeout config options for camera, filter wheel, focuser, rotator, roof/dome, weather, wcs</li>
    <li>Generate summary report of scans statuses</li>
    <li>telrun_status portion of class, written to a file</li>
    <li>Update telrun GUI</li>
    <li>Change to astropy for all coordinates</li>
    </ul>

<li>schedtel</li>
    <ul>
    <li>Config file</li>
    <li>telrunfile -> telrun_file as class with sanity checks built in</li>
    <li>No edb lines/ephem dependencies</li>
    <li>Write comments to header</li>
    <li>Change ccdcalib argument</li>
    <li>Fix shutter options</li>
    <li>Change tracking to an argument instead of a comment</li>
    <li>Enable priority keyword</li>
    <li>Add support for multiple observers</li>
    <li>Check naming conventions, time ordering</li>
    <li>Timefiller function for unused time</li>
    </ul>

<li>syncfiles</li>
    <ul>
    <li>Config file</li>
    <li>Updates observatory status file</li>
    <li>Updates telrun status file</li>
    </ul>

<li>bin</li>

<li>_scripts</li>
    <ul>
    <li>setup_telrun_observatory</li>
    <li>setup_remote_operations</li>
    <li>Scheduling, reduction, analysis scripts</li>
    </ul>

<li>Add notification support</li>
    <ul>
    <li>courier.com integration</li>
    </ul>

<li>Write docs</li>
    <ul>
    <li>README.md</li>
    <li>docstring documentation</li>
    <li>Examples</li>
    <li>readthedocs</li>
    </ul>

<li>Installer setup on pip, conda</li>

<li>Integration with grism pipeline</li>

<li>Outreach and use</li>
    <ul>
    <li>Design logo</li>
    <li>Personal website</li>
    <li>Potential users and sponsors:</li>
        <ul>
        <li>RLMT/MACRO</li>
        <li>VAO/Iowa</li>
        <li>Macalester</li>
        <li>Augustana</li>
        <li>Knox</li>
        <li>Harvard</li>
        <li>UConn</li>
        <li>ALFALFA-U</li>
        <li>Diffraction Limited</li>
        <li>Planewave</li>
        <li>Sierra Remote Observatories</li>
        </ul>
    </ul>

</ul>