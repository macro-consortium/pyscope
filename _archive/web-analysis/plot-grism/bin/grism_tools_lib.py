# -*- coding: utf-8 -*-

import numpy as np
import astropy.io.fits as pyfits; from scipy.ndimage.interpolation import rotate
from statsmodels.nonparametric.smoothers_lowess import lowess; from scipy.interpolate import interp1d
from scipy.signal import medfilt, medfilt2d,find_peaks; from scipy.optimize import curve_fit
from datetime import datetime; import matplotlib.pyplot as plt, matplotlib as mpl; import sys
from matplotlib.backends.backend_pdf import PdfPages
import io

plt.switch_backend('Agg')
mpl.rcParams['axes.prop_cycle'] = mpl.cycler('color', ['#377eb8', '#4daf4a', '#e41a1c', '#dede00', '#ff7f00', '#999999', '#984ea3', '#f781bf', '#a65628'])

''' Utilities for plotting and calibrating grism spectra
        -If both a calibration and reference spectrum are passed, apply the calibration to the image 
        and then the reference spectrum may be called when plotting a 2x2. 
        -If just a calibration is passed, then apply the calibration.
        -If just a reference spectrum is passed, begin a calibration sequence. 
        -If neither is passed, exit. '''
class grism_tools:
    def __init__(self, grism_image, cal_file='', ref_file=''):
        
        self.grism_image = grism_image
        
        # Open image and extract header info
        self.im, self.hdr = pyfits.getdata(grism_image, 0, header=True)
        self.object     = self.hdr['OBJECT']
        self.utdate     = self.hdr['DATE-OBS'][:-3].replace('T',' ')
        self.jd         = self.hdr['JD']
        self.telescope  = self.hdr['TELESCOP']
        self.instrument = self.hdr['INSTRUME']
        self.filter     = self.hdr['FILTER']
        self.z          = self.hdr['AIRMASS']
        self.imsize_x   = self.hdr['NAXIS1']
        self.imsize_y   = self.hdr['NAXIS2']
        
        # Create default plot title
        self.title = '%s\n%s %s grism: %s' % (self.object, self.telescope, self.utdate, self.filter)

        # Initialize some useful variables
        self.balmer     = np.array([397.0, 410.2, 434.0, 486.1, 656.3])
        self.helium     = np.array([388.9, 447.1, 471.3, 492.2, 501.6, 504.8, 587.6, 667.8, 706.5, 728.1])
        self.carbon     = np.array([477.2, 493.2, 502.4, 505.2, 538.0, 579.3, 580.1, 600.1, 601.3, 658.8, 711.5])
        self.nitrogen   = np.array([399.5, 463.1, 500.5, 568.0, 575.2, 648.2, 661.1, 744.2, 746.8])
        self.oxygen     = np.array([615.6, 645.6, 700.2, 725.4])
        self.calcium    = np.array([393.4, 396.8])

        # Flip image so L-> R corresponds to short -> long wavelength                     
        self.im = np.fliplr(self.im)

        # Check if either a calibration file or a reference spectrum have been passed, if neither, exit
        if cal_file == '' and ref_file == '':
            sys.exit('No calibration file or reference spectrum selected, exiting')
        elif cal_file != '' and ref_file != '':
            self.cal_file = cal_file
            self.ref_file = ref_file
            self.apply_calibration(cal_file)
        elif cal_file != '':
            self.cal_file = cal_file
            self.ref_file = None
            self.apply_calibration(cal_file)
        else:
            self.ref_file = ref_file
            self.init_calibration(ref_file)

    ''' Function to apply a calibration to the image '''
    def apply_calibration(self, cal_file, ywidth=-1, ycenter=-1):
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
        
        # Wavelength calibration: create pixel to wavelength function
        f_wave = np.poly1d(wavelength_calibration_coeffs) # Usage: wave = f_wave(pixels)
        
        # Subimage box to extract raw spectrum
        subimage_box = [int(x) for x in lines[2].split(',')]
        xmin,xmax,ymin,ymax = subimage_box

        if ycenter != -1:
            w = ymax - ymin
            ymin = ycenter - int(w/2)
            ymax = ycenter + int(w/2)

        if ywidth != -1:
            ymin += int(ywidth/2)
            ymax -= int(ywidth/2)
        
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

        ''' Tweak ymin, ymax by looking for max in middle of spectrum
        xc = int( np.mean([xmin,xmax])); yw = ywidth
        yvals = list(self.im[ymin:ymax,xc])
        ymax_idx = yvals.index(max(yvals))
        ymin = ymin + ymax_idx - yw; ymax = ymin + ymax_idx + yw '''
        
        # Create rotated subimage                                             
        im_rot = rotate(self.im, angle, reshape=False)
        subim = im_rot[ymin:ymax, xmin:xmax]
        
        # Calculate raw spectrum
        pixels,raw_spectrum_full = self.calc_spectrum(im=subim)
        wave = f_wave(pixels) 
        
        # Restrict wavelength range to that in calibration file                                                  
        wave, raw_spectrum = self.clip_spectrum(wave, raw_spectrum_full, wmin, wmax)
                                                            
        # Calculate and apply gains
        calibrated_spectrum = raw_spectrum / f_gain(wave)
        
        # Store arrays for plotting etc
        self.pixels = pixels
        self.raw_spectrum_full = raw_spectrum_full
        self.raw_spec = raw_spectrum
        self.cal_spec = calibrated_spectrum
        self.wave = wave                                                
        self.subim = subim
        self.f_wave = f_wave
        self.f_gain = f_gain
    
    def init_calibration(self, ref_file):
        # Crack Jacoby reference file, extract spectrum
        wave_ref, spec_ref = np.loadtxt(ref_file, unpack=True, comments='#',usecols=(0,1),dtype = float)
        spec_ref /= np.max(spec_ref)

        self.wave_ref = wave_ref
        self.spec_ref = spec_ref
    
    def wave_range(self):
        return self.wave[0], self.wave[-1]
        
    def header_params(self):
        return self.im, self.title, self.object, self.utdate, self.filter, self.telescope, self.instrument, self.z
    
    def wave_params(self):
        return self.jd, self.wave, self.cal_spec

    '''Calculates raw spectrum by summing pixels in all vertical slices'''
    def calc_spectrum(self, im=np.array([])):
        if len(np.shape(im))==1: im = self.subim
        xsize = im.shape[1]
        pixels = np.arange(xsize)
        S = []
        for pixel in pixels:
                ymax,signal,signal_max,_ = self.calc_channel_signal(im, pixel, do_plot=False)
                S.append(signal)
        pixels = np.array(pixels) ; S = np.array(S)
        self.pixels = pixels
        self.raw_spec = S
        return pixels, S

    ''' Calculates total counts in specified spectral channel xpixel by subtracting background and summing.
        The spectral signal is assumed to be in middle half of the spectrum. '''
    def calc_channel_signal(self,subim, xpixel, do_plot=False):
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
        fig = ''
        if do_plot:
            title = 'Channel %i\n ymax: %.1f, Max value: %.1f' % (xpixel,signal_max,ymax)
            fig, ax = plt.subplots(1,figsize=(10,12))
            ax.plot(yindex,base+yvals,'k.',label ='X pixel number %i' % xpixel)
            ax.plot(yindex,base,'r-')
            ax.grid()
            ax.legend()
        
        return(ymax, np.sum(signal),signal_max,fig)

    '''Plots raw or calibrated spectrum'''
    def plot_spectrum(self, calibrated = True, title='', plot_lines=['H'], medavg = 1, xlims =[380,720]):
        fig, ax = plt.subplots(1,1,figsize=(10, 6))
        
        xmin,xmax = xlims
        if title == '': title=self.title
        fig.suptitle(title) 
        
        if calibrated:
            x = self.wave ; y = self.cal_spec
            y = medfilt(y,kernel_size = medavg)   # Median average if requested
            ax.plot(x,y,'k-')
            ax.set_ylabel('Calibrated amplitude')
            ax.set_xlabel('Wavelength [nm]')
            ax.set_xlim(xmin,xmax)
            ax.set_ylim(0,np.max(y)*1.1)
            ax.grid()
            if 'H' in plot_lines:
                for x in self.balmer: ax.axvline(x=x,linestyle='-.', label='Hydrogen (Balmer)', color='#377eb8')
            if 'He' in plot_lines:
                for x in self.helium: ax.axvline(x=x,linestyle='-.', label='Helium', color='#4daf4a')
            if 'C' in plot_lines:
                for x in self.carbon: ax.axvline(x=x,linestyle='-.', label='Carbon', color='#e41a1c')
            if 'N' in plot_lines:
                for x in self.nitrogen: ax.axvline(x=x,linestyle='-.', label='Nitrogen', color='#dede00')
            if 'O' in plot_lines:
                for x in self.oxygen: ax.axvline(x=x,linestyle='-.', label='Oxygen', color='#ff7f00')
            if 'Ca' in plot_lines:
                for x in self.calcium: ax.axvline(x=x,linestyle='-.', label='Calcium', color='#999999')
            handles,labels = fig.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc=1)                                                          
        else:
            x = self.pixels ; y = self.raw_spec
            y = medfilt(y,kernel_size = medavg)   # Median average if requested
            ax.plot(x,y,'k-')
            ax.set_ylabel('Uncalibrated amplitude')
            ax.set_xlabel('Pixel nr.')
            ax.grid()
        
        self.spectrum_figure = fig
        spectrum_buff = io.BytesIO()
        fig.savefig(spectrum_buff)
        return spectrum_buff

    
    def plot_2x2(self, ref_file='', medavg = 1,xlims =[380,680]):
        '''Plots raw and calibrated spectra, gain curve, and reference spectrum (if given)'''
        fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(10, 8))
        ymax = 1.0
        xlims = xlims

        # Load in ref file from initialization if none is specified and it is there
        if ref_file == '' and self.ref_file != None:
            ref_file = self.ref_file
        else: 
            self.ref_file = ref_file
        
        fig.suptitle(self.title) 
        
        # Uncalibrated normalized spectrum
        ax1.set_ylim(0,ymax*1.1)
        y = self.raw_spec/np.nanmax(self.raw_spec)
        
        ax1.plot(self.wave,y,'k-')
        ax1.set_title('Uncalibrated spectrum,  grism %s' % self.filter)
        ax1.set_xlim(xlims)
        ax1.grid()

        # Gain curve
        ax2.set_ylim(0,1.1)  
        ax2.set_xlim(xlims)
        gain_curve = self.f_gain(self.wave)
        gain_curve /= np.max(gain_curve)
        ax2.plot(self.wave,gain_curve,'g-')
        ax2.set_title('Gain curve')
        ax2.grid()

        # Calibrated normalize spectrum
        ax3.set_ylim(0,ymax*1.1)  
        ax3.set_xlim(xlims)
        y = self.cal_spec/np.nanmax(self.cal_spec[10:]) # Don't use first few
        y = medfilt(y,kernel_size = medavg)   # Median average if requested
        ax3.plot(self.wave,y,'b-')
        ax3.set_title('Calibrated spectrum')
        ax3.grid()

        # Reference spectrum: Jacoby spectrum CSV file
        if self.ref_file != '':
            wave_ref, spec_ref = np.loadtxt(ref_file, unpack=True, comments='#',usecols=(0,1),dtype = float)
            spec_ref /= np.max(spec_ref)
            # Interpolate reference spectrum so it has same length and wavelength range as observed spectrum
            f_interp = interp1d(wave_ref,spec_ref)
            ref_spec = f_interp(self.wave)       
            ax4.set_ylim(0,ymax*1.1)  
            ax4.set_xlim(xlims)
            y = ref_spec/np.max(ref_spec)
            ax4.plot(self.wave,ref_spec,'b-')
            ax4.set_title('Reference spectrum')
            ax4.grid()
        
        self.twoxtwo_figure = fig
        twoxtwo = io.BytesIO()
        fig.savefig(twoxtwo)
        return twoxtwo
    
    '''Plot spectrum normalize by blackbody (Planck function)'''
    def plot_rectified_spectrum(self,T,wavemin=385,wavemax=700):
        
        fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(10, 10))
        fig.suptitle(self.title)
        
        B = self.__Planck(self.wave,T)
        B /= np.max(B)
        B *= 1.1 # These need to be fitted automatically
        spec_norm = self.cal_spec/B

        # Median filter
        k_size = 61
        base_fit = medfilt(spec_norm,kernel_size=k_size)

        # Calibrated spectrum, Normalized black body spectrum
        ax1.set_title('Calibrated spectrum')
        ax1.set_ylim(0,np.max(self.cal_spec)*1.1)
        ax1.set_xlim(wavemin,wavemax)
        ax1.plot(self.wave,self.cal_spec,'r-')
        ax1.grid()
        ax1.plot(self.wave,B,'b-',label='T = %i K' % T)
        ax1.legend()

        #ax2.plot(wave,spec_ref,'b-')
        for x in self.balmer: plt.axvline(x=x,linestyle='-.')
        ax2.set_xlim(wavemin,wavemax)
        ax2.grid()
        ax2.plot(self.wave,base_fit,'g-')
        ax2.plot(self.wave,spec_norm,'r-')

        ax3.plot(self.wave,spec_norm/base_fit,'r-')
        ax3.set_ylim(0.0,1.4)
        ax3.set_xlim(wavemin,wavemax)
        ax3.grid()

        self.rectified_figure = fig
        rectified_buff = io.BytesIO()
        fig.savefig(rectified_buff)
        return rectified_buff  

    '''Plot image: defaults to full image '''
    def plot_image(self,title='',im = np.array([]), figsize =(10,10),cmap='gray'):
        fig, ax = plt.subplots(figsize=figsize)
        if len(np.shape(im))==1 : im = self.im
        zmean = np.median(im); s = np.std(im)
        vmin = zmean - 2*s; vmax = zmean + 12*s
        myplot = ax.imshow(im,cmap=cmap, vmin= vmin, vmax = vmax)
        #fig.colorbar(myplot)
        if title == '': title = self.title
        plt.title(title)
        self.fits_figure = fig
        image_buff = io.BytesIO()
        fig.savefig(image_buff)
        return image_buff
    
    '''Plot strip image'''
    def plot_strip(self,cmap='jet', title = '', figsize=(10,3)):
        im = self.subim
        fig, ax = plt.subplots(figsize=figsize)
        myplot = ax.imshow(im,cmap=cmap, vmin= np.average(im)-np.std(im), vmax = np.average(im)+4*np.std(im))
        if title == '': title = '%s\n Dispersed strip image' % self.title
        plt.title(title)
        self.strip_figure = fig
        strip_buff = io.BytesIO()
        fig.savefig(strip_buff)
        return strip_buff

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

    def fit_gaussian(self,wave_min,wave_max,emission=False):
        ''' Fit gaussian function + slope to absorption or emisssion line, returns fitted params and plot'''
        wave = self.wave
        cal_spec = self.cal_spec
        
        def gauss_em(x,a,x0,s,m,b):
            f = np.exp(-(x-x0)**2/(2*s**2))
            g = m*x +b
            return g + a*f
        def gauss_abs(x,a,x0,s,m,b):
            f = np.exp(-(x-x0)**2/(2*s**2))
            g = m*x +b
            return g  - a*f   
        
        # select spectral range for fit
        x, y = self.clip_spectrum(wave, cal_spec, wave_min,wave_max)

        # Fit gaussian model
        if emission:
            idx = np.argmax(y)
            p0 = [y[idx],x[idx],1,0,np.median(y)] # Guess values
            popt,pcov = curve_fit(gauss_em,x,y,p0=p0)
        else:
            idx = np.argmin(y) 
            p0 = [y[idx],x[idx],1,0,np.median(y)] # Guess values
            popt,pcov = curve_fit(gauss_abs,x,y,p0=p0)
        amp, wave_c,fwhm,m,b = popt
        amp_err, wave_c_err,fwhm_err,m_err,b_err = np.sqrt(np.diag(pcov))
        f= 2*np.sqrt(2*np.log(2)) # sigma -> FWHM factor 
        fwhm *= f; fwhm_err *= f
        
        # Generate plot showing spectrum,fitted Gaussian model
        fig, ax = plt.subplots(figsize=(6,6))
        fig.suptitle(self.title)       
        ax.plot(x,y,'b.')
        label=r'FWHM = %.2f+/-%.2f nm' % (fwhm,fwhm_err)
        if emission:
            ax.plot(x, gauss_em(x,*popt),'k-', label=label)
        else:
            ax.plot(x, gauss_abs(x,*popt),'k-',label=label)
        ax.legend()
        t = r'Gaussian fit λc = %.2f+/-%.2f nm, FWHM = %.2f+/-%0.2f' % (wave_c,wave_c_err,fwhm,fwhm_err)
        ax.set_title(t,fontsize=10)
        ax.set_xlabel('Wavelength [nm]')
        ax.set_ylabel('Normalized amplitude')
        ax.grid()

        #NOTE POPT is unused in this version and is therefore not returned
        self.gauss_figure = fig
        gauss_buff = io.BytesIO()
        fig.savefig(gauss_buff)        
        return gauss_buff

    def get_emission(self):#TODO Implement
        return True

    
    def rotate_image(self,box,width):
        '''Fit linear slope to maximum y values in cropped image'''
        xmin,xmax,ymin,ymax = box
        subim = self.im[ymin:ymax,xmin:xmax]
        X = range(subim.shape[1])
        Y = [np.argmax(subim[:,j]) for j in X ]
        angle_rad,b = np.polyfit(X,Y,1)
        angle = np.rad2deg(angle_rad)
        subim_rot = rotate(subim, angle,reshape=False)
        # Crop subimage width centered 
        yc = angle_rad * (xmax-xmin)/2 + b
        ymin = int(yc - width/2); ymax = int(ymin + width)
        subim = subim_rot[ymin:ymax,:]
        self.subim = subim      
        return angle, subim 
    
    ''' Find pixel locations of spectral peaks for wavelength calibration'''
    def find_spectral_peaks(self,prominence=0.2,width=3,do_plot=False):
        S = self.raw_spec
        Snorm = S/np.nanmax(S)
        X = np.arange(len(Snorm))
        S_medavg = medfilt(Snorm,kernel_size=51)
        #S_peaks = -1*(Snorm - S_medavg)
        S_peaks = np.abs(Snorm - S_medavg)
        peaks, _ = find_peaks(S_peaks,prominence=prominence,width=width,distance=3)
        fig = ''
        if do_plot:
            fig = plt.figure(figsize=(12,3))
            plt.grid()
            plt.title(str(peaks))
            plt.plot(X,S_peaks)
            for peak in peaks:
                plt.axvline(x=peak,color='red')
        return peaks,fig
    
    def calc_wave(self,peaks,ref_lines):
        balmer_pix =  np.array(peaks)
        c = np.polyfit(balmer_pix,ref_lines,2)
        f_wave = np.poly1d(c)
        self.wave = f_wave(self.pixels)
        return f_wave,c
    
    '''Calculates a gain curve by comparing Jacoby spectrum to observerd spectrum
        Returns calibrated spectrum  and either smoothed gains with same length as raw_spec
        or coefficients of a polynomial fit and ''' 
    def calc_gain_curve(self, do_plot = False, do_poly=False, nsmooth=9,npoly=9):
        # Interpolate Jacoby reference spectrum so it has same length and wavelength range as observed spectrum
        f_interp = interp1d(self.wave_ref,self.spec_ref)
        spec_ref_interp = f_interp(self.wave)

        # Loess average
        spec_avg = lowess(self.raw_spec, self.wave, is_sorted=True, return_sorted=False, frac=0.05, it=0)
        
        # Median average both spectra and take ratio to get gain curve; smooth gain curve
        #spec_avg     = medfilt(raw_spec, kernel_size=nsmooth)
        spec_ref_avg = medfilt(spec_ref_interp, kernel_size=nsmooth)
        gain = spec_avg/spec_ref_avg
        gain_smooth = medfilt(gain,kernel_size=51)

        if do_poly:
            # Fit a high order polynomial to gains
            c = np.polyfit(self.wave,gain_smooth,npoly)
            p = np.poly1d(c)
            gain_curve = p(self.wave)
        else:
            c = None
            gain_curve = gain_smooth
            
        self.cal_spec = self.raw_spec/gain_curve
        self.gain_curve = gain_curve       

        # Plot gain curve and poly fit if requested           
        if do_plot:
            fig, ax = plt.subplots(1,1,figsize=(8, 4))
            plt.plot(self.wave,gain,'g.',label='Gains')
            plt.plot(self.wave,gain_smooth,'b.',label='Smooth gains')
            if do_poly: plt.plot(self.wave,gain_curve,'r-', lw =2, label ='Polynomial fit, n = %i' % npoly)
            plt.legend()
            plt.grid(); plt.title('Gain curve')
            plt.ylim(0)
            plt.xlabel('Wavelength [nm]')
        
        return c, gain_curve,fig
    
    def write_calib_csv(self, cal_file, wavelength_coefficients, angle, subim_box, gain_curve):
        c1,c2,c3 = [float(x) for x in wavelength_coefficients]
        hdr_line = 'Grism calibration created %s using %s, %s, Filter: %s\n' %(datetime.now().strftime("%Y/%m/%d"),self.telescope, self.instrument, self.filter)
        cal_line = '%.2f, %.3e, %.3f, %.2f\n' % (float(angle),c1,c2,c3)
        xmin,xmax,ymin,ymax = subim_box

        with open(cal_file, 'w') as fh:
            fh.write(hdr_line)
            fh.write(cal_line)
            fh.write('%i, %i, %i, %i\n' % (xmin,xmax,ymin,ymax))
            for j,w in enumerate(self.wave):
                fh.write('%.2f %.4f\n' % (w, gain_curve[j]))
        print('Wrote calibration file %s' % cal_file)

    def get_calib(self):
        return self.cal_file

    #Note 4/11/21, parameters will need to be updated with other plots, or restructuring to make them pull from self. parameters.
    #def get_pdf(self,lines,medavg,minSpectrum,maxSpectrum,minGauss,maxGauss,emission):
    def get_pdf(self,fits = False, strip=False,spectrum=False,gauss=False,rectified=False,twoxtwo=False):
        pages = PdfPages("./temp/Grism.pdf")
        if fits:
            pages.savefig(self.fits_figure)
        if strip:
            pages.savefig(self.strip_figure)     
        if spectrum:
            pages.savefig(self.spectrum_figure)
        if gauss:
            pages.savefig(self.gauss_figure)
        if rectified:
            pages.savefig(self.rectified_figure)
        if twoxtwo:
            pages.savefig(self.twoxtwo_figure) 
        pages.close()      

    def get_object_info(self):
        return self.object, self.telescope, self.utdate, self.filter
