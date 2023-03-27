import subprocess

def resize_console_window(num_columns, buffer_length=5000):
    """
    Resize a Windows cmd.exe console to the specified width
    and buffer length
    """
    
    subprocess.call("mode con cols=%d lines=%d" % (
        num_columns,
        buffer_length
        ), 
        shell=True)