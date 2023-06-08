#!/usr/bin/env python

'''
Reads database of Jacoby  stellar spectra, plots, makes csv files
Ref: Jacoby G. et al. 1984, A Library of Stellar Spectra, Astrophys. J. Suppl., 56, 257 (1984)
URL: http://cdsarc.u-strasbg.fr/cgi-bin/Cat?III/92
RLM 1 Feb 2016
'''

import matplotlib.pyplot as plt
import numpy as np
import smooth,sys

def plot_star(x,y):
	plt.figure(1,figsize=(12,8))
	plt.plot(x,y,'r-')
	plt.xlabel('Wavelength (nm)')
	plt.ylabel(r'Flux  (erg cm$^{-2}$ s$^{-1}$ Angstrom$^{-1}$ $\times\ 10^{13}$)')
	plt.title('%s' % star)
	plt.grid(True)
	plt.xlim(380,750)
	fn_spec = '%s-Jacoby-spec.png' % star
	plt.savefig(fn_spec,format ='png')
	print 'Wrote spectrum plot file: %s' % fn_spec
	plt.close()
	return

def write_csv(x,y):
	# Write CSV file of wavelengths and amplitudes
	fn_csv = '%s-Jacoby-spec.csv' % star
	fn = open(fn_csv,'w')
	fn.write('# File %s\n' % star)
	fn.write('# Wavelength [nm]    Normalized Amplitude\n')
	for n in range(len(x)):
		fn.write('   %5.2f         %6.4f\n' % (x[n], y[n]))
	fn.close()
	print 'Wrote CSV file %s' % fn_csv
	return

########## MAIN #############

# Retrieve flux data
flux_data = 'fluxes.dat'
fn = open(flux_data)
lines = fn.readlines()
names = []
for line in lines:
	name = line[0:9].replace(' ','')
	names.append(name)
	fluxes = line[10:].split()
unique_names = list(set(names))
fn.close()

# Build dictionary structure using stars as keys
data = {}
print 'Reading %s ...' % flux_data
for name in unique_names:
	flux = []
	for line in lines:
		if name == line[0:9].replace(' ',''):
			fluxline = [float(line[i:i+10])*1.e13 for i in range(10,len(line)-1,10)]
			flux += fluxline
	data[name] = flux

# Get list of star names
starnames = []
fn = open('jacoby-list.rasort','r')
lines = fn.readlines()
for line in lines:
	starname = line.split()[1]
	starnames.append(starname)
fn.close()

# Set initial wavelength
lambda1 = 351.0 - 1.3  # Determined from Balmer lines

# Create plot and CSV files
for star in starnames:
	if star in data:
		y = np.array(data[star])
		y = smooth.smooth(y,window_len=21,window='hanning')
		x =  0.14*np.arange(len(y)); x += lambda1
		plot_star(x,y)
		write_csv(x,y)
	