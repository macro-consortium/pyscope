"""
Wrapper around the PlaneWave PlateSolve2 utility

PlateSolve2 and the APM star catalog are available from:
http://planewave.com/downloads/software/
"""

import glob
import math
import os.path
import subprocess
import tempfile
import time

DEFAULT_PLATESOLVE_EXE_LOCATIONS = [
    r"C:\Users\kmi\Desktop\Planewave work\Code\Dave's VB6 Code\PlateSolve2\PlateSolve2.exe",
    r'C:\Program Files (x86)\PlaneWave Instruments\PlateSolve2\PlateSolve2.exe',
    r'C:\Program Files (x86)\PlaneWave Instruments\PWI3\PlateSolve2\PlateSolve2.exe'
]

_platesolve_exe_location = None

def find_default_platesolve_exe():
    """
    Search for PlateSolve2.exe in default locations when module is first imported.
    If not found, location value will remain None
    """

    global _platesolve_exe_location

    for location in DEFAULT_PLATESOLVE_EXE_LOCATIONS:
        if os.path.isfile(location):
            _platesolve_exe_location = location
            return

find_default_platesolve_exe()


def set_platesolve_exe_location(path_to_exe):
    """
    Explicitly set the location of the PlateSolve2 executable.
    This overrides any auto-detected path to PlateSolve2.exe that may have been
    discovered at startup
    """

    global _platesolve_exe_location
    _platesolve_exe_location = path_to_exe


def platesolve(filename, center_ra_j2000_hours, center_dec_j2000_degs, image_width_arcmin, image_height_arcmin, num_search_regions, autoclose_after_seconds=10):
    """
    Run PlateSolve2 on the given filename (which may include an absolute or relative path).
    
    center_ra_j2000_hours: Estimated center RA, in J2000 Hours
    center_dec_j2000_degs: Estimated center Dec, in J2000 Degrees
    image_width_arcmin: Estimated width of the image, in arcminutes. Used by PlateSolve to calculate the estimated pixel scale
    image_height_arcmin: Estimated height of the image, in arcminutes. Used by PlateSolve to calculate the estimated pixel scale
    
    """
    
    if _platesolve_exe_location is None:
        raise Exception("PlateSolve2.exe could not be found in the following locations:\n" +
                        "\n".join(DEFAULT_PLATESOLVE_EXE_LOCATIONS) + "\n" +
                        "Please install PlateSolve2 or call set_platesolve_exe_location() before calling platesolve()"
                        )

    use_new_command_line_args = True

    if not use_new_command_line_args:
        # Results file is written to the same directory and filename as the
        # FITS image, but with the file extension ".apm" instead
        results_filepath = os.path.splitext(filename)[0] + ".apm"
    else:
        results_filepath = os.path.join(tempfile.gettempdir(), "platesolve2.apm")
    
    # Delete any old results
    if os.path.exists(results_filepath):
        os.remove(results_filepath)
    
    center_ra_j2000_rads = math.radians(center_ra_j2000_hours*15)
    center_dec_j2000_rads = math.radians(center_dec_j2000_degs)

    if use_new_command_line_args:
        arcsec_per_pixel = image_width_arcmin
        arguments = "-solve,%s,%f,%f,%f,%d,%d,%s" % (
                filename,
                center_ra_j2000_rads,
                center_dec_j2000_rads,
                arcsec_per_pixel,
                num_search_regions,
                autoclose_after_seconds,
                results_filepath
                )
    else:
        image_width_rads = math.radians(image_width_arcmin/60.0)
        image_height_rads = math.radians(image_height_arcmin/60.0)

        arguments = "%f,%f,%f,%f,%d,%s,%d" % (
            center_ra_j2000_rads,
            center_dec_j2000_rads,
            image_width_rads,
            image_height_rads,
            num_search_regions,
            filename,
            autoclose_after_seconds
            )
    
    
    # Open as background process
    process = subprocess.Popen([_platesolve_exe_location, arguments])
    
    # Wait for results file to appear
    start_time = time.time()
    while time.time() - start_time < 60:
        if os.path.exists(results_filepath) and os.stat(results_filepath).st_size > 10:
            # At least partial results file has been written
            time.sleep(0.2) # One more chance for output to get flushed
            break
        
        if process.poll() != None:
            raise Exception("Error running PlateSolve: process exited prematurely")
            
        time.sleep(1)
    
    if not os.path.exists(results_filepath):
        raise Exception("Error running PlateSolve: output file not found")
    
    lines = open(results_filepath, "r").readlines()
    if len(lines) != 3:
        raise Exception("Expected 3 lines but got %d in '%s'" % (len(lines), results_filepath))
    
    fields_line1 = lines[0].strip().split(",")
    if len(fields_line1) != 3:
        raise Exception("Expected 3 fields on line 1 but got %d in '%s'" % (len(fields_line1), results_filepath))
    
    try:
        solved_ra_j2000_rads = float(fields_line1[0])
        solved_dec_j2000_rads = float(fields_line1[1])
        return_code = int(fields_line1[2])
    except ValueError:
        raise Exception("Invalid numeric value on line 1 of '%s'" % results_filepath)
    
    if return_code != 1:
        result = PlateSolveResult()
        result.return_code = return_code
        return result
    
    fields_line2 = lines[1].split(",")
    if len(fields_line2) != 5:
        raise Exception("Expected 5 fields on line 1 but got %d in '%s'" % (len(fields_line2), results_filepath))
    
    try:
        arcsec_per_pixel = float(fields_line2[0])
        rotation_angle_degs = float(fields_line2[1])
        stretch = float(fields_line2[2]) # Difference in scale factor between the X and Y axes
        skew = float(fields_line2[3]) # Measure of axis non-perpendicularity
        num_extracted_stars = int(fields_line2[4])
    except ValueError:
        raise Exception("Invalid numeric value on line 2 of '%s'" % results_filepath)
    
    solved_ra_j2000_hours = math.degrees(solved_ra_j2000_rads) / 15.0
    solved_dec_j2000_degs =  math.degrees(solved_dec_j2000_rads)
    
    result = PlateSolveResult()
    result.return_code = return_code
    result.ra_j2000_hours = solved_ra_j2000_hours
    result.dec_j2000_degs = solved_dec_j2000_degs
    result.arcsec_per_pixel = arcsec_per_pixel
    result.rotation_angle_degs = rotation_angle_degs
    result.stretch = stretch
    result.skew = skew
    result.num_extracted_stars = num_extracted_stars
    
    return result

class PlateSolveResult:
    def __init__(self):
        self.return_code = None
        self.ra_j2000_hours = None
        self.dec_j2000_degs = None
        self.arcsec_per_pixel = None
        self.rotation_angle_degs = None
        self.stretch = None
        self.skew = None
        self.num_extracted_stars = None

def test():
    print("Using " + str(_platesolve_exe_location))

    for file in glob.glob(r'C:\Users\kmi\Desktop\testimages\ra1dec10\*.fit*'):
        print(file)
        results = platesolve(file, 1, 10, .64, 0, 50)
        print("Results:")
        print("  Code:", results.return_code)
        if results.return_code == 1:
            print("  RA (J2000 hours):", results.ra_j2000_hours)
            print("  Dec (J2000 degs):", results.dec_j2000_degs)
            print("  Arcsec per pixel:", results.arcsec_per_pixel)
            print("  Rotation angle (degs):", results.rotation_angle_degs)
            print("  Stretch:", results.stretch)
            print("  Skew:", results.skew)
            print("  Extracted stars:", results.num_extracted_stars)
            print()

if __name__ == "__main__":
    test()
