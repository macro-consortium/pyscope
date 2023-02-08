import ephem
from iotalib import convert

def calcOffsetPx(x,y):
    scale = 0.625/60.                     # arcmin/pixel for VAO SBIG camera
    dRA_fiber = 0.87; dDec_fiber = 30.58  # Fiber offset from CCD field center
    xc = 1536; yc = 1024                  # pixel coords of CCD field center

    dRA_ccd = (xc - x)*scale			  # Correct to center of CDD and scale RA
    dDec_ccd = (yc - y)*scale			  # Correct to center of CDD and scale Dec
    dRA = dRA_fiber + dRA_ccd			  # Correct fiber offset RA
    dDec = dDec_fiber + dDec_ccd		  # Correct fiber offset Dec

    return (dRA,dDec)

def makeObsStar(ra_j2000_hours, dec_j2000_degs):
    ra_j2000_hours = convert.from_dms(ra_j2000_hours)
    dec_j2000_degs = convert.from_dms(dec_j2000_degs)
    obs = ephem.Observer()
    obs.date = e.now()
    obs.lat, obs.lon = '41.662195', '-91.532210'           # Van Allan Hall, Iowa City, Iowa, USA
    star = ephem.FixedBody()
    star._ra = convert.hours_to_rads(ra_j2000_hours)
    star._dec = convert.degs_to_rads(dec_j2000_degs)
    star.compute(obs)
    return star


def westofMeridian(ra_j2000_hours, dec_j2000_degs):
    star = makeObsStar(ra_j2000_hours, dec_j2000_degs)

    if(convert.degs_to_rads(180) > star.az > convert.degs_to_rads(0)):
        return false
    else:
        return true