"""
Sensortherm METIS
========

How ya garn?
"""

from enum import Enum
from typing import Annotated, Optional
from annotated_types import Ge

import serial

class MeasurementChannel(Enum):
    """
    Measurement channel
    """

    TWO_COLOUR              = 0 # 2-colour ratiometric measurement
    SINGLE_COLOUR_CHANNEL_1 = 1 # 1 colour measurement, channel 1
    SINGLE_COLOUR_CHANNEL_2 = 1 # 1 colour measurement, channel 2

class AnalogOutputMode(Enum):
    """
    Analog output mode
    """

    CURRENT_0_TO_20MA = 0 # 0-20mA
    CURRENT_4_TO_20MA = 1 # 4-20mA

class TargetingLightState(Enum):
    """
    Targeting light state
    """

    OFF    = 0 # Targeting light off
    ON     = 1 # Targeting light on
    TOGGLE = 2 # Toggle targeting light state

class Language(Enum):
    """
    Display panel interface language
    """

    ENGLISH  = 0 # English/Englisch
    ENGLISCH = 0 # Englisch/English
    GERMAN   = 1 # German/Deutsch
    DEUTSCH  = 1 # Deutsch/German

class Command(Enum):
    """
    Commands
    """

    REFERENCE_NUMBER_SHORT = 'bn'
    REFERENCE_NUMBER_LONG = 'bn1'
    TARGETING_LIGHT = 'la'
    SERIAL_NUMBER = 'sn'

class Metis():
    """
    Sensortherm METIS device
    """

    def __init__(self, address : Annotated[int, Ge(0)], stream : serial.Serial, debug: bool = False):
        self._address = address
        self._stream = stream
        self._stream.write(b'\r')
        self._debug = debug

    def _send_command(self, command : Command, data : Optional[str] = None) -> bytes:
        command_string = f'{self._address:02d}{command.value}{data or ""}\r'
        if self._debug:
            print(command_string)
        self._stream.write(command_string.encode('ascii'))
        self._stream.flush()
        return self._stream.read_until(b'\r')

    def _targeting_light(self, state : TargetingLightState):
        # TODO I am not sure if the address is encoded in hex or decimal format; need to test
        return self._send_command(Command.TARGETING_LIGHT, f'{state.value}')
        
    def toggle_laser(self):
        """
        Toggle targeting light state
        """
        return self._targeting_light(state = TargetingLightState.TOGGLE)

    def laser_on(self):
        """
        Turn targeting light on
        """
        return self._targeting_light(state = TargetingLightState.ON)

    def laser_off(self):
        """
        Turn targeting light off
        """
        return self._targeting_light(state = TargetingLightState.OFF)

    def get_type_short(self) -> str:
        """
        Get reference type, 18 digits
        """
        return self._send_command(Command.REFERENCE_NUMBER_SHORT).decode('ascii')

    def get_type_long(self) -> str:
        """
        Get reference type, 21 digits
        """
        return self._send_command(Command.REFERENCE_NUMBER_LONG).decode('ascii')

    def get_serial(self) -> str:
        """
        Get device serial number
        """
        return self._send_command(Command.SERIAL_NUMBER).decode('ascii')
