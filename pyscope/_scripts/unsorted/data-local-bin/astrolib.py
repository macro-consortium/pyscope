# Module astrolib

''' 
Handy  utilities for coord conversion, data fitting
26 Nov 2008 RLM
09 Oct 09 add polyfitw, fit_gaussian, find_root (adapted from CARSMath lib)
11 June 2010 - add amoeba
05 Apri 2011 - add dot_prod
4 Nov 2012 add pm, rad ,-> dms and hms without using obsolete pynova library
'''


from math import *
from sys import *
import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
import ephem as ep
import datetime
from numpy.linalg import norm

# ========================================
# Radians <-> hms, dms conversion utilities
# =========================================


# Convert sexagesimal string to decimal number (e.g. "10:30:00" -> 10.5)
# Valid formats: DD.ddd, DD:MM.mmm, DD:MM:SS
# Separators: colon, underscore, space
def hms2rad(hms_str):
	import re
	result = 0
#	dms_str = hms_str.trim()
	fields = re.split(r'[: _]', hms_str)
	fields = [float(x) for x in fields]
	while len(fields) > 0:
		result = result/60.0 + fields.pop()
	rad = result*pi/12.
	return rad

def dms2rad(dms_str):
	import re
	sign = 1
	result = 0
#	dms_str = dms_str.trim()
	if dms_str[0] == "-":
		sign = -1
		dms_str = dms_str[1:]
	fields = re.split(r'[: _]', dms_str)
	fields = [float(x) for x in fields]
	while len(fields) > 0:
		result = result/60.0 + fields.pop()
	rad = sign*result*pi/180.	
	return rad
	
def rad2dms(rad):
    deg = rad*180./pi
    sign = ""
    if deg < 0: sign = "-"
    deg = abs(deg)
    dmsdeg = floor(deg)
    dmsmin = floor((deg-dmsdeg)*60.)
    dmssec = ((deg-dmsdeg)*60.-dmsmin)*60.
    return "%s%02d:%02d:%011.7f" % (sign, dmsdeg, dmsmin, dmssec)

def rad2hms(rad):
    if rad < 0: rad += 2*pi
    dhrs = rad*12./pi
    hmshrs = floor(dhrs)
    hmsmin = floor((dhrs-hmshrs)*60.)
    hmssec = ((dhrs-hmshrs)*60.-hmsmin)*60.
    return "%02d:%02d:%011.7f" % (hmshrs, hmsmin, hmssec)



# Julian date <-> date functions
# ===========================================================

# Returns current julian day
def jdnow():
	jd_now = float(ep.julian_date())
	return jd_now
	
def datenow():
    x = str(ep.now())
    ymd, ut = x.split()
    return ymd, ut

# Converts fractional year to date/time (e.g. 2012/6/1 05:35:11) and jd
def yr2datejd(yr):
	date = ep.Date(str(yr))
	jd = float(ep.julian_date(date))
	return date, jd
	
def date2jd(y,m,d,hr,min,sec):
# Get JD from a given date
	date = '%i/%i/%i %i:%i:%i' % (y,m,d,hr,min,sec)
	jd = float(ep.julian_date(date))
	return jd

# Get date from JD
def jd2date(jd):
	mjd = jd - 2415020
	date = ep.Date(mjd)
	ymd_str, ut_str = str(date).split()
	return ymd_str, ut_str

# JD to fractional year
def jd2fyear(jd):
	date = ep.Date(jd - 2415020)
	y,m,d = date.triple()
	date0 = ep.Date(str(y))  # Jan 1 at 0 UT in year y
	fyr = y + (date - date0)/365.25
	return fyr
	

def parallax(ra,dec,par,jd):
	'''
	Calculates parallax at given jd [input, output in radians]
	add results to go from heliocentric to geocentric
	'''
	n = jd - 2451545.0
	L = radians(280.466 + 0.9856474*n)
	g = radians(357.528 + 0.9856003*n)
	lam = L + radians(1.915)*sin(g) + radians(0.02)*sin(2*g)
	epsilon = radians(23.439 - 0.00000004*n)
	R = 1.00014 - 0.01671*cos(g) - 0.00014*cos(2*g)
	X = -R*cos(lam)
	Y = -R*sin(lam)*cos(epsilon)
	Z = -R*sin(lam)*sin(epsilon)
	dra = par*(X*sin(ra) - Y*cos(ra))
	ddec = par*(X*cos(ra)*sin(dec) +Y*sin(ra)*sin(dec) - Z*cos(dec))
	return dra, ddec	

def pm(jd,jd0,pm_ra,pm_dec):
    '''
    Calculates total proper motion from jd0 to jd
    pm_ra, pm_dec = annual p.m.
    output angles in same units as input (e.g. radians)
    '''
    dyr = (jd - jd0)/365.25
    dra = pm_ra * dyr; ddec = pm_dec * dyr
    return dra, ddec 
    
def dot_prod(a,b):
	c = np.dot(a,b)/(norm(a)*norm(b))
	theta = acos(c)
	return c,theta


def Ecc(M,e):
	M0 = M + e*np.sin(M) ; M1 = M + e*np.sin(M0)
	M2 = M + e*np.sin(M1); M3 = M + e*np.sin(M2)
	M4 = M + e*np.sin(M3); M5 = M + e*np.sin(M4)
	M6 = M + e*np.sin(M5); M7 = M + e*np.sin(M6)
	M8 = M + e*np.sin(M7); M9 = M + e*np.sin(M8)
	return M9
	
	
def hel_geo(ra,dec,par,jd,flag):
	'''
	Applies correction to/from helio - geocentric coords
	'''
	if flag == 'g': 
		sign = -1
	else:
		sign = 1
	dra,ddec = parallax(ra,dec,par,jd)
	ra += dra*sign/cos(dec); dec += ddec*sign
	return ra,dec

def orbit(jd,T,P,a,i,Omega,e,omega,m1,m2,Par):
	'''
	Orbit calculator: outputs position offsets from c.m., radius vector, RVs given orbital elements, input jd
	Inputs:
		jd = Julian date
		T = time of periastron passage of primary (JD)
		P = orbital period (days)
		a = semi-major axis (mas)
		i = inclination (rads)
		Omega = longitude f ascending node (rads)
		e = eccentricity
		omega = longitude of periastron of primary
		m1,m2 = masses of primary,secondary (solar masses)
		Par = parallax (mas)
	Outputs:
		alpha1[2], dec1[2] = RA, Dec offsets of primary [sec] w.r.t. center of mass (mas)
		rho1,rho2 = position vectors of primary,sec w.r.t. c.m. (mas)
		theta = position angle of secondary as viewed by primary (rads)
		nu = true anomaly (rads)
		rv1, rv2 = radial velocities of primary, secondary (km/s)		
	'''
	R = m2/(m1+m2)
	M = (2*pi/P) * (jd - T)
	E = Ecc(M,e)
	a1 = a*R; a2 = a*(1-R)
	t = 1-e*np.cos(E)
	r1 = a1*t; r2 = a2*t
	nu = 2*np.arctan( sqrt((1+e)/(1-e)) * np.tan(E/2))
	Theta = np.arctan2(np.sin(nu+omega)*np.cos(i), np.cos(nu+omega) )
	theta = np.fmod(Theta + Omega,2*pi)
	zeta = np.sqrt( np.sin(nu+omega)**2 * cos(i)**2 + np.cos(nu+omega)**2 )
	rho1 = -r1*zeta; rho2 = r2*zeta
	alpha1 = rho1 * np.sin(theta); alpha2 = rho2 * np.sin(theta)
	dec1 =   rho1 * np.cos(theta) ; dec2 =  rho2 * np.cos(theta)
	AU = 1.5e8
	K1 = -2*pi * a1 * ( sin(i)/(P*sqrt(1-e*e)) ) * AU/(Par*86400)
	K2 =  2*pi * a2 * ( sin(i)/(P*sqrt(1-e*e)) ) * AU/(Par*86400)
	t = np.cos(nu+omega) + e*np.cos(omega)
	rv1 = K1 * t
	rv2 = K2 * t
	return alpha1,alpha2,dec1,dec2,rho1,rho2,theta,nu,rv1,rv2

def orbit_phase(t,T,P):
	phase = fmod(t-T,P)/P
	if phase < 0: phase += 1
	return phase
	
def orbit1(jd,T,P,a,i,Omega,e,omega,m1,m2,Par):
	'''
	Orbit calculator: outputs position offsets from c.m., radius vector, RVs given orbital elements, input jd
	Inputs:
		jd = Julian date
		T = time of periastron passage of primary (JD)
		P = orbital period (days)
		a = semi-major axis (mas)
		i = inclination (rads)
		Omega = longitude f ascending node (rads)
		e = eccentricity
		omega = longitude of periastron of primary
		m1,m2 = masses of primary,secondary (solar masses)
		Par = parallax (mas)
	Outputs:
		alpha1[2], dec1[2] = RA, Dec offsets of primary [sec] w.r.t. center of mass (mas)
		rho1,rho2 = position vectors of primary,sec w.r.t. c.m. (mas)
		theta = position angle of secondary as viewed by primary (rads)
		nu = true anomaly (rads)
		rv1, rv2 = radial velocities of primary, secondary (km/s)		
	'''
	R = m2/(m1+m2)
	M = (2*pi/P) * (jd - T)
	E = Ecc(M,e)
	a1 = a*R; a2 = a*(1-R)
	t = 1-e*cos(E)
	r1 = a1*t; r2 = a2*t
	nu = 2*atan( sqrt((1+e)/(1-e)) * tan(E/2))
	Theta = atan2(sin(nu+omega)*cos(i), cos(nu+omega) )
	theta = fmod(Theta + Omega,2*pi)
	zeta = sqrt( sin(nu+omega)**2 * cos(i)**2 + cos(nu+omega)**2 )
	rho1 = r1*zeta; rho2 = -r2*zeta
	alpha1 = rho1 * sin(theta); alpha2 = rho2 * sin(theta)
	dec1 =   rho1 * cos(theta) ; dec2 =  rho2 * cos(theta)
	AU = 1.5e8
	K1 = 2*pi * a1 * ( sin(i)/(P*sqrt(1-e*e)) ) * AU/(Par*86400)
	K2 =  -2*pi * a2 * ( sin(i)/(P*sqrt(1-e*e)) ) * AU/(Par*86400)
	t = cos(nu+omega) + e*cos(omega)
	rv1 = K1 * t
	rv2 = K2 * t
	return alpha1,alpha2,dec1,dec2,rho1,rho2,theta,nu,rv1,rv2
	

# print "%f = %d/%d/%d %d:%d:%d" % (jd_now, result.years, result.months, result.days, result.hours, result.minutes, result.seconds)

def find_moon(jd):
	moon_xyz = ln_rect_posn()
	moon_geo = ln_get_lunar_geo_posn(jd,moon_xyz,0)
	xm = float(moon_xyz.X)
	ym = float(moon_xyz.Y)
	zm = float(moon_xyz.Z)
	return (xm, ym, zm)
'''
def gei2geo(jd,x_gei,y_gei,z_gei):
	gst_rad = ln_get_apparent_sidereal_time(jd);phi = gst_rad
	x_geo = x_gei*cos(phi) + y_gei*sin(phi)
	y_geo = x_gei*sin(phi) - y_gei*cos(phi)
	z_geo = z_gei
	gst_hms = rad_to_hms(gst_rad)
	return (gst_hms,x_geo,y_geo,z_geo)
'''


############################################################
def polyfitw(x, y, w, ndegree, return_fit=0):
   """
   Performs a weighted least-squares polynomial fit with optional error estimates.
   Inputs:
      x: The independent variable vector.
      y: The dependent variable vector.  This vector should be the same length as X.
      w: The vector of weights.  This vector should be same length as X and Y.
      ndegree: The degree of polynomial to fit.
   Outputs:
      If return_fit==0 (the default) then polyfitw returns only C, a vector of 
      coefficients of length ndegree+1.
      If return_fit!=0 then polyfitw returns a tuple (c, yfit, yband, sigma, a)
         yfit:  The vector of calculated Y's.  Has an error of + or - Yband.
         yband:  Error estimate for each point = 1 sigma.
         sigma: The standard deviation in Y units.
         a: Correlation matrix of the coefficients.

   Written by:   George Lawrence, LASP, University of Colorado, adopted to Python 2.5 RLM 8 Oct 09                
   """
   n = min(len(x), len(y)) # size = smaller of x,y
   m = ndegree + 1         # number of elements in coeff vector
   a = np.zeros((m,m),dtype=np.float)  # least square matrix, weighted matrix
   b = np.zeros(m,dtype=np.float)    # will contain sum w*y*x^j
   z = np.ones(n,dtype=np.float)     # basis vector for constant term

   a[0,0] = np.sum(w)
   b[0] = np.sum(w*y)
   for p in range(1, 2*ndegree+1):     # power loop
      z = z*x   # z is now x^p
      if (p < m):  b[p] = np.sum(w*y*z)   # b is sum w*y*x^j
      sum = np.sum(w*z)
      for j in range(max(0,(p-ndegree)), min(ndegree,p)+1):
         a[j,p-j] = sum
   a = linalg.inv(a)
   c = np.dot(b,a)
   if (return_fit == 0):
      return c     # exit if only fit coefficients are wanted

   # compute optional output parameters.
   yfit = np.zeros(n,np.float)+c[0]   # one-sigma error estimates, init
   for k in range(1, ndegree +1):
      yfit = yfit + c[k]*(x**k)  # sum basis vectors
   var = np.sum((yfit-y)**2 )/(n-m)  # variance estimate, unbiased
   sigma = np.sqrt(var)
   yband = np.zeros(n,dtype=np.float) + a[0,0]
   z = np.ones(n,dtype=np.float)
   for p in range(1,2*ndegree+1):     # compute correlated error estimates on y
      z = z*x		# z is now x^p
      sum = 0.
      for j in range(max(0, (p - ndegree)), min(ndegree, p)+1):
         sum = sum + a[j,p-j]
      yband = yband + sum * z      # add in all the error sources
   yband = yband*var
   yband = np.sqrt(yband)
   return c, yfit, yband, sigma, a

############################################################
def fit_gaussian(chans, counts):
   """
   Fits a peak to a Gaussian using a linearizing method
   Returns (amplitude, centroid, fwhm).
   Inputs:
      chans: An array of x-axis coordinates, typically channel numbers
      counts:An array of y-axis coordinates, typically counts or intensity
   Outputs:
      Returns a tuple(amplitude, centroid, fwhm)
      amplitude: The peak height of the Gaussian in y-axis units
      centroid: The centroid of the gaussian in x-axis units
      fwhm: The Full Width Half Maximum (FWHM) of the fitted peak
   Method:
      Takes advantage of the fact that the logarithm of a Gaussian peak is a
      parabola.  Fits the coefficients of the parabola using linear least
      squares.  This means that the input Y values (counts)  must not be 
      negative.  Any values less than 1 are replaced by 1.
   """
   center = (chans[0] + chans[-1])/2.
   x = np.asarray(chans, dtype=np.float)-center
   y = np.log(np.clip(counts, 1, max(counts)))
   w = np.asarray(counts, dtype=np.float)**2
   w = np.clip(w, 1., max(w))
   fic = polyfitw(x, y, w, 2)
   fic[2] = min(fic[2], -.001)  # Protect against divide by 0
   amplitude = np.exp(fic[0] - fic[1]**2/(4.*fic[2]))
   centroid  = center - fic[1]/(2.*fic[2])
   sigma     = np.sqrt(-1/(2.*fic[2]))
   fwhm      = 2.35482 * sigma
   return amplitude, centroid, fwhm

def compress_array(array, compress):
   """
   Compresses an 1-D array by the integer factor "compress".  
   Temporary fix until the equivalent of IDL's 'rebin' is found.
   """
   l = len(array)
   if ((l % compress) != 0):
      print 'Compression must be integer divisor of array length'
      return array

   temp = np.resize(array, (l/compress, compress))
   return np.sum(temp, 1)/compress

def expand_array(array, expand, sample=0):
   """
   Expands an 1-D array by the integer factor "expand".  
   if 'sample' is 1 the new array is created with sampling, if 1 then
   the new array is created via interpolation (default)
   Temporary fix until the equivalent of IDL's 'rebin' is found.
   """

   l = len(array)
   if (expand == 1): return array
   if (sample == 1): return np.repeat(array, expand)

   kernel = np.ones(expand, dtype = np.float)/expand
   # The following mimic the behavior of IDL's rebin when expanding
   temp = np.convolve(np.repeat(array, expand), kernel, mode=2)
   # Discard the first "expand-1" entries
   temp = temp[expand-1:]
   # Replace the last "expand" entries with the last entry of original
   for i in range(1,expand): temp[-i]=array[-1]
   return temp

def find_root(func, x0, fprime=None, args=(), tol=1.48e-8, maxiter=50):
    """
    Given a function of a single variable and a starting point,
    find a nearby zero using Newton-Raphson.
    fprime is the derivative of the function.  If not given, the
    Secant method is used.
    """
    if fprime is not None:
        p0 = x0
        for iter in range(maxiter):
            myargs = (p0,)+args
            fval = func(*myargs)
            fpval = fprime(*myargs)
            if fpval == 0:
                print "Warning: zero-derivative encountered."
                return p0
            p = p0 - func(*myargs)/fprime(*myargs)
            if abs(p-p0) < tol:
                return p
            p0 = p
    else: # Secant method
        p0 = x0
        p1 = x0*(1+1e-4)
        q0 = apply(func,(p0,)+args)
        q1 = apply(func,(p1,)+args)
        for iter in range(maxiter):
            try:                
                p = p1 - q1*(p1-p0)/(q1-q0)
            except ZeroDivisionError:
                if p1 != p0:
                    print "Tolerance of %g reached" % (p1-p0)
                return (p1+p0)/2.0
            if abs(p-p0) < tol:
                return p
            p0 = p1
            q0 = q1
            p1 = p
            q1 = apply(func,(p1,)+args)
    raise RuntimeError, "Failed to converge after %d iterations, value is %f" % (maxiter,p)

def plot2d(x,y,sigma,title,xlabel,ylabel,linetype,ngrid,plotname):
	'''
	Plots simple y vs x
	Inputs:
	x,y,sigma = arrays of x,y, y uncertainty (set =0 for no error bars)
	title, xlabel, ylabel = strings
	linetype: 0 = points, 1= line, 2= points, 3= points with lines
	ngrid: 0 = none, 1 = true
	plottype: string '' = on screen, otherwise make named ps file
	'''
	if linetype == 0: plt.plot(x, y,'o')
	if linetype == 1: plt.plot(x, y,'_')
	if linetype == 2: plt.plot(x, y,'o-')
	plt.plot(x, y,'o')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	if ngrid != 0: plt.grid(True)
	if plotname != '': plt.savefig('plotname')
	plt.show()

def chisq(y,ymod,sigma,nparams):
	npts = len(y)
	df = npts - nparams
	n = 0; chi =0
	while n < npts:
		chi += ( (y[n] - ymod[n])/sigma[n] )**2
		n += 1
	chi /= df
	return chi

def amoeba(var,scale,func,ftolerance=1.e-4,xtolerance=1.e-4,itmax=500,data=None):
    '''Use the simplex method to maximize a function of 1 or more variables.
    
       Input:
              var = the initial guess, a list with one element for each variable
              scale = the search scale for each variable, a list with one
                      element for each variable.
              func = the function to maximize.
              
       Optional Input:
              ftolerance = convergence criterion on the function values (default = 1.e-4)
              xtolerance = convergence criterion on the variable values (default = 1.e-4)
              itmax = maximum number of iterations allowed (default = 500).
              data = data to be passed to func (default = None).
              
       Output:
              (varbest,funcvalue,iterations)
              varbest = a list of the variables at the maximum.
              funcvalue = the function value at the maximum.
              iterations = the number of iterations used.

       - Setting itmax to zero disables the itmax check and the routine will run
         until convergence, even if it takes forever.
       - Setting ftolerance or xtolerance to 0.0 turns that convergence criterion
         off.  But do not set both ftolerance and xtolerance to zero or the routine
         will exit immediately without finding the maximum.
       - To check for convergence, check if (iterations < itmax).
              
       The function should be defined like func(var,data) where
       data is optional data to pass to the function.

       Example:
  		def f1(x,data=None):
			x0 = 1; x1 = -2; x2 = 4; x3 = -10
			f = exp( - ((x[0]-x0)**2 + (x[1] - x1)**2 + (x[2]-x2)**2  + (x[3] - x3)**2) )
			return f
		# ==== MAIN =====
		var_guess = [0.2,-1.8,3.7,0]
		var_scale = [0.01,0.01,0.01,0.01]     
		print amoeba(var_guess,var_scale,f1)
     
       Version 1.0 2005-March-28 T. Metcalf
               1.1 2005-March-29 T. Metcalf - Use scale in simsize calculation.
                                            - Use func convergence *and* x convergence
                                              rather than func convergence *or* x
                                              convergence.
               1.2 2005-April-03 T. Metcalf - When contracting, contract the whole
                                              simplex.
       '''

    nvar = len(var)       # number of variables in the minimization
    nsimplex = nvar + 1   # number of vertices in the simplex
    
    # first set up the simplex

    simplex = [0]*(nvar+1)  # set the initial simplex
    simplex[0] = var[:]
    for i in range(nvar):
        simplex[i+1] = var[:]
        simplex[i+1][i] += scale[i]

    fvalue = []
    for i in range(nsimplex):  # set the function values for the simplex
        fvalue.append(func(simplex[i],data=data))

    # Ooze the simplex to the maximum

    iteration = 0
    
    while 1:
        # find the index of the best and worst vertices in the simplex
        ssworst = 0
        ssbest  = 0
        for i in range(nsimplex):
            if fvalue[i] > fvalue[ssbest]:
                ssbest = i
            if fvalue[i] < fvalue[ssworst]:
                ssworst = i
                
        # get the average of the nsimplex-1 best vertices in the simplex
        pavg = [0.0]*nvar
        for i in range(nsimplex):
            if i != ssworst:
                for j in range(nvar): pavg[j] += simplex[i][j]
        for j in range(nvar): pavg[j] = pavg[j]/nvar # nvar is nsimplex-1
        simscale = 0.0
        for i in range(nvar):
            simscale += abs(pavg[i]-simplex[ssworst][i])/scale[i]
        simscale = simscale/nvar

        # find the range of the function values
        fscale = (abs(fvalue[ssbest])+abs(fvalue[ssworst]))/2.0
        if fscale != 0.0:
            frange = abs(fvalue[ssbest]-fvalue[ssworst])/fscale
        else:
            frange = 0.0  # all the fvalues are zero in this case
            
        # have we converged?
        if (((ftolerance <= 0.0 or frange < ftolerance) and    # converged to maximum
             (xtolerance <= 0.0 or simscale < xtolerance)) or  # simplex contracted enough
            (itmax and iteration >= itmax)):             # ran out of iterations
            return simplex[ssbest],fvalue[ssbest],iteration

        # reflect the worst vertex
        pnew = [0.0]*nvar
        for i in range(nvar):
            pnew[i] = 2.0*pavg[i] - simplex[ssworst][i]
        fnew = func(pnew,data=data)
        if fnew <= fvalue[ssworst]:
            # the new vertex is worse than the worst so shrink
            # the simplex.
            for i in range(nsimplex):
                if i != ssbest and i != ssworst:
                    for j in range(nvar):
                        simplex[i][j] = 0.5*simplex[ssbest][j] + 0.5*simplex[i][j]
                    fvalue[i] = func(simplex[i],data=data)
            for j in range(nvar):
                pnew[j] = 0.5*simplex[ssbest][j] + 0.5*simplex[ssworst][j]
            fnew = func(pnew,data=data)
        elif fnew >= fvalue[ssbest]:
            # the new vertex is better than the best so expand
            # the simplex.
            pnew2 = [0.0]*nvar
            for i in range(nvar):
                pnew2[i] = 3.0*pavg[i] - 2.0*simplex[ssworst][i]
            fnew2 = func(pnew2,data=data)
            if fnew2 > fnew:
                # accept the new vertex in the simplex
                pnew = pnew2
                fnew = fnew2
        # replace the worst vertex with the new vertex
        for i in range(nvar):
            simplex[ssworst][i] = pnew[i]
        fvalue[ssworst] = fnew
        iteration += 1
        #if __debug__: print ssbest,fvalue[ssbest]
