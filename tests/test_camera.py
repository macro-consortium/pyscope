import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pyscope import WCS

wcs = WCS('wcs_astrometrynet')

wcs.Solve('tests/xwg206100c.fts')