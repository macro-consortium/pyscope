import relimport

import sys

from iotalib import talonwcs

def main():
    wcs_args = sys.argv[1:] # Remove script name from list of args
    
    talonwcs.run_wcs(*wcs_args)
    
if __name__ == "__main__":
    main()