import numpy as np

def airmass(alt):
    '''Calculates the airmass given an altitude via Pickering 2002'''
    deg = np.pi/180
    return 1/np.sin((alt/deg + 244/(165+47*(alt/deg)**1.1))*deg)