import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))




from pyscope import Camera, Telescope, Observatory, WCS



wcs = WCS('wcs_astrometrynet')