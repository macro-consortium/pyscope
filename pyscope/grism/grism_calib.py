#imports and definitions
from pyscope.grism.grism_utils import *
import os,sys
import glob
from astropy.io import fits
import numpy as np
import numpy.ma as ma
from astropy.io.fits import getdata
import astropy.units as u
import astropy.constants as const
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import rotate
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.ndimage import maximum_filter1d
from scipy.signal import medfilt, find_peaks, detrend
from datetime import datetime
import smplotlib
import csv

balmer = np.array([397.0, 410.17, 434.05, 486.14, 656.45])
deg = np.pi/180.


def read_calfile(fname):
    ''' Reads grism calibration file (.csv), extracts header line, subimage box, rotation angle, 
    and coefficients to generate functions that convert pixels to wavelength and gain vs wavelength'''
    with open(fname,'r') as f:
        lines = f.read().split('\n')
        hdr_line = lines[0]
        box = [int(x) for x in lines[1].split(',')]
        angle = float(lines[2])
        wavelength_coefficients = np.array([float(x) for x in lines[3].split(',')])
        gain_coefficients = np.array([float(x) for x in lines[4].split(',')] )    
    return(hdr_line, box, angle, wavelength_coefficients, gain_coefficients)


def doCal(grism_image,cal_file,ref_wave,uncal_wave,grismres,vis):
    
    #getting uncalibrated data
    if os.path.exists(grism_image):
        im, hdr = getdata(grism_image, 0, header=True)
        object_name = hdr['OBJECT']
        obs_date = hdr['DATE-OBS']
        print(f"Found grism image: {grism_image}.")
    else:
        print('Cannot find %s, stopping' % grism_image)
        raise StopExecution  

    if os.path.exists(cal_file):
        print(f"Found calibration file: {cal_file}")
    else:
        print('Cannot find %s, stopping' % cal_file)
        raise StopExecution  

    #getting data from image and calibration file
    im, hdr = getdata(grism_image, 0, header=True)
    cal_hdr, box, rot_angle, wavelength_coefficients, gain_coefficients = read_calfile(cal_file)
    f_wave = np.poly1d(wavelength_coefficients)
    f_gain = np.poly1d(gain_coefficients)

    #getting data from image and calibration file
    cal_hdr, box, rot_angle, wavelength_coefficients, gain_coefficients = read_calfile(cal_file)
    f_wave = np.poly1d(wavelength_coefficients)
    f_gain = np.poly1d(gain_coefficients)

    #defining subimage box dimensions as specified by user
    print('Creating subimage...')
    xi,yi = im.shape
    mybox = box
    rotangle = rot_angle
    xstart,ystart,xwidth,ywidth = mybox
    print(f'Drawing box at {xstart},{ystart} with dimensions {xwidth},{ywidth}')
    print(f'Full image dimensions: {xi},{yi}')
    print(f'Rotation angle = {rotangle} deg')

    #instantiate with rotation angle and subimage box
    B = grism_utils(grism_image,cal_file,rotangle,mybox,f_wave,f_gain)

    #create subimage using optional box parameters
    subim,transim = B.create_box()
    xs,ys = subim.shape
    zmax = np.max(subim)
    print(f'Maximum ADU count in subimage = {zmax}')

    #plotting subimage
    object_name, obs_date,telescope,camera,title,im,rot_angle, box, _,_ = B.summary_info()
    if vis == True:
        fig = B.plot_box(image=transim,subim=subim,figsize =(10,10),cmap='jet',box=mybox)
        print(f'Object: {object_name}')

    #plotting uncalibrated spectrum
    print('Plotting uncalibrated spectrum...')
    B = grism_utils(grism_image,cal_file,rot_angle,mybox,f_wave,f_gain)
    object_name, obs_date,telescope,camera,title,im,rot_angle, box, _,_ = B.summary_info()

    spectrum = B.calibrate_spectrum(subim, norm=False)   

    if vis == True:
        fig = B.plot_spectrum(spectrum, xaxis='pixel', yaxis='uncal', subrange = slice(0,len(spectrum[0])),\
                    title='%s Uncalibrated Spectrum' % object_name, medavg = 5,xlims =[0,0],ylims =[0,0])
        fig2 = B.plot_spectrum(spectrum, xaxis='wave', yaxis='uncal', subrange = slice(0,len(spectrum[0])),\
                            title='%s Uncalibrated Spectrum' % object_name, medavg = 5,plot_balmer=True,xlims =[0,0],ylims =[0,0])


    # exctract spectrum information
    print('Creating spetrum object...')
    pixels, waves, amp_uncal, amp_cal = spectrum
    

    # identify and fit gaussians

    uncal_wave = np.array(uncal_wave)

    if len(uncal_wave) < 2:
        print('Must fit for at least 2 lines')
        raise StopExecution()

    up_range = 8
    down_range = 8

    def close_ind(lst, K):

        return min(range(len(lst)), key = lambda i: abs(lst[i]-K))

    peak_px = []

    print('Fitting Balmer Gaussian...')
    wave_min= []
    wave_max= []
    for i in range(len(uncal_wave)):
        wave_min.append(uncal_wave[i]-down_range)
        wave_max.append(uncal_wave[i]+up_range)
    for i in range(len(uncal_wave)):
        params, wave, amp, amp_mod = B.fit_spectral_line(spectrum,wave_min[i],wave_max[i])
        wave_ctr,wave_ctr_err,fwhm,fwhm_err,a,a_err = params
        #if np.abs(a) > 100 and fwhm > 2:
        print(f'Wave_ctr = {round(wave_ctr, 1)} +/- {round(wave_ctr_err, 1)} nm, FWHM = {round(fwhm, 1)} +/- {round(fwhm_err, 1)} nm' )
        fig = B.plot_spectral_line(wave,amp,amp_mod,wave_ctr,wave_ctr_err,fwhm,fwhm_err,color='red',title=object_name)
        ind_ctr = close_ind(waves, wave_ctr)
        px_ctr = pixels[ind_ctr]
        peak_px.append(px_ctr)

    print(f'The fitted pixel peaks are: {peak_px}, compared to the real wavelengths: {ref_wave}')
            
        
    #derive new wavelength coefficients
    print('Calculating wavelength coefficients...')
    def quadratic(x, a, b, c):
        return a * x**2 + b * x + c

    def linear(x, a, b):
        return a * x + b

    if len(uncal_wave) == 2:
        mode = linear
    else:
        mode = quadratic

    params, _ = curve_fit(mode, peak_px, ref_wave)

    print(f'new wavelength coefficients are {params}')

    #getting reference spectrum
    print('Getting reference spectrum...')
    fn = open('/Users/crinkosk/pyscope/pyscope/pyscope/grism/temp_cal/fluxes.dat')
    lines = fn.readlines()
    names = []
    for line in lines:
        name = line[0:9].replace(' ','')
        names.append(name)
        fluxes = line[10:].split()
    unique_names = list(set(names))
    data = {}
    for name in unique_names:
        flux = []
        for line in lines:
            if name == line[0:9].replace(' ',''):
                fluxline = [float(line[i:i+10]) for i in range(10,len(line)-1,10)]
                flux += fluxline
        data[name] = flux

    #plotting ref spectrum
    print('Plotting reference spectrum...')

    star = object_name

    fluxes = np.array(data[star])
    lambda1 = 351.0
    jwaves =  0.14*np.arange(len(fluxes))
    jwaves += 351.0

    if grismres=='High':
        fluxes = fluxes[1650:2680]
        jwaves = jwaves[1650:2680]

    if vis == True:
        plt.figure(1,figsize=(8,4))
        plt.plot(jwaves,fluxes,'r-')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel(r'Flux  (erg cm$^{-2}$ s$^{-1}$ Angstrom$^{-1}$)')
        plt.title('%s' % star + ' Reference Spectrum')
        plt.grid(True)

    #deriving flux calibration (gain curve)
    print('Deriving gain...')
    # make spectra the same shape
    def interpolate_data(data, new_size):
        old_size = len(data)
        x_old = np.linspace(0, 1, old_size)
        x_new = np.linspace(0, 1, new_size)
        
        interpolated_data = np.interp(x_new, x_old, data)
        
        return interpolated_data

    new_size = len(jwaves)  
    wave_interp = interpolate_data(waves, new_size)
    amp_interp = interpolate_data(amp_uncal, new_size)

    #devide spectra
    gain=amp_interp/fluxes
    x = wave_interp
    y = gain

    print('Plotting gain...')
    if vis:
        plt.figure(1,figsize=(8,4))
        plt.plot(x,y,'r-')
        #plt.ylim(0,1)
        #plt.xlim(300,750)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Gain (Data / Reference)')
        plt.title('Exact Gain')
        plt.grid(True)


    # fit gain curve to smooth polynomial 

    print('Deriving polynomial gain curve...')

    # Define the function to fit
    def polynomial_function(x, *coefficients):
        return np.polyval(coefficients, x)

    x = wave_interp
    y = gain
    degree = 8

    # Fit a polynomial to the data
    initial_guess = np.ones(degree+1)  # Initial guess for the coefficients
    coefficients, _ = curve_fit(polynomial_function, x, y, p0=initial_guess)
    fit =  polynomial_function(x, *coefficients)

    print('Plotting polynomial gain curve...')
    if vis == True:
        # Plot the original data and the fitted polynomial
        plt.scatter(x, y,s=13, label='Gain')
        plt.plot(x, fit, color='red', label=f'{degree}th Degree Polynomial')
        plt.legend()
        # plt.xlim(300,900)
        # plt.ylim(0,2e12)
        plt.xlabel('Wavelength')
        plt.ylabel('Gain (Data / Reference)')
        plt.title('Polynomial Gain Curve Fit')
    

    #Refine gain curve by removing outliers
    print('Refining gain curve...')
    # Calculate the residuals
    residuals = gain - fit

    gain2 = gain[np.abs(residuals) < .1e16]
    wave_interp2  = wave_interp[np.abs(residuals) < .1e16]

    print('Plotting refined gain...')
    if vis:
        plt.figure(1,figsize=(8,4))
        plt.plot(x,residuals,'r-',label='Residuals')
        plt.plot(x,gain,'b-',label='Exact Gain')
        plt.plot(wave_interp2,gain2,'g-',label='Refined Gain')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Gain (Data / Reference)')
        plt.title('Refining Gain')

    print('Deriving refined polynomial gain curve...')
    x2 = wave_interp2
    y2 = gain2
    degree = 8

    # Fit a polynomial to the data
    initial_guess2 = np.ones(degree+1)  # Initial guess for the coefficients
    coefficients2, _ = curve_fit(polynomial_function, x2, y2, p0=initial_guess2)
    fit2 =  polynomial_function(x2, *coefficients2)

    print('Plotting refined polynomial gain curve...')
    if vis:
        # Plot the original data and the fitted polynomial
        plt.plot(x2, y2, label='Refined Gain',c='gray')
        plt.plot(x, fit, color='red', label=f'Original Polynomial')
        plt.plot(x2, fit2, color='blue', label=f'Refined Polynomial')
        plt.legend()
        # plt.xlim(300,900)
        # plt.ylim(0,2e12)
        plt.xlabel('Wavelength')
        plt.ylabel('Gain')
        plt.title('Refined Polynomial Gain Curve Fit')

    print(f'new flux coefficients are {coefficients2}')

    #make standard sized fit for exporting
    x3 = np.linspace(0,wave_interp2[-1],len(x))
    fit3 = polynomial_function(x3,*coefficients2)


    return mybox, rotangle, x, fit, params, coefficients2
