import relimport # Set up our path so that iotalib can be found

# Built-in Python imports
import glob
import logging
import os
import re
import shutil
import time

# iotalib imports
from iotalib import config # to get path to config folder
from iotalib import logutil
from iotalib import ssh
from iotalib import paths

# Configuration. TODO - move this to a config file
remote_username = "talon"
remote_host = "macroconsortium.org"
remote_port = 22
send_sls_now_interval_seconds = 120  # Copy local telrun.sls to remote telrun.now no more frequently than this many seconds
identity_file = paths.config_path("pyscope_chronos.ppk")


pscp_exe = paths.putty_path("pscp.exe")
plink_exe = paths.putty_path("plink.exe")

local_image_dir = paths.image_dir()
local_transferred_image_dir = os.path.join(paths.image_dir(), "transferred")
local_duplicate_image_dir = os.path.join(paths.image_dir(), "duplicate") # If image already exists in transferred dir, copy it here (with a unique filename) instead
remote_image_dir = "/usr/local/telescope/user/images"

valid_file_extensions = [".fts", ".fits", ".fit"]

# Keep track of the last time we sent telrun.sls to the remote server
# so that we don't re-send it too frequently
last_telrun_send_time = 0

def main():
    while True:
        try:
            copy_telrun()
            have_more_images = copy_images(3)

            if not have_more_images:
                time.sleep(60)
        except Exception as ex:
            logging.exception("Error!!! Trying to sleep it off...")
            time.sleep(10)
    
def copy_telrun():
    global last_telrun_send_time

    local_telrun_incoming_path = paths.telrun_sls_path("telrun.incoming")
    local_telrun_sls_path = paths.telrun_sls_path("telrun.sls")
    local_telrun_new_path = paths.telrun_sls_path("telrun.new")
    remote_telrun_sls_path = "/usr/local/telescope/archive/telrun/telrun.sls"    
    remote_telrun_sent_path = "/usr/local/telescope/archive/telrun/telrun.sent"
    remote_telrun_now_incoming_path = "/usr/local/telescope/archive/telrun/telrun.now.incoming"
    remote_telrun_now_path = "/usr/local/telescope/archive/telrun/telrun.now"

    logging.info("Copying telrun.sls from %s", remote_host)
    scp_return_code = ssh.secure_copy(
        remote_username + "@" + remote_host + ":" + remote_telrun_sls_path, 
        local_telrun_incoming_path,
        remote_port=remote_port,
        scp_executable=pscp_exe,
        identity_file=identity_file
        )

    if scp_return_code != 0:
        logging.info("telrun.sls NOT copied")
    else:
        logging.info("Renaming local %s to %s", local_telrun_incoming_path, local_telrun_new_path)
        shutil.move(local_telrun_incoming_path, local_telrun_new_path)

        logging.info("Renaming remote %s to %s", remote_telrun_sls_path, remote_telrun_sent_path)
        move_command = "mv '%s' '%s'" % (remote_telrun_sls_path, remote_telrun_sent_path)
        ssh_return_code = ssh.ssh_command(
            move_command,
            remote_username,
            remote_host,
            remote_port=remote_port,
            ssh_executable=plink_exe,
            identity_file=identity_file
            )

        if ssh_return_code != 0:
            logging.info("Remote file NOT renamed successfully")

    if time.time() - last_telrun_send_time < send_sls_now_interval_seconds:
        logging.info("Too soon to re-send telrun.sls back to remote server")
    elif not os.path.isfile(local_telrun_sls_path):
        logging.info("No current telrun.sls to send back to remote server")
    else:
        logging.info("Sending current telrun.sls to %s", remote_host)
        scp_return_code = ssh.secure_copy(
            local_telrun_sls_path,
            remote_username + "@" + remote_host + ":" + remote_telrun_now_incoming_path, 
            remote_port=remote_port,
            scp_executable=pscp_exe,
            identity_file=identity_file
            )
        if scp_return_code != 0:
            logging.warn("Error copying telrun.sls back to server")

        else:
            logging.info("Renaming remote %s to %s", remote_telrun_now_incoming_path, remote_telrun_now_path)
            move_command = "mv '%s' '%s'" % (remote_telrun_now_incoming_path, remote_telrun_now_path)
            ssh_return_code = ssh.ssh_command(
                move_command,
                remote_username,
                remote_host,
                remote_port=remote_port,
                ssh_executable=plink_exe,
                identity_file=identity_file
                )

            if ssh_return_code != 0:
                logging.warn("Remote file NOT renamed successfully")
            else:
                last_telrun_send_time = time.time()


def copy_images(max_image_count):
    """
    Copy images to remote server.
    Return after copying max_image_count images (e.g. so that we can 
    periodically check for a new .sls file)

    Returns True if more images remain to be copied when this function
    returns, or False if all images have been copied.
    """
    
    files = []
    
    for file_or_dir in os.listdir(paths.image_dir()):
        file_or_dir = os.path.join(paths.image_dir(), file_or_dir)
        if not os.path.isfile(file_or_dir):
            continue
        filepath = file_or_dir

        # Only consider files containing one of the valid file extensions
        for file_extension in valid_file_extensions:
            if filepath.endswith(file_extension):
                files.append(filepath)
                break
        
    num_files = len(files)
    for i, filepath in enumerate(files):
        if i >= max_image_count:
            return True # More images need to be copied, but return for now to check on other things

        logging.info("File %s of %s (%s images remain)", i+1, min(num_files, max_image_count), num_files)
        
        logging.info("Copying %s", filepath)
        
        scp_return_code = ssh.secure_copy(
            filepath,
            remote_username + "@" + remote_host + ":" + remote_image_dir, 
            remote_port=remote_port,
            scp_executable=pscp_exe,
            identity_file=identity_file
            )

        if scp_return_code != 0:
            logging.info("Error transferring image")
            continue

        
        if not os.path.exists(local_transferred_image_dir):
            logging.info("Creating %s", local_transferred_image_dir)
            os.makedirs(local_transferred_image_dir)

        if not os.path.exists(local_duplicate_image_dir):
            logging.info("Creating %s", local_duplicate_image_dir)
            os.makedirs(local_duplicate_image_dir)
            
        filename = os.path.basename(filepath)
        dest_filepath_transferred = os.path.join(local_transferred_image_dir, filename)
        dest_filepath_duplicate = os.path.join(local_duplicate_image_dir, filename)
        logging.info("local_transferred_image_dir = %s", local_transferred_image_dir)
        logging.info("local_duplicate_image_dir = %s", local_duplicate_image_dir)
        logging.info("filepath = %s", filepath)
        logging.info("filename = %s", filename)
        logging.info("dest_filepath_transferred = %s", dest_filepath_transferred)
        logging.info("dest_filepath_duplicate = %s", dest_filepath_duplicate)

        if os.path.exists(dest_filepath_transferred):
            logging.warn("File %s already exists", dest_filepath_transferred)
            for i in range(999):
                dest_filepath_duplicate_unique = dest_filepath_duplicate + "." + str(i)
                if not os.path.exists(dest_filepath_duplicate_unique):
                    break
            logging.warn("Moving to %s", dest_filepath_duplicate_unique)
            shutil.move(filepath, dest_filepath_duplicate_unique)
        else:
            logging.info("Moving to %s", local_transferred_image_dir)
            shutil.move(filepath, local_transferred_image_dir)

    return False # No more images to copy
    
        
if __name__ == "__main__":
    logutil.setup_log("syncfiles.log")
    main()
