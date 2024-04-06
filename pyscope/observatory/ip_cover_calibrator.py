import binascii
import logging
import socket
import struct
import sys

from .cover_calibrator import CoverCalibrator

logger = logging.getLogger(__name__)


class IPCoverCalibrator(CoverCalibrator):
    def __init__(self, tcp_ip, tcp_port, buffer_size):
        self._tcp_ip = tcp_ip
        self._tcp_port = tcp_port
        self._buffer_size = buffer_size

    def CalibratorOff(self):
        logger.debug("IPCoverCalibrator.CalibratorOff called")
        return self._send_packet(0)

    def CalibratorOn(self, Brightness):
        logger.debug(f"CalibratorOn called with Brightness={Brightness}")
        return self._send_packet(Brightness)

    def CloseCover(self):
        logger.debug("IPCoverCalibrator.CloseCover called")
        raise NotImplementedError

    def HaltCover(self):
        logger.debug("IPCoverCalibrator.HaltCover called")
        raise NotImplementedError

    def OpenCover(self):
        logger.debug("IPCoverCalibrator.OpenCover called")
        raise NotImplementedError

    @property
    def Brightness(self):
        logger.debug("IPCoverCalibrator.Brightness called")
        return

    @property
    def CalibratorState(self):
        logger.debug("IPCoverCalibrator.CalibratorState called")
        return

    @property
    def CoverState(self):
        logger.debug("IPCoverCalibrator.CoverState called")
        return

    @property
    def MaxBrightness(self):
        logger.debug("IPCoverCalibrator.MaxBrightness called")
        return 254

    def _send_packet(self, intensity):
        logger.debug(f"_send_packet called with intensity={intensity}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.tcp_ip, self.tcp_port))

        # Create 4 byte array
        my_bytes = bytearray()
        my_bytes.append(253)
        my_bytes.append(0)
        my_bytes.append(intensity)
        my_bytes.append(1)

        try:
            s.send(my_bytes)
        except:
            return False
        finally:
            data = s.recv(self.buffer_size)
            if data != b"U":
                return False
            s.close()
            return True

    @property
    def tcp_ip(self):
        logger.debug("IPCoverCalibrator.tcp_ip called")
        return self._tcp_ip

    @property
    def tcp_port(self):
        logger.debug("IPCoverCalibrator.tcp_port called")
        return self._tcp_port

    @property
    def buffer_size(self):
        logger.debug("IPCoverCalibrator.buffer_size called")
        return self._buffer_size
