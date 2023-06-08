#!/usr/bin/env python

# Convert B,V to Sloan g,r
# Reference: Bilir et al. 2005
# 22 Feb 2017 RLM

import numpy as np

ans = input('Enter B,V (separated by comma): ')
B,V = [float(x) for x in ans.split(',')]

g = V + 0.634*(B-V) - 0.108
g_r = 1.124*(B-V) - 0.252
r = g - g_r
print('B = %.2f, V = %.2f, B-V = %.2f' % (B,V,B-V))
print('g = %.2f, r = %.2f, g-r = %.2f' % (g,r,g-r))

'''
# Jordi 2005
g_V =  0.630*(B-V) - 0.124
g_B = -0.370*(B-V) - 0.124

print 'g-V = %.2f, %.2f' % (g_V, g-V)
print 'g-B = %.2f, %.2f' % (g_B, g-B)
'''