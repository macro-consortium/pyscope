"""
This script is an example of how to use pwi4_client to automate the
startup of a PWI4-controlled mount.
"""

import time

from pwi4_client import PWI4

pwi4 = PWI4()

def main():
    connect_to_mount()
    enable_motors()
    find_home()

def connect_to_mount():
    print("Connecting to mount...")
    pwi4.mount_connect()
    while not pwi4.status().mount.is_connected:
        time.sleep(1)
    print("Done")

def enable_motors():
    print("Enabling motors")
    pwi4.mount_enable(0)
    pwi4.mount_enable(1)
    while True:
        status = pwi4.status()
        if status.mount.axis0.is_enabled and status.mount.axis1.is_enabled:
            break
        time.sleep(1)
    print("Done")

def find_home():
    print("Finding home")
    pwi4.mount_find_home()
    last_axis0_pos_degs = -99999
    last_axis1_pos_degs = -99999
    while True:
        status = pwi4.status()
        delta_axis0_pos_degs = status.mount.axis0.position_degs - last_axis0_pos_degs
        delta_axis1_pos_degs = status.mount.axis1.position_degs - last_axis1_pos_degs

        if abs(delta_axis0_pos_degs) < 0.001 and abs(delta_axis1_pos_degs) < 0.001:
            break

        last_axis0_pos_degs = status.mount.axis0.position_degs
        last_axis1_pos_degs = status.mount.axis1.position_degs

        time.sleep(1)
    print("Done")

if __name__ == "__main__":
    main()
