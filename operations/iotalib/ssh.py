"""
Wrapper around a Secure Copy (scp) client program such as the "pscp"
program that comes with PuTTY
"""

# Built-in Python imports
import logging
import subprocess


def secure_copy(source_file, dest_file, remote_port=22, scp_executable="pscp", password=None, identity_file=None):
    """
    Wrapper for running an SSH Secure Copy program, such as scp or pscp.

    source_file: The original file to copy. Local files are specified by path; remote files are specified via the "user@host:path" format
    dest_file: The destination of the copied file. Local targets are specified by path; remote targets are specified via the "user@host:path" format
    remote_port: The TCP port for the remote SSH server (22 by default)
    scp_executable: The path to the "scp"-compatible executable
    password: If not None, will attempt password authentication using the given string value
              (Only works with putty "pscp", not standard "scp")
    identity_file: If not None, will attempt to use private key authentication using specified identity file 

    Note: if neither "password" nor "identity_file" is specified, scp will probably prompt for a password on STDIN
    """

    enable_compression_flag = "-C"
    remote_port_flag = "-P"
    password_flag = "-pw"
    private_key_flag = "-i"

    args = [
        scp_executable,
        enable_compression_flag,
        remote_port_flag,
        str(remote_port)
        ]
    
    
    if password is not None:
        args.append(password_flag)
        args.append(password)

    if identity_file is not None:
        args.append(private_key_flag)
        args.append(identity_file)

    args.append(source_file)
    args.append(dest_file)

    logging.debug("subprocess.call(%s)", args)
    return_code = subprocess.call(args)
    logging.debug("return code = %s", return_code)
    
    return return_code

def ssh_command(remote_command, remote_user, remote_host, remote_port=22, ssh_executable="plink", password=None, identity_file=None):
    """
    Wrapper for executing a command on a remote server over ssh

    remote_command: The command to execute on the remote machine; e.g. "mv file1 file2"
    remote_user: The login name to use on the remote machine
    remote_host: The hostname or IP address of the remote machine
    remote_port: The TCP port for the remote SSH server (22 by default)
    ssh_executable: The path to the "ssh"-compatible executable
    password: If not None, will attempt password authentication using the given string value
              (Only works with putty "pscp", not standard "scp")
    identity_file: If not None, will attempt to use private key authentication using specified identity file 
    
    Note: if neither "password" nor "identity_file" is specified, scp will probably prompt for a password on STDIN
    """

    enable_compression_flag = "-C"
    remote_port_flag = "-P"
    password_flag = "-pw"
    private_key_flag = "-i"

    args = [
        ssh_executable,
        enable_compression_flag,
        remote_port_flag,
        str(remote_port)
        ]
    
    
    if password is not None:
        args.append(password_flag)
        args.append(password)

    if identity_file is not None:
        args.append(private_key_flag)
        args.append(identity_file)

    args.append(remote_user + "@" + remote_host)
    args.append(remote_command)

    logging.debug("subprocess.call(%s)", args)
    return_code = subprocess.call(args)
    logging.debug("return code = %s", return_code)

    return return_code

def test():
    logging.basicConfig(level=logging.DEBUG)

    password = input("Enter password:")

    #secure_copy("talon@deimos.physics.uiowa.edu:.ssh/id_dsa", "./id_dsa.talon@deimos", remote_port=53222, password=password)
    #secure_copy("talon@deimos.physics.uiowa.edu:/usr/local/telescope/archive/telrun/telrun.sls", ".", remote_port=53222, identity_file="id_dsa.talon@deimos")

if __name__ == "__main__":
    test()
