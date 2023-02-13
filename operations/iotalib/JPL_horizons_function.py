"""
Reference material

# These work
s = 'Ceres'
s = 'Juno'
s = '1'
s = '3552'
s = '52768'
s = '109109'
s = '363599'
s = 'C/2019 Y4 (ATLAS)'

# These do not work
'''
s = '52768 (1998 OR2)' ; id_type ='smallbody'
s = '1P/Halley' ; id_type ='comet_name'
s = '1P/Halley'
s = '1/P Halley'
s = '363599 2004 FG11' ; id_type ='asteroid_name'
s = '2019 Y4' ; id_type = ''
s = 'C/2017 T2 (PANSTARRS)' ; id_type = 'smallbody'
s = 'C/2017 T2' ; id_type = 'comet_name'
'''
# Calculate object
obj = Horizons(id=s,location='857', id_type = id_type, epochs=2459000.5)
eph = obj.ephemerides()

# Report ICRF coords and rates
ra  = np.array(eph['RA'])[0]
dec = np.array(eph['DEC'])[0]
ra_rate = np.array(eph['RA_rate'].to('arcsec/s'))[0]
dec_rate = np.array(eph['DEC_rate'].to('arcsec/s'))[0]

# Print results
print 'Date = %s' % eph['datetime_str'][0]
print 'Object = %s' % eph['targetname'][0]
print 'RA =  %.4f deg, RA rate = %.4f arcsec/sec' % (ra,ra_rate)
print 'Dec = %.4f deg, Dec rate = %.4f arcsec/sec' % (dec,dec_rate)
"""


from astroquery.jplhorizons import Horizons
import numpy as np



def query_jpl(object_id, id_type = None):
    """Queries jpl horizon site and returns tuple with (ra, dec, ra_rate [in arcsec/sec], dec_rate [in arcsec/sec])"""
    obj = horizons(id = object_id, id_type = id_type, epochs = 2459000.5)
    eph = obj.ephemerides()
    return (np.array(eph['RA'])[0], np.array(eph['DEC'])[0], np.array(eph['RA_rate'].to('arcsec/s'))[0], np.array(eph['DEC_rate'].to('arcsec/s'))[0])
