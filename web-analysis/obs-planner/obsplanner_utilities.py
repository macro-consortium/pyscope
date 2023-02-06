# These are convenience functions called by obsplanner
''' 18 February 2022 RLM '''

import numpy as np
import astroplan, io
from pywebio.input import input_group as input_group
from pywebio.input import TEXT
import pywebio.input as pywebio_input
from pywebio.output import put_table

import astropy.units as u
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from astroplan import FixedTarget, Observer, moon_illumination
from time import strftime

planet_dict = \
{'mercury':1, 'venus':2,'mars':4,'jupiter':5,'saturn':6,'uranus':7,'neptune':8,'pluto':9}

def set_now_ts(set_value):
    ''' callback function to set current date in get_inputs'''
    t = Time.now().iso[0:10]
    set_value(t)
    
def check_form(ans):
        ''' Looks for object in CDS (quicker) then JPL Horizons to check if it is a valid object'''
        object_name = ans['target']
        err_msg = 'Cannot find object in catalogs, try again. \
        If solar system object, check https://ssd.jpl.nasa.gov/horizons/app.html# for compatible name'
        
        if object_name.upper() == 'MOON':  # special case!
            return
        try: 
            fixed_target = FixedTarget.from_name(object_name, name=object_name)
            return
        except:
            try: 
                if object_name.lower() in planet_dict:
                    planet = '%s Barycenter' % object_name  # Planet name alone is ambiguous in lookup
                    obj = Horizons(id=planet, location=857, epochs=2450000) # location and epochs are dummies
                    obj_table = obj.ephemerides()  # NB Astropy Table object
                else:
                    obj = Horizons(id=object_name,location=857, id_type='smallbody', epochs=2450000)
                    obj_table = obj.ephemerides()
                return
            except:
                return('target', err_msg)
#put_link('Inputs (Click for compatible solar system object names'\,url='https://ssd.jpl.nasa.gov/horizons/app.html#/')  

def get_inputs():
        

        radio_dict = [ {'label':'VAO', 'value':'VAO'},
        {'label':'Gemini', 'value':'Gemini', 'selected':True}  ]
        seeing_dict = [ 
        {'label':'Poor (>3")'      , 'value':3.0},
        {'label':'Fair (2.5")'     , 'value':2.5,'selected':True},
        {'label':'Good (2.0")'     , 'value':2.0},
        {'label':'Excellent (1.5")', 'value':1.5} ]
        filter_dict = [
        {'value':'B', 'label':'Johnson-Cousins blue'},
        {'value':'V', 'label':'Green (AstroDon gen IIE)'},
        {'value':'G', 'label':'Sloan g photometric [green]','selected':True},
        {'value':'R', 'label':'Sloan r photometric [red]'},
        {'value':'I', 'label':'Sloan i photometric [near-IR]'},
        {'value':'O', 'label':'Oxygen III 500.7nm narrowband [5nm]'},
        {'value':'H', 'label':'H-alpha 656.3nm narrowband [5nm]'},
        {'value':'L', 'label':'Luminance wideband [clear]'},
        {'value':'1', 'label':'Sulpher SII 672.6nm narrowband [5nm]'},
        {'value':'W', 'label':'Longpass IR 650nm-850nm'},
        {'value':'8', 'label':'Red grism (550-700 nm)'},
        {'value':'9', 'label':'Blue grism (390-550 nm)'}]
        
        #obj_dict = [{'label':'Fixed','selected':True},{'label':'Planet'},{'label':'Asteroid, Comet'}]

        h1 = 'Object name e.g. M51, Jupiter, NGC891, coordinates: 21:04:31 +34:12:10 comet C/2019 L3, asteroid nr. 981'
        h2 = 'Choose the telescope to use'
        h3 = 'Observing date format: YYYY-MM-DD'
        input_list = [
        pywebio_input.input('Object name',  name='target',placeholder='Object name', help_text=h1, required=True),
        pywebio_input.radio(label ='Telescope',name='telescope',options=radio_dict,help_text=h2,inline=True),
        pywebio_input.input('Observing date', name='obsdate',type=TEXT, help_text=h3, required=True,\
        value = Time.now().iso[0:10], action=('Tonight', set_now_ts)),
        pywebio_input.radio(label='Filter',name='filter',options=filter_dict,required=True),
        pywebio_input.radio(label='Seeing',name='seeing',options=seeing_dict,inline=True,required=True),
        pywebio_input.checkbox(label='',name='detailed', inline=True,options=['Detailed report'])]
        # Check if object lookup was successful, if not reset form using validate
        ans = input_group('Observing inputs', input_list,  validate=check_form)
        
        object_name = ans['target']
        telescope = ans['telescope']
        obsdate = ans['obsdate']
        myfilter = ans['filter']
        seeing = ans['seeing']
        detailed = ans['detailed']
        return object_name, telescope, obsdate, myfilter, seeing, detailed
    
def hm(t,full=False):
    ''' t is an Astropy Time object '''
    if full:
        return t.iso[:-7]
    else:
        return t.iso[11:-7]

def lst_hm(t,obs):
    ''' t is an Astropy Time object '''
    lst = obs.local_sidereal_time(t) # Astropy  object
    h,m,s = [int(x) for x in lst.hms]
    lst_str = '%02d:%02d' % (h,m)
    return lst_str

def local_hm(t,obs):
    ''' t is an Astropy Time object. 
    N.B. Local time conversion is not conveniently supported in astropy ot astroplan. This took hours to figure out! '''
    local = obs.astropy_time_to_datetime(t) # datetime object  
    return local.strftime("%H:%M")

def elevation_table(B, obs, objname, time):
    ''' NB Not currently used '''
    sunset,sunrise,midnight,rise,transit,settime = B.rise_set_times(time)
    observe_times = sunset + (sunrise - sunset)*np.linspace(0, 1, 10)
    A = []
    for t in observe_times:
        coords,coords_str, V = B.coordinates(t, objname)
        alt,az,up = B.altaz(t)
        jd_str = '%.3f' % t.jd 
        a = [hm(t,full=True),jd_str,local_hm(t,obs), lst_hm(t,obs), int(alt), coords_str]
        if up:
            A.append(a)
        h = ['UT', 'JD','Local', 'LST', 'Altitude', 'Coordinates(J2000)']
    put_table(A,header = h)
    return

def get_recommendation(object_name, objtype, is_extended, B, mode, seeing, myfilter, magnitude):
    ''' Generate 3 or 4 line text message with reommendations for exposure time, suitable filters'''
    
    # First consider grism images
    if myfilter == '8' or myfilter == '9':
        s1 = 'You have selected a dispersed spectrum (grism) observation.'
        s2 = '\nThis makes estimating SNR and saturation highly dependent on spectral features.'
        s3 = '\nThe suggested exposure times should be suitable for normal stellar spectra, '
        s4 = '\nbut for emission line spectra you will need to experiment.'
        recommend_string = s1+s2+s3+s4
        return recommend_string
    
    # Next consider the Moon
    if object_name.upper() == 'MOON':
        s1 = 'The Moon is very bright and its brightness varies with phase, '
        s2 = 'so it is difficult to estimate suitable exposure times.'
        fcode = myfilter.upper()[0]
        if  fcode != '1' and fcode != 'H' and fcode != 'O':
            s3 = '\nI suggest you try a narrowband filter and short exposure time (0.125 sec --  0.5 sec).'
        else:
            s3 = '\nYou have chosen a narrowband filter, which is likely the best choice to avoid saturation.'
        recommend_string = s1+s2+s3
        return recommend_string
    
    # Next consider planets 
    if objtype == 'Planet':
        if object_name.upper() == 'VENUS':
            s1 = 'Venus is very bright (magnitude %.1f).' % magnitude
            s2 = '\nTry an exposure time 0.05 sec in H or O filter to image the planet.'
            s3 = ''
        elif object_name.upper() == 'MARS':
            s1 = 'Mars is very bright (magnitude %.1f).' % magnitude 
            s2 = '\nTry exposure time 0.05 sec in H or O filter to image the planet.' 
            s3 = '\nIf you want to image the faint satellites, try 4 sec, R filter. Note: Mars will be overexposed'
        elif object_name.upper() == 'JUPITER':
            s1 = 'Jupiter is extremely bright (magnitude %.1f).'  % magnitude 
            s2 = '\nTry exposure time 0.05 sec in H or O filter to image the planet.'
            s3 = '\nIf you wish to image the Galilean satellites, try 1 sec, R filter Note: Jupiter will be overexposed'
        elif object_name.upper() == 'SATURN':
            s1 = 'Saturn is very bright (magnitude %.1f).' % magnitude
            s2 = '\nTry an exposure time 0.25 sec in H or O filter to image the planet.'  
            s3 = '\nIf you want to image the satellites, try 1 sec, R filter. Note: Saturn will be overexposed'
        elif object_name.upper() == 'URANUS':
            s1 = 'Uranus is quite bright (magnitude %.1f).' % magnitude
            s2 = '\nTry exposure time 1 sec in H or O filter to image the planet.' 
            s3 = '\nIf you want to image the satellites, try 4 sec, R filter. Note: Uranus will be overexposed'
        elif object_name.upper() == 'NEPTUNE':  # V = 8
            s1 = 'Neptune is relatively bright (magnitude %.1f).' % magnitude
            s2 = '\nTry exposure time 1 sec in R,G,B, or V  filters to image the planet.' 
            s3 = '\nIf you want to image the satellites, try 4 sec, R filter. Note: Neptune will be overexposed'
        recommend_string = s1 + s2 + s3   
        return recommend_string
    # Extended objects
    if is_extended:  
        galaxy = 'Galaxy' in objtype
        supernova = 'Supernova' in objtype
        emission_line_object = ('HII' in objtype) or ('PN' in objtype) or ('Nebula' in objtype)
        if galaxy and magnitude < 9:
            s1 = '%s is a %s, magnitude = %i. \
        Since it is an extended object, overexposure is not a problem.' % (object_name,objtype, magnitude)
            s2 = '\nRecommended exposure time is 32 sec in G or R filter for monochrome imaging (256 s for deep imaging)'
            s3 = '\nFor color RGB-imaging, try 32 sec in B and V filters, 128 sec in H filter to highlight HII regions'
        elif galaxy and magnitude > 9:
            s1 = '%s is a %s (magnitude %i) \
        Since it is an extended object, overexposure is not a problem.' % (object_name,objtype, magnitude)
            s2 = '\nRecommended exposure time is 128 sec in G or R filter for monochrome imaging (256 s for deeper imaging)'
            s3 = '\nFor color RGB-imaging, try 128 sec in B and V filters, 256 sec in H filter to highlight HII regions'   
        elif emission_line_object and magnitude < 9:
            s1 = '%s is a bright %s with emission lines.' % (object_name,objtype)
            s2 = '\nRecommended narrow-band filters with exposure time: 32 sec per filter.'
            s3 = '\nTry narrow-band filters H (H alpha, 656nm), O (Oxygen III,500nm), 1 (SII 688nm)'
        elif emission_line_object and magnitude > 9:
            s1 = '%s is a faint %s with  emission lines.' % (object_name,objtype)
            s2 = '\nRecommended exposure time: 256 sec per filter.'
            s3 = '\nTry narrowband filters H (H alpha, 656nm), O (Oxygen III,501nm), 1 (SII 688nm)'  
        elif supernova:
            s1 = '%s is a %s with emission lines' % (object_name,objtype)
            s2  = '\nRecommended exposure time: 64 sec per filter.'
            s3 = '\nTry narrowband filters H (H alpha, 656nm), O (Oxygen III,500nm), 1 (SII 688nm)'
        else:
            s1 = '%s is a %s' % (object_name,objtype)
            if myfilter in ['L','B','V','R','G']:
                s2  = '\nTry exposure time: 16 sec for filter %s.' % myfilter
            else:
                s2  = '\nTry exposure time: 256 sec for filter %s.' % myfilter 
            s3 = '\nNote: Unable to recognize object type, so this recommendation is uncertain'
        recommend_string = s1 + s2 + s3   
        return recommend_string

    else:
        # Finally, point-like objects (stars, minor bodies): Determine snr, maximum exposure time from saturation time
        exptime = 1
        sky_mean, sky_rms, adu_sec, adu_sum, snr, adu_peak, saturation_time = B.sky_parms(mode, exptime)
        exptimes = 2**np.linspace(-3,10,14)
        t = exptimes
        if saturation_time < t[0]:
            recommend_string  = \
            '%s will saturate in less than %.2f sec. I recommend you choose another filter' % (object_name, t[0])        
        else:
            tmax = t[t < saturation_time].max()
            tmax = min(tmax,1024)
            sky_mean, sky_rms, adu_sec, adu_sum, snr, adu_peak, saturation_time = B.sky_parms(mode, tmax)
            s1 = 'The current apparent magnitude of %s is %.1f' % (object_name,magnitude)
            s2 = '\nMaximum exposure time is %.1f sec. [Filter %s, %.1f\" seeing]' % (tmax, myfilter, seeing) 
            s3 = '\nEstimated signal to noise ratio SNR = %i' % snr
            recommend_string = s1 + s2 + s3   
        return recommend_string
        
