import sys
from os.path import abspath, dirname, join

"""
Prepend the parent directory to the python path so that the local copy
of the code is used instead of whatever happens to be in the user's
PYTHONPATH. Hopefully prevents development code from accidentally getting 
imported in a production run.
"""

sys.path.insert(0, abspath( join(dirname(abspath(__file__)), "..") ))
