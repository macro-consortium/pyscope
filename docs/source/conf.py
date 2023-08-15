import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

from sphinx_astropy.conf.v2 import *

project = 'pyscope'
copyright = '2023, Walter Golay'
author = 'Walter Golay'
release = '0.1.0'

graphviz_dot = '/usr/local/bin/dot'