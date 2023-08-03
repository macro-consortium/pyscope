import socket
import struct
import binascii
import sys

from .cover_calibrator import CoverCalibrator

class IPCoverCalibrator(CoverCalibrator):
    def __init__(self, tcp_ip, tcp_port, buffer_size):
        self._tcp_ip = tcp_ip
        self._tcp_port = tcp_port
        self._buffer_size = buffer_size
    
    def CalibratorOff(self):
        return self._send_packet(0)

    def CalibratorOn(self, Brightness):
        return self._send_packet(Brightness)

    def CloseCover(self):
        raise NotImplementedError

    def HaltCover(self):
        raise NotImplementedError

    def OpenCover(self):
        raise NotImplementedError

    @property
    def Brightness(self):
        pass

    @property
    def CalibratorState(self):
        return

    @property
    def CoverState(self):
        return

    @property
    def MaxBrightness(self):
        return 254
    
    def _send_packet(self, intensity):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.tcp_ip, self.tcp_port))

        # Create 4 byte array
        my_bytes = bytearray()
        my_bytes.append(253);       my_bytes.append(0)
        my_bytes.append(intensity); my_bytes.append(1)

        try:
            s.send(my_bytes)
        except:
            return False
        finally:
            data = s.recv(self.buffer_size)
            if data != 'U': return False
            s.close()
            return True
    
    @property
    def tcp_ip(self):
        return self._tcp_ip
    
    @property
    def tcp_port(self):
        return self._tcp_port

    @property
    def buffer_size(self):
        return self._buffer_size