import serial

from sensortherm.metis import Metis

ser = serial.Serial('/dev/ttyUSB0', 115_200, timeout=1, parity=serial.PARITY_EVEN)

m3 = Metis(0, ser)
