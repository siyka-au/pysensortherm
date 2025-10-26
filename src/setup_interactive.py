import serial

from sensortherm.metis import Metis, MeasurementChannel, Language, TargetingLightState, InternalTemperatureSensor, BufferMode, _DataStatus0, _DataStatus1, _DataStatus2, _DataStatus3

ser = serial.Serial('/dev/ttyUSB0', 115_200, timeout=1, parity=serial.PARITY_EVEN)

m3 = Metis(0, ser, debug=True)
