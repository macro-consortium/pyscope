#!/usr/bin/env python

fn = open('jacoby-list.edt','r')
lines = fn.readlines()
for line in lines:
	line =  line[0:25] + ' ' + line[74:99]
	ra =  line[20:38]
	rah,ram,ras = [float(x) for x in ra.split()]
	ra = rah + ram/60. + ras/3600.
	line = 	'%6.3f %s' % (ra, line)
	print line
