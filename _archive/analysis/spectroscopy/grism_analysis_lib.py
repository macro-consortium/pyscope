# Class library for grism_analysis
# 25 Mar 2022 RLM
#  7 Dec 2022 Add use_velocity option to fit_gaussian

import numpy as np
import ccdproc as ccdp
from astropy.io.fits import getdata
from scipy.ndimage.interpolation import rotate
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.interpolate import interp1d
from scipy.signal import medfilt, medfilt2d
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from datetime import datetime
import matplotlib.pyplot as plt
import sys

class grism_tools:
    def __init__(self, grism_image, cal_file, ref_file='', subimage_box=[0,0,0,0],ywidth=30):
        ''' Utilities for calibrating and plotting spectra from grism images'''
        
        self.grism_image = grism_image
        self.cal_file = cal_file
        self.balmer = np.array([397.0, 410.17, 434.05, 486.14, 656.45])
        
        ''' Open image, extract header information '''
        im, hdr = getdata(grism_image, 0, header=True)
        self.object    =  hdr['OBJECT']
        self.utdate    =  hdr['DATE-OBS'][:-3].replace('T',' ')
        self.telescope =  hdr['TELESCOP']
        self.instrument = hdr['INSTRUME']
        
        # Flip image so L-> R corresponds to short -> long wavelength                     
        im = np.fliplr(im)
        
        # Crack filter codes
        fil = hdr['FILTER'][0]
        if fil == '6': self.filter = '6'
        if fil == '8': self.filter = 'R'
        if fil == '9': self.filter = 'B'
        
        # Create default plot title
        self.title = '%s\n%s %s grism: %s' % \
        (self.object, self.telescope, self.utdate, self.filter)
        self.imsize_x = hdr['NAXIS1'] ; self.imsize_y = hdr['NAXIS2']
                                                        
        # Crack calibration file, extract params
        try:
            fn = open(self.cal_file,'r')
        except:
            sys.exit('Calibration file %s not found, exiting' % cal_file)
        
        # Parse header line, coeffs, subimage box
        lines = fn.readlines()
        hdr_line = lines[0]
        angle,c1,c2,c3 = [float(x) for x in lines[1].split(',')]
        wavelength_calibration_coeffs = [c1,c2,c3]
        
        # Wavelength calibration: create  pixel  to wavelength function
        f_wave = np.poly1d(wavelength_calibration_coeffs) # Usage: wave = f_wave(pixels)
        
        # Subimage box to extract raw spectrum
        if subimage_box == [0,0,0,0]:
            subimage_box = [int(x) for x in lines[2].split(',')]
        
        # Amplitude calibration: create gain curve function
        lines = lines[3:]
        wavelength_gain = []; gain_curve = []
        for line in lines[2:]:
            w,g = [float(x) for x in line.split()]
            wavelength_gain.append(w); gain_curve.append(g)
        wavelength_gain = np.array(wavelength_gain)
        
        fn.close()
        wmin = wavelength_gain[0]; wmax = wavelength_gain[-1]                                                  
        f_gain = interp1d(wavelength_gain,gain_curve) # Usage: gain = f_gain(any_wave)
        
        # Tweak ymin, ymax by looking for max in middle of spectrum
        xmin,xmax,ymin,ymax = subimage_box
        xc = int( np.mean([xmin,xmax])); yw = ywidth
        yvals = list(im[:,xc])
        ymax_idx = yvals.index(max(yvals))
        ymin = ymax_idx - yw; ymax = ymax_idx + yw
        
        # Create rotated subimage                                             
        im_rot = rotate(im, angle,reshape=False)
        subim = im_rot[ymin:ymax, xmin:xmax]
        
        # Calculate raw spectrum
        pixels,raw_spectrum_full = self.calc_spectrum(subim)
        wave = f_wave(pixels) 
        
        # Restrict wavelength range to that in calibration file                                                  
        wave, raw_spectrum = self.clip_spectrum(wave, raw_spectrum_full, wmin,wmax)
                                                            
        # Normalize raw spectrum
        raw_spectrum /= np.max(raw_spectrum)
                               
        # Calculate and apply gains
        calibrated_spectrum = raw_spectrum / f_gain(wave)
        
        # Store arrays for plotting etc
        self.im = im.astype(float)
        self.pixels = pixels
        self.raw_spectrum_full = raw_spectrum_full
        self.raw_spectrum = raw_spectrum
        self.calibrated_spectrum = calibrated_spectrum
        self.wave = wave                                                
        self.subim = subim
        self.f_wave = f_wave
        self.f_gain = f_gain
        
        
        gain =f_gain(wave)
        '''
        for j,w in enumerate(wave):
            print('TEST:  wave = %0.2f gain = %.3f raw = %.3f cal = %.3f' % \
            (w,gain[j],self.raw_spectrum[j],self.calibrated_spectrum[j]))
        '''
        
        
    def header_params(self):
        return self.title, self.object, self.utdate, self.filter, self.telescope, self.instrument

    def calc_spectrum(self,im):
        '''Calculates raw spectrum by summing pixels in all vertical slices'''
        xsize = im.shape[1]
        Xpixel = np.arange(xsize)
        Signal = []
        for xpixel in Xpixel:
                ymax,signal,signal_max,fig = self.calc_channel_signal(im, xpixel, do_plot=False)
                Signal.append(signal)
        Xpixel = np.array(Xpixel) ; Signal = np.array(Signal)
        return Xpixel, Signal
 
    def calc_channel_signal(self,subim, xpixel, do_plot=False):
        
        ''' Calculates total counts in specified spectral channel xpixel by subtracting background and summing.
        The spectral signal is assumed to be in middle half of the spectrum. '''
        
        yvals = subim[:,xpixel]
        yindex = np.arange(len(yvals))
        
        # Choose first, last quartiles for base, fit linear slope
        n1 = int(len(yindex)/4); n2 = 3*n1
        x1 = yindex[0:n1] ; x2 = yindex[n2:]
        y1 = yvals[0:n1]  ; y2 = yvals[n2:]
        X = np.concatenate((x1,x2),axis=0)
        Y = np.concatenate((y1,y2),axis=0)
        c = np.polyfit(X,Y,1) # linear fit  
        p = np.poly1d(c)
        base = p(yindex)
        
        # Calculate signal vs pixel by subtracting baseline, sum and get index of maximum pixel
        signal = yvals - base
        signal_max = np.max(signal)
        ymax = np.argmax(signal)
    
        # Plot
        fig =''
        if do_plot:
            title = 'Channel %i\n ymax: %.1f, Max value: %.1f' % (xpixel,signal_max,ymax)
            fig, ax = plt.subplots(1,figsize=(10,12))
            ax.plot(yindex,base+yvals,'k.',label ='X pixel number %i' % xpixel)
            ax.plot(yindex,base,'r-')
            ax.grid()
            ax.legend()
        
        return(ymax, np.sum(signal),signal_max,fig)

    def plot_spectrum(self, calibrated = True, title='', plot_balmer=True, medavg = 1,xlims = [380,680], ylims = [0,0]):
        '''Plots raw or calibrated spectrum'''
        fig, ax = plt.subplots(1,1,figsize=(10, 6))
        
        xmin,xmax = xlims
        wave = self.wave
        pixels = self.pixels
        raw_spec = self.raw_spectrum_full
        cal_spec = self.calibrated_spectrum
        
        if title == '': title=self.title
        fig.suptitle(title) 
        
        if calibrated:
            x = wave ; y = cal_spec
            y = medfilt(y,kernel_size = medavg)   # Median average if requested
            ax.plot(x,y,'k-')
            ax.set_ylabel('Calibrated amplitude')
            ax.set_xlabel('Wavelength [nm]')
            ax.set_xlim(xmin,xmax)
            if ylims == [0,0]:
                ax.set_ylim(0,np.max(y)*1.1)
            else:
                ymin, ymax = ylims
                ax.set_ylim(ymin, ymax)
            ax.grid()
            if plot_balmer:
                for x in self.balmer: ax.axvline(x=x,linestyle='-.')
        else:
            x = pixels ; y = raw_spec
            y = medfilt(y,kernel_size = medavg)   # Median average if requested
            ax.plot(x,y,'k-')
            ax.set_ylabel('Uncalibrated amplitude')
            ax.set_xlabel('Pixel nr.')
            ax.grid()
        
        return fig

    
    def plot_2x2(self, ref_file='', medavg = 1,xlims =[380,680]):
        '''Plots raw and calibrated spectra, gain curve, and reference spectrum (if given)'''
        fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(10, 8))
        ymax = 1.0
        xlims = xlims
        wave = self.wave
        raw_spec = self.raw_spectrum
        cal_spec = self.calibrated_spectrum
        
        fig.suptitle(self.title) 
        
        # Uncalibrated normalized spectrum
        ax1.set_ylim(0,ymax*1.1)
        y = raw_spec/np.nanmax(raw_spec)
        
        ax1.plot(wave,y,'k-')
        ax1.set_title('Uncalibrated spectrum,  grism %s' % self.filter)
        ax1.set_xlim(xlims)
        ax1.grid()

        # Gain curve
        ax2.set_ylim(0,1.1)  
        ax2.set_xlim(xlims)
        gain_curve = self.f_gain(wave)
        gain_curve /= np.max(gain_curve)
        ax2.plot(wave,gain_curve,'g-')
        ax2.set_title('Gain curve')
        ax2.grid()

        # Calibrated normalize spectrum
        ax3.set_ylim(0,ymax*1.1)  
        ax3.set_xlim(xlims)
        y = cal_spec/np.nanmax(cal_spec[10:]) # Don't use first few
        y = medfilt(y,kernel_size = medavg)   # Median average if requested
        ax3.plot(wave,y,'b-')
        ax3.set_title('Calibrated spectrum')
        ax3.grid()

        # Reference spectrum: Jacoby spectrum CSV file
        if ref_file != '':
            wave_ref, spec_ref = np.loadtxt(ref_file, unpack=True, comments='#',usecols=(0,1),dtype = float)
            spec_ref /= np.max(spec_ref)
            # Interpolate reference spectrum so it has same length and wavelength range as observed spectrum
            f_interp = interp1d(wave_ref,spec_ref)
            ref_spec = f_interp(wave)       
            ax4.set_ylim(0,ymax*1.1)  
            ax4.set_xlim(xlims)
            y = ref_spec/np.max(ref_spec)
            ax4.plot(wave,ref_spec,'b-')
            ax4.set_title('Reference spectrum')
            ax4.grid()
        
        return fig
    
    def plot_rectified_spectrum(self,T,wavemin=385,wavemax=700):
        '''Plot spectrum normalize by blackbody (Planck function)'''
        
        fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(10, 10))
        fig.suptitle(self.title)
        
        wave = self.wave
        cal_spec = self.calibrated_spectrum
        
        B = self.__Planck(wave,T)
        B /= np.max(B)
        B *= 1.1 # These need to be fitted automatically
        spec_norm = cal_spec/B

        # Median filter
        k_size = 61
        base_fit = medfilt(spec_norm,kernel_size=k_size)

        # Calibrated spectrum, Normalized black body spectrum
        ax1.set_title('Calibrated spectrum')
        ax1.set_ylim(0,np.max(cal_spec)*1.1)
        ax1.set_xlim(wavemin,wavemax)
        ax1.plot(wave,cal_spec,'r-')
        ax1.grid()
        ax1.plot(wave,B,'b-',label='T = %i K' % T)
        ax1.legend()

        #ax2.plot(wave,spec_ref,'b-')
        for x in self.balmer: plt.axvline(x=x,linestyle='-.')
        ax2.set_xlim(wavemin,wavemax)
        ax2.grid()
        ax2.plot(wave,base_fit,'g-')
        ax2.plot(wave,spec_norm,'r-')

        y = spec_norm/base_fit
        ax3.plot(wave,y,'r-')
        ax3.set_ylim(0.0,1.1*np.max(y))
        ax3.set_xlim(wavemin,wavemax)
        ax3.grid()
        return fig  
  
    def plot_image(self,title='',figsize =(10,10),cmap='gray'):
        fig, ax = plt.subplots(figsize=figsize)
        im = self.im
        zmean = np.median(im); s = np.std(im)
        vmin = zmean - 2*s; vmax = zmean + 12*s
        myplot = ax.imshow(im,cmap=cmap, vmin= vmin, vmax = vmax)
        #fig.colorbar(myplot)
        if title == '': title = self.title
        plt.title(title)
        return fig
    
    def plot_strip(self,cmap='jet', title = ''):
        '''Plot strip image'''
        im = self.subim
        fig, ax = plt.subplots(figsize=(10, 3))
        myplot = ax.imshow(im,cmap=cmap, vmin= np.min(im), vmax = np.max(im))
        if title == '': title = '%s\n Dispersed strip image' % self.title
        plt.title(title)
        return fig

    def clip_spectrum(self,wave,spectrum, wave_min,wave_max):
        # Clips spectrum to user-specified wavelength [or pixel] range    
        A = np.array(list(zip(wave,spectrum)))
        A = A[A[:,0]>=wave_min]; A = A[A[:,0]<=wave_max]
        wave,spectrum = list(zip(*A))
        wave = np.array(wave)
        spectrum = np.array(spectrum)
        return wave,spectrum

    def __Planck(self,wave,T):
        # Planck function
        c = 3e8; h = 6.64e-34; k = 1.38e-23; nm = 1.e-9
        wave = wave * nm  # Convert wave to meters
        t1 = 2*h*c**2/wave**5
        t2 = h*c / (wave*k*T)
        return t1 * (np.exp(t2) -1)**-1

    def fit_gaussian(self,wave_min, wave_max, subtract_baseline=False,use_velocity = False):
        ''' Fit gaussian function + slope to absorption or emisssion line, returns fitted params and plot'''
        c = 3e5
        wave = self.wave
        cal_spec = self.calibrated_spectrum
        
        def fit_gauss(xdata,ydata,p0, subtract_baseline):
            ''' Fit Gaussian plus linear slope to (x,y) '''
            def func(x, x0, a, sigma, m, b,):
                t = (x-x0) /sigma
                f = a*np.exp(-t**2) + m*x + b
                return f
            p, pcov = curve_fit(func, xdata, ydata,p0)
            x0, a, fwhm,m,b = p
            ymod = func(xdata, *p) 
            
            if subtract_baseline:
                ymod  -= m*xdata + b
                ydata -= m*xdata + b
                
            x0_err, a_err, fwhm_err, _ ,_ = np.abs(np.sqrt(np.diag(pcov)))
            f= 2*np.sqrt(2*np.log(2)) # sigma -> FWHM factor 
            fwhm *= f; fwhm_err *= f
            fwhm = np.abs(fwhm)
            emission = p[0] > 0
            return ydata,ymod, a, a_err, x0, x0_err,fwhm, fwhm_err, emission
     
        # Select spectral range for fit
        x, y = self.clip_spectrum(wave, cal_spec, wave_min,wave_max)
        
        # Fit gaussian model
        p0 = (np.mean(x),np.mean(y),1,0,np.median(y)) # Guess values
        ydata,ymod, a, a_err, wave_c, wave_c_err, fwhm, fwhm_err, emission =\
            fit_gauss(x,y,p0=p0,subtract_baseline=subtract_baseline)
            
        # Generate plot showing spectrum,fitted Gaussian model
        fig, ax = plt.subplots(figsize=(10,8))
        fig.suptitle(self.title)
  
        if use_velocity:
            v_fwhm = c * fwhm/wave_c; v_fwhm_err = c * fwhm_err/wave_c
            label=r'FWHM = %i+/-%i km/s' % (v_fwhm,v_fwhm_err)
            v = c * (x - wave_c) /wave_c
            ax.plot(v,ydata,'b.')
            if emission:
                ax.plot(v, ymod,'k-', label=label)
            else:
                ax.plot(v, ymod,'k-',label=label)
            t = r'Gaussian fit λc = %.1f+/-%.1f nm, FWHM = %.2f+/-%0.2f' % (wave_c,wave_c_err,fwhm,fwhm_err)
            ax.set_xlabel('Velocity w.r.t. centroid [km/s]')
        else:
            ax.plot(x,ydata,'b.')
            label=r'FWHM = %.1f+/-%.1f nm' % (fwhm,fwhm_err)
            if emission:
                ax.plot(x, ymod,'k-', label=label)
            else:
                ax.plot(x, ymod,'k-',label=label)
            t = r'Gaussian fit λc = %.1f+/-%.1f nm, FWHM = %.1f+/-%0.1f' % (wave_c,wave_c_err,fwhm,fwhm_err)
            ax.set_xlabel('Wavelength [nm]')
        ax.set_title(t,fontsize=10)
        ax.set_ylabel('Normalized amplitude')
        ax.grid()
        ax.legend()
        return fig, ymod, a, a_err, wave_c, wave_c_err, fwhm, fwhm_err, emission
    
