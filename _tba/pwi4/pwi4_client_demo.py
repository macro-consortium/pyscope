"""
This script demonstrates basic usage of the pwi4_client library
for controlling PWI4 via its HTTP interface.
"""

import time

from pwi4_client import PWI4


print("Connecting to PWI4...")

pwi4 = PWI4()

s = pwi4.status()
print("Mount connected:", s.mount.is_connected)

if not s.mount.is_connected:
    print("Connecting to mount...")
    s = pwi4.mount_connect()
    print("Mount connected:", s.mount.is_connected)

print("  RA/Dec: %.4f, %.4f" % (s.mount.ra_j2000_hours, s.mount.dec_j2000_degs))


print("Slewing...")
pwi4.mount_goto_ra_dec_j2000(10, 70)
while True:
    s = pwi4.status()

    print("RA: %.5f hours;  Dec: %.4f degs, Axis0 dist: %.1f arcsec, Axis1 dist: %.1f arcsec" % (
        s.mount.ra_j2000_hours, 
        s.mount.dec_j2000_degs,
        s.mount.axis0.dist_to_target_arcsec,
        s.mount.axis1.dist_to_target_arcsec
    ))


    if not s.mount.is_slewing:
        break
    time.sleep(0.2)

print("Slew complete. Stopping...")
pwi4.mount_stop()

