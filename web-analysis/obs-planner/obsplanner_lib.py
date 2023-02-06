'''
4 Feb 2022 RLM
This class is instantiated by obsplanner
N.B. Requires astroquery version 4.3 or higher
'''
import numpy as np
import astroplan,io

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style

import astropy.units as u
from astropy.coordinates import Angle, SkyCoord, EarthLocation, get_moon, solar_system_ephemeris, get_body

#from astropy.time import Time

from astroplan import FixedTarget, Observer, moon_illumination
from astroplan.plots import plot_airmass, plot_sky, plot_finder_image

from astroquery.simbad import Simbad
from astroquery.jplhorizons import Horizons
from astroquery.skyview import SkyView

from pytz import timezone
from time import strftime

from pprint import pprint

import warnings
warnings.filterwarnings("ignore")  # Suppress annoying warnings
matplotlib.use('agg')  # required, use a non-interactive backend

meter = 1 ; sec = 1
micron = 1e-6 *meter
deg = np.pi/180.
arcsec = np.pi/(180*3600)

planet_dict = \
{'mercury':1, 'venus':2,'mars':4,'jupiter':5,'saturn':6,'uranus':7,'neptune':8,'pluto':9}

objtype_dict = \
    {'HII':'HII Region','OpCl':'Open Star Cluster','GlCl':'Globular Star Cluster','PN':'Planetary Nebula',\
    'SNR':'Supernova remnant','LINER':'LINER Galaxy','AGN':'AGN Galaxy','Assoc*':'Stellar Association',\
    'IG':'Galaxy','GinPair':'Galaxy pair','GinGroup':'Galaxy in a group','Seyfert_2':'Seyfert Galaxy',\
    'HII_G':'Galaxy','StarburstG':'Starburst Galaxy','RfNeb':'Reflection Nebula','Cl*':'Stellar asterism',\
    'BClG':'Cluster galaxy','EmG':'Emission line galaxy','LSB_G':'Galaxy',\
    'EB*':'Eclipsing Binary','SB*':'Spectroscopic binary','SG*':'Supergiant'}

# Set up Simabd query to return needed fields
simbad = Simbad()
simbad.add_votable_fields('dim', 'main_id','flux(V)','dimensions','otype','typed_id','otype','morphtype','sptype')

class obs_planner:
    def __init__(self, telescope, camera, object_name, myfilter, fwhm, time):
        ''' Methods for calculating coordinates,rise/set times, airmass plot, etc 
        given object name and observing site. '''
        self.telescope = telescope # Name of telescope (Gemini or VAO)
        self.camera = camera
        self.myfilter = myfilter
        self.fwhm = fwhm
        self.time = time
        self.object_name = object_name
        
        if telescope == 'Gemini':
            longitude = '-110d36m06.42s' ; latitude = '+31d39m56.08s' ; elevation = 1500 * u.m
            location = EarthLocation.from_geodetic(longitude, latitude, elevation)
            obsname = 'Iowa Robotic Telescope (Gemini)'
            observer = Observer(name = obsname, location=location, timezone=timezone('US/Arizona'))
            description="Iowa Robotic Telescope at Winer Observatory"
            obscode = '857' ; self.obscode = obscode
            self.night_adu = 0.2  # Pseudo ADU/pixel/sec in G or R filter; night sky, no Moon
            self.min_elevation = 20*u.degree
            D = 0.51; f = 6.8
            self.plate_scale = D*f
        else:
            longitude = '-91d31m48.6s' ; latitude = '+41d39m40.1s' ; elevation = 200 * u.m
            location = EarthLocation.from_geodetic(longitude, latitude, elevation)
            obsname = 'Van Allen Observatory'
            observer = Observer(name = obsname, location=location, timezone=timezone('US/Central'))
            description="Van Allen Observatory at Iowa City"
            obscode = '748' ; self.obscode = obscode
            self.night_adu = 1.0 # Total guess: measure this
            self.min_elevation = 25*u.degree
            D = 0.43; f = 6.8
            self.plate_scale = D*f
        self.obsname = obsname
        self.observer = observer 
        self.obscode = obscode
        self.description = description
        
        # Camera parameters
        if '4040' in camera:
            self.RN = 2.7
            self.DC = 0.07 # Scaling from 0.3 at 0C to -20C
            self.G_high = 1.05      # (inverse) high gain, elec/ADU unbinned (2.3 binned)
            self.G_low  = 1.05/16.  # (inverse) low gain, elec/ADU unbinned (2.3 binned)
            self.pixel_size = 9 * micron  # unbinned
            self.camera_gain_modes =['Low','High','Spro']
            self.saturation_adu = {'Low':3000, 'High':3000,'Spro':55000}
            self.gains = {'Low':1/16,'High':1.05,'Spro':1.05}
            
        elif '6303' in camera:
            self.RN = 15
            self.DC = 0.04 # Scaling from 0.3 at 0C to -20C
            self.G_high = 1.05      # (inverse) high gain, elec/ADU unbinned (2.3 binned)
            self.G_low  = 1.05/16.  # (inverse) low gain, elec/ADU unbinned (2.3 binned)
            self.pixel_size = 9 * micron  # unbinned
            self.camera_gain_modes =['Default']
            self.saturation_adu = {'Default':55000}
            self.gains = {'Default':1} # True??
         
        if telescope == 'Gemini':
                self.ZPmag   = {'B':21.25, 'W':22.0, 'G':22.14, 'R':21.93, 'I':21.0, 
                 'V':21.56, 'H':18.2, 'O':18.2, 'L':23.25, '1':22.00,'8':11.1,'9':10.6,'W':21.0} # Needs verification
        elif telescope == 'VAO':
                self.ZPmag   = {'B':20.1, 'V':20.1, 'G':21.4, 'R':21.1, 'I':20.2, 
                 'V':20.1, 'H':17.6, 'O':17.6, 'L':21.8,'1':21.1,'8':9.5,'9':10.0} # Guesses ! Needs verification
        
        # Retrieve object coordinates from CDS; magnitude, and description from either Simbad or JPL Horizons
        solar_system_object = False
        try:
            # Lookup using CDS - this is more comprehensive than Simbad, but doesn't provide as much information
            target = FixedTarget.from_name(object_name, name=object_name) # Astroplan FixedTarget object
            
            # Now try SIMBAD lookup to retrieve more information
            try:
                t = simbad.query_object(object_name)
                objtype = t['OTYPE'][0]
                try:
                    objtype = objtype.decode()   # objtype is a byte or string type depending on astroquery version !
                except (UnicodeDecodeError, AttributeError):
                    pass
    
                V =  t['FLUX_V'][0]
                if hasattr(V,'mask'): V = np.nan
                sp_type = t['SP_TYPE'][0]
                if hasattr(sp_type,'mask'): sp_type ='' 
                diameter = t['GALDIM_MAJAXIS'][0]
                if hasattr(diameter,'mask'): diameter = np.nan 
                if objtype in objtype_dict: objtype = objtype_dict[objtype]
            except:
                objtype =''; V =np.nan; sp_type =''; diameter =np.nan   
            self.objtype = objtype
            self.is_extended = diameter != np.nan and diameter > 0.1
            self.magnitude = V
            self.diameter = diameter
            self.sp_type = sp_type
            
        except:
            ''' Solar system object'''
            solar_system_object = True
            
            ''' Parse object name so JPL Horizons understands it'''
            if object_name.lower() == 'moon':
                obj_id = '301'
                obj = Horizons(id=obj_id, location=self.obscode, epochs=observer.midnight(time))
                obj_table = obj.ephemerides()
                self.objtype = 'Moon'
            elif object_name.lower() in planet_dict:
                planet = '%s Barycenter' % object_name  # Planet name alone is ambiguous in lookup
                obj = Horizons(id=planet, location=self.obscode, epochs=time.jd)
                obj_table = obj.ephemerides()  # NB Astropy Table object 
                self.objtype = 'Planet'
            else:
                obj = Horizons(id=object_name,location=self.obscode, id_type='smallbody', epochs=time.jd)
                obj_table = obj.ephemerides()
                self.objtype = 'Minor solar system body'
            
            ra =  obj_table['RA'][0] 
            dec = obj_table['DEC'][0]
            target = FixedTarget(SkyCoord(ra,dec, unit="deg"), name=object_name) # Convert target to FixedTarget object
            self.is_extended = False
            self.diameter = np.nan
            self.sp_type = np.nan
            try:
                self.magnitude =  obj_table['V'][0]
            except:
                self.magnitude = np.nan
            
        self.object_name = object_name
        self.solar_system_object = solar_system_object
        self.target = target # NB target is a astroplan FixedTarget object with attributes .coord, .name
        coords = target.coord
        coords_str = coords.to_string(style ='hmsdms', precision=1, sep=':', decimal =False)
        self.coords_str = coords_str
        self.coords = coords
        self.solar_system_object = solar_system_object
        
        '''sunset, sunrise, local midnight, and rise/set times for object. '''
        sunset            = observer.twilight_evening_nautical(time, which='nearest')
        sunrise           = observer.twilight_morning_nautical(time, which='next')
        midnight          = observer.midnight(time)
        obj_rise_time     = observer.target_rise_time(sunset,coords,horizon = self.min_elevation)
        obj_transit_time  = observer.target_meridian_transit_time(sunset,coords,which='nearest')
        obj_set_time      = observer.target_set_time(sunset,coords,horizon = self.min_elevation,which='next')
        self.sunset = sunset
        self.sunrise = sunrise
        self.midnight = midnight
        self.obj_rise_time = obj_rise_time
        self.obj_transit_time = obj_transit_time
        self.obj_set_time  = obj_set_time  
       
        ''' Moon rise/set times, illumination, and angle to object'''
        self.moon           = get_moon(midnight,location=location)  # Skycoord object
        self.moon_rise_time = observer.moon_rise_time(sunset,which='nearest')
        self.moon_set_time  = observer.moon_set_time(sunset,which='next')
        self.moon_illum     = moon_illumination(sunset)     # Fraction 0->1.0
        self.moon_angle     = self.moon.separation(self.coords).deg # Degrees
        
    def set_magnitude(self,magnitude):
        ''' get user-supplied magnitude when catalog lookup fails'''
        self.magnitude = magnitude
        return
    
    def observatory_info(self):
        return self.observer, self.obsname, self.obscode, self.description, self.min_elevation.value 
    
    def object_info(self):
        return self.coords, self.coords_str, self.magnitude, self.objtype, self.is_extended, \
        self.diameter,self.sp_type, self.moon_illum, self.moon_angle, self.solar_system_object
        
    def object_up(self,ntimes_per_hr = 4):
        ''' Calculates how long target is above minimum elevation during the night'''
        dtime = (self.sunrise - self.sunset)
        dtime_hr = dtime.to_value('hr')
        ntimes = int(ntimes_per_hr * dtime_hr)
        observe_times = self.sunset + dtime * np.linspace(0,1,ntimes)
        #observe_times = [x for x in observe_times]
        object_up = [self.observer.target_is_up(t,self.coords, horizon=self.min_elevation) for t in observe_times]
        A = []
        for i,observe_time in enumerate(observe_times):
            if object_up[i]: A.append(observe_time)
        object_up_times = A
        object_up_hr = sum(object_up) / ntimes_per_hr
        return object_up_times, object_up_hr

    def rise_set_table(self):
        ''' Returns a rise/set table for Sun, Moon, Object'''
        obsname = self.obsname
        objname = self.object_name
        min_elev = self.min_elevation.value
        A = [[' ', 'UT Date/Time', 'Local', 'LST']]
        minus_12 = "-12\u00b0"
        zero_deg = "0\u00b0"
        min_elev = "%i\u00b0" % min_elev
        l1 = 'Sunset  (%s elevation)   ' % minus_12
        l2 = 'Sunrise (%s elevation)   ' % minus_12
        l3 = 'Moonrise (%s elevation)  ' % zero_deg
        l4 = 'Moonset  (%s elevation)  ' % zero_deg
        l5 = '%s Rises (>%s elevation)' % (objname, min_elev)
        l6 = '%s Transits    ' % objname
        l7 = '%s Sets (< %s elev.) ' % (objname, min_elev)
        labels = [l1,l2,l3,l4,l5,l6,l7]
        times = [self.sunset, self.sunrise, self.moon_rise_time, self.moon_set_time, \
            self.obj_rise_time, self.obj_transit_time, self.obj_set_time]
        for j,t in enumerate (times):
            ut,local,lst = self.hm(t,full = True)
            A.append([labels[j], ut, local, lst])   
        return A
          
    def coordinates_table(self, ntimes_per_hr =2):
        ''' Create a table of position vs UT (useful for solar system objects with varying coords) '''
        up_times, _ = self.object_up(ntimes_per_hr = ntimes_per_hr)
        A = [['UT Date/Time', 'J2000 Coordinates']]
        object_name = self.object_name
        for t in up_times: 
            ut,local,lst = self.hm(t,full = True)
            if self.objtype == 'Planet':
                planet = '%s Barycenter' % object_name
                obj = Horizons(id=planet, location=self.obscode, epochs=t)
            elif self.objtype == 'Minor solar system body':
                obj = Horizons(id=object_name,location=self.obscode, id_type='smallbody', epochs=t)
            ephem_table = obj.ephemerides()
            ra =  ephem_table['RA'][0]  ; dec = ephem_table['DEC'][0]
            c = SkyCoord(ra,dec, unit="deg")
            coords_str = c.to_string(style ='hmsdms', precision=1, sep=':', decimal =False)
            s = [ut,coords_str]
            A.append(s)
        return A
    
    def hm(self, time, full=False):
        '''Convert time object to hh:mm string in UT, local, and LST.  
           If full = True, express UT in yyyy-mm-dd hh:mm string '''
        if full:
            ut =  time.iso[:-7]
        else:
            ut = time.iso[11:-7]
        local = self.observer.astropy_time_to_datetime(time).strftime("%H:%M") # datetime object 
        lst   = self.observer.local_sidereal_time(time) # Astropy Angle object
        h,m,s = [int(x) for x in lst.hms]
        lst = '%02d:%02d' % (h,m)
        return ut, local,lst
    
    def airmass_plot(self):
        ''' Plots airmass of object, Moon  vs UT '''
        
        myobj = self.target # FixedTarget object
        # Moon is a Skycoord object, needs to be converted to FixedTarget
        moon_skycoord = SkyCoord(ra = self.moon.ra.deg * u.deg, dec = self.moon.dec.deg * u.deg)
        moon = FixedTarget(moon_skycoord, name='Moon')
        min_elev = self.min_elevation.value
        max_airmass = np.sin(min_elev*deg)**-1
        fig, ax = plt.subplots() # Create Axes object, pass ax to plot_airmass
        ax = plot_airmass([myobj,moon], self.observer, self.midnight, ax = ax, \
          max_airmass = max_airmass, altitude_yaxis=True, brightness_shading=True)
        ax.grid(1)
        plt.tight_layout()
        ax.legend()
        buf = io.BytesIO()
        fig.savefig(buf)
        ax.cla()
        return buf
    
    def altaz(self, time):
        #Calculate altitude, azimuth at time and  upflag (True if alt > minimum elevation
        alt = self.observer.altaz(time,self.coords).alt.deg
        az =  self.observer.altaz(time,self.coords).az.deg
        up = alt > self.min_elevation
        return (alt,az,up)

    def sky_plot(self, ntimes_per_hr = 1): 
        ''' Plot object on az-el allsky projection in hourly points'''  
        obj = FixedTarget(coord=self.coords, name=self.object_name) # Create astroplan Fixed target object
        object_up_times, object_up_hr = self.object_up(ntimes_per_hr = ntimes_per_hr)
        fig,ax = plt.subplots(subplot_kw={'projection':'polar'})  # create fig,ax objects, pass ax to plot_sky
        ax = plot_sky(obj, self.observer, object_up_times, ax=ax)
        ax.legend(loc='center left', bbox_to_anchor=(0.85, 1.0))
        buf = io.BytesIO()
        fig.savefig(buf)
        return buf


    def image_field_plot(self, fov_radius=10*u.arcmin, style_kwargs={'cmap':'gray_r'}):
        '''  Create postage-stamp DSS finder image using astroplan SkyView '''
        fig,ax = plt.subplots()
        plt.axis('off')
        try:
            ax,hdu = plot_finder_image(self.target,reticle = True,fov_radius=fov_radius, style_kwargs =style_kwargs)
            ax.patch.set_edgecolor('black')  
            ax.patch.set_linewidth('1')  
            buf = io.BytesIO()
            fig.savefig(buf)
            ax.cla()
            return buf
        except:
            return None
 
    def snr_plot(self,mode,exptimes = 2**np.linspace(-3,10,14)):
        Snr = [] ; Exptimes =[]
        myfilter = self.myfilter
        for exptime in exptimes:
            sky_mean,sky_rms, adu_sec, adu_sum, snr,adu_peak, saturation_time = self.sky_parms(mode, exptime)
            if exptime < saturation_time:
                Snr.append(snr) ; Exptimes.append(exptime)
        fig, ax = plt.subplots()  # Create a figure containing a single axes.
        ax.plot(Exptimes,Snr,'ro')  # Plot some data on the axes.
        ax.plot(Exptimes,Snr,'k--')
        title = 'SNR vs. time (Gain mode: %s, Filter %s, Mag = %.1f' % (mode,myfilter,self.magnitude)
        ax.set_title(title)
        ax.set_xlabel('Exposure time [sec]')
        ax.set_ylabel('SNR')
        ax.grid()
        buf = io.BytesIO()
        fig.savefig(buf)
        return buf
    
    def sky_parms(self, mode, exptime):
        ''' Sky brightness and RMS in ADU, based on numerical fit to image data at
        at variety of Moon phases and angular separations '''
        myfilter =self.myfilter
        night_adu = self.night_adu
        moon_angle = self.moon_angle  # degrees
        saturation_adu = self.saturation_adu[mode]
        myfilter = myfilter.upper()
        pixel_size = self.pixel_size
        plate_scale = self.plate_scale
        fwhm = self.fwhm # radians
        fwhm_pixel = fwhm * plate_scale / pixel_size
        npixel = 1.75 * np.pi * (fwhm_pixel/2)**2
        
        moon_illum = self.moon_illum  # 0->1.0
        RN = self.RN
        if mode =='Spro' : RN *= 4
        if mode == 'Low':
            G = self.G_low
        else:
            G = self.G_high  
        # factor to account for filter width - m/l guesses
        fw = {'L':2,'B':0.5,'G':1.0,'R':1.0,'V':0.5,'H':0.04,'O':0.04,'1':0.04,'8':1,'9':1,'W':0.75} 
        angle = np.where(moon_angle>90,90, moon_angle)
        fmoon = 4 * moon_illum * (1./(angle*deg)) **2  # empirical! 
        night_sky =  G * fw[myfilter] * night_adu * exptime  
        moon_mean =  G * fw[myfilter] * fmoon * exptime  
        moon_mean = np.where(angle>90,0,moon_mean)
        sky_mean  = G * ( moon_mean + night_sky + (RN) ) 
        sky_rms   = np.sqrt(moon_mean +night_sky + RN**2)
        
        adu_sec = G * 2.5**(self.ZPmag[myfilter] - self.magnitude)
        adu_sum = adu_sec *exptime
        #snr = adu_sum / (sky_rms * npixel)
        adu_peak = adu_sum / npixel
        snr = adu_peak / sky_rms
        saturation_time = npixel *(saturation_adu / adu_sec)
        return sky_mean, sky_rms, adu_sec, adu_sum, snr, adu_peak, saturation_time
        
    def photometry_summary_table(self, mode):
        ''' Returns table of sky mean, Sky RMS;  SNR  (1,8,64,512,1024) for given gain mode, filter'''
        myfilter = self.myfilter
        exptimes = 2**np.linspace(-3,10,14)
        A = [['Exposure time ', 'Sky mean', 'Sky RMS', 'ADU sum','ADU peak','SNR'] ]
        for j,exptime in enumerate(exptimes):
            sky_mean, sky_rms, adu_sec, adu_sum, snr, adu_peak, saturation_time = self.sky_parms(mode, exptime)
            # convert to strings
            exptime = '%g' % exptime
            sky_mean,sky_rms,adu_sum,adu_peak,snr = ['%.1f' % x for x in [sky_mean,sky_rms,adu_sum,adu_peak,snr]]
            if float(exptime) < saturation_time and float(snr)> 3:
                A.append([exptime,sky_mean, sky_rms, adu_sum, adu_peak,snr])   
        return A, saturation_time