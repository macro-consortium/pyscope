
#imports and definitions
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from astropy.io.fits import getdata
from scipy.ndimage import rotate
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import medfilt, find_peaks, detrend

balmer = np.array([397.0, 410.17, 434.05, 486.14, 656.45])
deg = np.pi/180.


class StopExecution(Exception):
    def _render_traceback_(self):
        pass

class grism_utils:
    def __init__(self, grism_image, cal_file, rot_angle, box, f_wave,f_gain):
        """
        The main class for grism spectrum generation and analysis.

        grism_utils contains all the functions required for extracting, calibrating, and visualizing spectra from grism images.

        Parameters
        ----------
        grism_image : str
            location of the grism image you want to work on.

        cal_file : str
            location of the grism calibration file you want to use (must be a csv).
        
        rot_angle : int
            read from the calibration file; rotation angle of extraction box

        f_wave : list
            read from the calibration file; coefficients of wavelength calibration function

        f_gain : list
            read from the calibration file; coefficients of flux calibration function


        Other Parameters
        ----------------
        TBD

        Raises
        ------
        TBD

        See Also
        --------
        TBD

        Notes
        -----
        TBD

        References
        ----------
        TBD

        Examples
        --------
        TBD
        """
        
        self.grism_image = grism_image
        self.cal_file = cal_file
        self.balmer = np.array([397.0, 410.17, 434.05, 486.14, 656.45])
        self.wavelength_range = [380,750]
        
        ''' Open image, extract header information '''
        im, hdr = getdata(grism_image, 0, header=True)
        self.im = im
        self.hdr = hdr
        self.object_name  = hdr['OBJECT']
        self.obs_date     = hdr['DATE-OBS'][:-12].replace('T',' ')
        self.telescope    = hdr['TELESCOP']
        self.camera       = hdr['INSTRUME'][0:9]
        self.imsize_x = hdr['NAXIS1'] ; self.imsize_y = hdr['NAXIS2']
        # Create default plot title
        self.title = '%s (%s)\nGrism spectrum: %s %s' % \
        (self.object_name, self.obs_date, self.telescope, self.camera)
                                                     
        self.rot_angle = rot_angle
        self.box = box
        self.f_wave = f_wave
        self.f_gain = f_gain
        
    def summary_info(self):
        """
        Prints key parameters from the current instantiation. 
        """
        return self.object_name, self.obs_date,self.telescope,self.camera,self.title,self.im,self.rot_angle, self.box, self.f_wave, self.f_gain
    
    def create_box(self):       
        """Extracts a subimage. The spectral trace is oriented by transforming the image,
           and the subimage is extracted based on dimensions supplied by the extraction box.

        Returns:
            im_rot (arraylike): the transformed image (full size)

            subim  (arraylike): the extracted subimage

        """
        
        # Flip image so L-> R corresponds to short -> long wavelength                
        im_flip = np.fliplr(self.im)
        
        # Rotate full image  
        im_rot = rotate(im_flip, self.rot_angle,reshape=False)
        
        # Trim image to subimage using box
        xstart,ystart,xwidth,ywidth = self.box
        self.subim = im_rot[ystart:ystart+ywidth,xstart:xstart+xwidth]
        return self.subim , im_rot
    
    def plot_box(self,image, subim, box, vmin=None, vmax=None,figsize =(10,10),cmap='gray'):
        """Plots the full image and extracted subimage side by side for inspection.

        Args:
            image (arraylike): full transformed image

            subim (arraylike): extracted subimage

            box (list): dimensions of the extraction box; this will be plotted on the full image for visual aid.

            vmin (int, optional): minimum value of image scale. Defaults to None.

            vmax (int, optional): maximum value of image scale. Defaults to None.

            figsize (tuple, optional): size of figure. Defaults to (10,10).

            cmap (str, optional): colormap to use. Defaults to 'gray'.

        Returns:
            fig (arraylike): figure displaying both images and box annotation.

        """
        
        fig, ax = plt.subplots(1, 2,figsize=figsize)
        zmean = np.median(image); s = np.std(image)

        if vmin == None:
            vmin = zmean - 2*s; 
        if vmax == None:
            vmax = zmean + 12*s

        ax[0].imshow(image,cmap=cmap, vmin= vmin, vmax = vmax)
        ax[1].imshow(subim,cmap=cmap, vmin= vmin, vmax = vmax)
        ax[0].set_title(f"{self.object_name} ({self.obs_date}): Grism Image")
        ax[1].set_title(f"{self.object_name} ({self.obs_date}): Extraction Box")

        xstart,ystart,xwidth,ywidth = box
        rect = Rectangle((xstart,ystart),xwidth,ywidth,linewidth=.5,edgecolor='r',facecolor='none')
        ax[0].add_patch(rect)
            
        return fig 
    
    def calibrate_spectrum(self,subim,norm=False):
        """Calculates raw spectrum by summing pixels in all vertical slices,
           then apply wavelength & gain calibration according to cal file.

        Args:
            subim (arraylike): the subimage from which to extract the spectrum.
            norm (bool, optional): whether or not to normalize the spectrum.

        Returns:
            spectrum : spectrum object containing pixel, wavelength, uncalibrated amplitude and calibrated amplitude values. 
        """

        pixels = np.arange(subim.shape[1])
        # find sum of pixel values along each column (spectral channel)
        uncal_amp = []
        for pixel in pixels:
            ymax,signal,signal_max = self.__calc_channel_signal(subim,pixel)
            uncal_amp.append(signal)
        uncal_amp = np.array(uncal_amp)
        if norm:
            uncal_amp /= np.max(uncal_amp)
        else:
            pass
     
        # Wavelength calibration
        wave = self.f_wave(pixels)
    
        # Gain calibration
        gain_curve = self.f_gain(wave)
        cal_amp = uncal_amp / gain_curve
    
        spectrum = np.vstack([pixels,wave,uncal_amp,cal_amp])
        return spectrum

    def __calc_channel_signal(self,subim,xpixel):  
        """Calculates total counts in specified spectral channel xpixel 
        by subtracting background and summing. The spectral signal is assumed 
        to be in middle half of the spectrum.

        Args:
            subim (arraylike): _description_
            
            xpixel (int): x pixel at which to perform signal calculation.
        
        Returns:
            ymax (int): y position of maximum value in column.

            tot_signal (int): total counts in column.

            signal_max (int): maximum value in column.
        """

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
        tot_signal = np.sum(signal)     
        return(ymax, tot_signal,signal_max) 
    
    def plot_gain_curve(self, spectrum, wmin=350,wmax=750,color='r',title=''):
        """Plots the gain curve based on wavelengths in input spectrum.

        Args:
            spectrum (arraylike): input spectrum.

            wmin (int, optional): minimum wavelength of the plot. Defaults to 350.

            wmax (int, optional): maximum wavelength of the plot. Defaults to 750.

            color (str, optional): color to plot the gain curve. Defaults to 'r'.

            title (str, optional): title the figure. Defaults to ''.

        Returns:
            fig : plot of the gain curve

        """

        p,w,u,c = self.clip_spectrum(spectrum,wmin,wmax)
        gain_curve =self.f_gain(w)
        gain_curve /= np.max(gain_curve)
        fig, ax = plt.subplots(1, 1,figsize=(8,5))
        ax.plot(w,gain_curve,color =color)
        ax.set_ylabel(r'Flux  (count cm$^{2}$ s Angstrom erg$^{-1}$)')
        plt.suptitle(title)
        plt.grid()
        return fig

    def fit_spectral_line(self,spectrum,wave_min,wave_max):
        """Fit a Gaussian function to spectral line in the wavelength range wave_min to wave_max.
        Returns fitted parameters with uncertainties and a plot of spectral line and fitted Gaussian.

        Args:
            spectrum (_type_): _description_
            wave_min (_type_): _description_
            wave_max (_type_): _description_

        Returns:
            _type_: _description_
        """
    
        # Constrain spectrum to desired wavelength range, unpack needed arrays
        pixel,wave,uncal_amp,amp = self.clip_spectrum(spectrum,wave_min,wave_max)
    
        # Detrend to remove slope
        uncal_amp = detrend(uncal_amp)
    
        # Find index of max value
        imax = np.argmax(np.abs(uncal_amp))
    
        # Fit a Gaussian model
        p0 = (wave[imax],uncal_amp[imax],1,1,1)
        params, pcov = curve_fit(self.__gftn, wave, uncal_amp,p0)
        wave_ctr, a, fwhm,_,_ = params
        uncal_amp_mod = self.__gftn(wave, *params)
        wave_ctr_err, a_err, fwhm_err,_,_= np.abs(np.sqrt(np.diag(pcov)))
        f= 2*np.sqrt(2*np.log(2)) * 0.5
        fwhm *= f; fwhm_err *= f
        fwhm = np.abs(fwhm)
        params = (wave_ctr,wave_ctr_err,fwhm,fwhm_err,a,a_err)
        return params, wave, uncal_amp, uncal_amp_mod

    def plot_spectral_line(self,x,amp,amp_mod,x_ctr,x_ctr_err,fwhm,fwhm_err,color='r',title=''):
        fig, ax = plt.subplots(1, 1,figsize=(8,5))
        ax.plot(x,amp_mod,color =color)
        ax.plot(x,amp,'k.')
        T = f"{title}\n$\\lambda_c$ = {x_ctr:.1f} +/- {x_ctr_err:.1f} nm, FWHM = {fwhm:.1f} +/- {fwhm_err:.1f} nm"
        # T = '%s\n$\lambda_c$ = %.1f +/- %.1f nm, FWHM = %.1f +/- %.1f nm' % \
            # (title,x_ctr,x_ctr_err,fwhm,fwhm_err)
        plt.suptitle(T)
        plt.grid()
        return fig
    
    def __gftn(self,x, x0, a, sigma,m,b):
        ''' Define a Gaussian function'''
        t = (x-x0) /sigma
        f = a*np.exp(-2*t**2)+m*x+b
        return f

    def clip_spectrum(self,spectrum, wave_min, wave_max):
        '''Restrict wavelength range to avoid crazy gain curve at edges '''
        pixel, wave, uncal_amp, cal_amp = spectrum
        mask = (wave > wave_min) & (wave < wave_max)
        pixel_m = pixel[mask]
        wave_m  = wave[mask]
        uncal_amp_m   = uncal_amp[mask]
        cal_amp_m = cal_amp[mask]
        spectrum = np.vstack( [pixel_m, wave_m,uncal_amp_m, cal_amp_m] )
        return spectrum
    
    def plot_spectrum(self, spectrum, xaxis = 'pixel',yaxis = 'uncal', subrange = slice(0,9999), title='', \
        jacoby = False, plot_balmer = False, medavg = 1,xlims =[0,0],ylims =[0,0],grid=True):
        '''Plots science or Jacoby  spectrum, with selectable axes [x: pixels or wavelength; y: uncalibrated or calibrated. '''
        fig, ax = plt.subplots(1,1,figsize=(8, 4))           
        fig.suptitle(title) 
    
        if jacoby:
            w,c = spectrum
            s = subrange
            wave = w[s]; amp_cal = c[s]
            x = wave    ; ax.set_xlabel('Wavelength (nm)') 
            y = amp_cal ; ax.set_ylabel('Calibrated flux (counts)')
        else:
            # Slice spectrum by selecting user-selected pixel range (Unpythonic!)
            p,w,u,c = spectrum
            s = subrange
            p = p[s] ; w = w[s]; u =u[s]; c = c[s]
            spectrum = np.vstack([p,w,u,c])
        
            pixels, wave, amp_uncal, amp_cal = spectrum
            if xaxis == 'pixel':
                x = pixels ; ax.set_xlabel('Pixels')
            else:
                x = wave ; ax.set_xlabel('Wavelength (nm)')
            if yaxis == 'uncal':
                y = amp_uncal ; ax.set_ylabel('Uncalibrated flux (counts)')
            else:
                y = amp_cal   ; ax.set_ylabel(r'Flux  (erg cm$^{-2}$ s$^{-1}$ Angstrom$^{-1}$)')
  
        if plot_balmer:
            for b in balmer: ax.axvline(x=b,linestyle='dotted')
     
        # Median average if requested 
        y = medfilt(y,kernel_size = medavg)  
        ax.plot(x,y,'k-')

        #set axis limits
        if xlims != [0,0]: 
            xmin,xmax = xlims
            ax.set_xlim(xmin,xmax)
        if ylims != [0,0]: 
            ymin,ymax = ylims
            ax.set_ylim(ymin,ymax)
        else:
            #select good channels (middle 80% of channels) and set ylim based on those values
            good_channels = y[int(.15*len(y)):int(.85*len(y))]
            ax.set_ylim(np.min(good_channels)*.7,np.max(good_channels)*1.3)
        if grid:
            ax.grid()
        return fig

