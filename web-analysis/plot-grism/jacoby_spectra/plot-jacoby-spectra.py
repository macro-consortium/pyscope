#!/usr/bin/env python

'''
Reads Standard stellar spectra, plots
Ref: Jacoby G. et al. 1984, A Library of Stellar Spectra, Astrophys. J. Suppl., 56, 257 (1984)
URL: http://cdsarc.u-strasbg.fr/cgi-bin/Cat?III/92
RLM 26 Mar 2015
'''

import matplotlib.pyplot as plt
import numpy as np

fn = open('fluxes.dat')
lines = fn.readlines()
names = []
for line in lines:
	name = line[0:9].replace(' ','')
	names.append(name)
	fluxes = line[10:].split()
unique_names = list(set(names))

# Build dictionary structure using stars as keys
data = {}
for name in unique_names:
	flux = []
	for line in lines:
		if name == line[0:9].replace(' ',''):
			fluxline = [float(line[i:i+10])*1.e13 for i in range(10,len(line)-1,10)]
			flux += fluxline
	data[name] = flux

star = 'HD116608'

plt.figure(1,figsize=(12,8))
y = np.array(data[name])
lambda1 = 351.0

x =  0.14*np.arange(len(y))
x += 351.0
plt.plot(x,y,'r-')
plt.xlabel('Wavelength (nm)')
plt.ylabel(r'Flux  (erg cm$^{-2}$ s$^{-1}$ Angstrom$^{-1}$ $\times\ 10^{13}$)')
plt.title('%s' % star)
plt.grid(True)
plt.show()

