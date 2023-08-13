#!/usr/bin/env python

# Create observing file of Jacoby standard stars for Grism observing with specified RA range
# RLM 25 Jan 2016

ra_min = 9.5; ra_max = 18.5

f_out = 'frm000.sch'
fn  = open(f_out,'w')

f = open('jacoby-list.rasort','r')
lines = f.readlines()
f.close()

# Write header keywords
fn.write("title 'GRISM spectra of Jacoby standard stars'\n")
fn.write("observer 'Robert Mutel'\n")
fn.write ("priority 1\n")
fn.write("\n")
#fn.write("# Jacoby standard stars beteen RA %.1f - %.1f") % (ra_min,ra_max)

# Write image request lines
nsrc = 0
for line in lines:
	ra =  line[34:46]; dec = line[47:59]
	#print line,ra,dec
	rah,ram,ras = ra.split()
	rah = int(rah); ram = int(ram); ras = float(ras)
	decd,decm,decs = dec.split()
	decd = int(decd); decm = int(decm); decs = int(float(decs)) 
	ra =  '%2.2i:%2.2i:%04.1f' % (rah,ram,ras)
	dec = '%+2.2i:%2.2i:%2.2i' % (decd,decm,decs)
	sptype = line[18:25]
	src = line[8:17]; src = src.replace(' ','')
	ra_fp = float(line[0:6])
	if ra_min < ra_fp < ra_max:
		fn.write( "source '%s'   ra %s   dec %s   epoch 2000  filter t dur 60  comment '%s' /\n" % (src,ra,dec,sptype) )
		nsrc += 1

print 'Wrote %i sources to %s' % (nsrc, f_out)
fn.close()
