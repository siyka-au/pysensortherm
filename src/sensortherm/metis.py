"""
Sensortherm METIS
========

How ya garn?
"""

from ast import Tuple
from collections import namedtuple
from enum import Enum
from typing import Annotated, Any, Callable, Dict, List, Optional, Tuple, TypedDict
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
    REFERENCE_NUMBER_SHORT    = 'bn'
    REFERENCE_NUMBER_LONG     = 'bn1'
    TARGETING_LIGHT           = 'la'
    SERIAL_NUMBER             = 'sn'
    READ_MEASURED_TEMPERATURE = 'mw'
    READ_TEMPERATURE_SENSOR   = 'tsc'
    SIGNAL_STRENGTH           = 'sl'
    BUFFER_MODE               = 'bum'
    BUFFER_READ               = 'bup'

class InternalTemperatureSensor(Enum):
    """
    Internal temperature sensor
    """
    ONE = 0
    TWO = 1

class BufferMode(Enum):
    """
    Buffer mode
    """
    ZERO  = 0
    ONE   = 1
    TWO   = 2
    THREE = 3

class Status(TypedDict):
    """
    Status
    """
    fahrenheit_active : bool
    digital_output_1 : bool
    digital_output_2 : bool
    digital_output_3 : bool
    digital_input_1 : bool
    digital_input_2 : bool
    digital_input_3 : bool
    controlling_active : bool
    auto_tune_active : bool
    auto_tune_at_controller_start : bool
    device_ready : bool
    device_hardware_error : bool
    controller_finished_successful : bool
    targeting_light_active : bool
    setup0 : bool
    setup1 : bool
    setup2 : bool
    display0 : bool
    display1 : bool
    display2 : bool

class BufferData:
    """
    Buffer data
    """
    measured_value                  : Optional[float]
    temperature_2_colour            : Optional[float]
    temperature_1_colour_channel_1  : Optional[float]
    temperature_1_colour_channel_2  : Optional[float]
    signal_strength                 : Optional[float]
    setpoint_value_at_ramp_function : Optional[float]
    controller_manipulated_variable : Optional[float]
    analog_input                    : Optional[int]
    measured_temperature            : Optional[float]
    status                          : Optional[Status]

class MetisException(Exception):
    """
    Sensortherm METIS device exception
    """

class Metis():
    """
    Sensortherm METIS device
    """

    def __init__(self, address : Annotated[int, Ge(0)],
                 stream : serial.Serial,
                 debug: bool = False):
        self._address = address
        self._stream = stream
        self._stream.write(b'\r')
        self._debug = debug

    def _str_command(self, command : Command, data : Optional[str] = None) -> bytes:
        command_string = f'{self._address:02d}{command.value}{data or ""}\r'
        if self._debug:
            print(command_string)
        self._stream.write(command_string.encode('ascii'))
        self._stream.flush()
        answer = self._stream.read_until(b'\r')[:-1]
        if answer == b'no':
            raise MetisException('Error sending command')
        else:
            return answer

    def _int_command(self, command : Command,
                                      data : Optional[str] = None) -> int:
        hex_string = self._str_command(command, data)
        return _parse_int(hex_string)

    def _targeting_light(self, state : TargetingLightState):
        # TODO I am not sure if the address is encoded in hex or decimal format; need to test
        return self._str_command(Command.TARGETING_LIGHT, f'{state.value}')

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

    def read_type_short(self) -> str:
        """
        Read reference type, 18 digits
        """
        return self._str_command(Command.REFERENCE_NUMBER_SHORT).decode('ascii')

    def read_type_long(self) -> str:
        """
        Read reference type, 21 digits
        """
        return self._str_command(Command.REFERENCE_NUMBER_LONG).decode('ascii')

    def read_serial(self) -> str:
        """
        Read device serial number
        """
        return self._str_command(Command.SERIAL_NUMBER).decode('ascii')

    def read_temperature(self, channel : MeasurementChannel) -> float:
        """
        Read temperature measurement channel
        """
        return self._int_command(
            Command.READ_MEASURED_TEMPERATURE, f'{channel.value}') / 10.0

    def read_2_colour_temoperature(self) -> float:
        """
        Read 2 colour (ratiometric) temperature
        """
        return self.read_temperature(MeasurementChannel.TWO_COLOUR)

    def read_single_colour_channel_1(self) -> float:
        """
        Read single colour temperature, channel 1
        """
        return self.read_temperature(MeasurementChannel.SINGLE_COLOUR_CHANNEL_1)

    def read_single_colour_channel_2(self) -> float:
        """
        Read single colour temperature, channel 2
        """
        return self.read_temperature(MeasurementChannel.SINGLE_COLOUR_CHANNEL_2)

    def read_temperature_sensor(self, sensor : InternalTemperatureSensor) -> float:
        """
        Read internal temperature sensor
        """
        return self._int_command(Command.READ_TEMPERATURE_SENSOR,
                                                  f'{sensor.value}') / 256.0

    def read_temperature_sensors(self) -> Tuple[float, float]:
        """
        Read internal temperature sensors
        """
        one = self.read_temperature_sensor(InternalTemperatureSensor.ONE)
        two = self.read_temperature_sensor(InternalTemperatureSensor.TWO)
        return (one, two)

    def read_signal_strength(self) -> float:
        """
        Read measured signal strength
        """
        return self._int_command(Command.SIGNAL_STRENGTH,) / 10.0

    def get_buffer_mode(self) -> BufferMode:
        """
        Get buffer mode
        """
        answer = self._int_command(Command.BUFFER_MODE)
        return BufferMode(answer)

    def set_buffer_mode(self, buffer_mode : BufferMode):
        """
        Set buffer mode
        """
        self._str_command(Command.BUFFER_MODE, f'{buffer_mode.value:02x}')

    def read_buffer(self):
        """
        Read buffer
        """
        answer = self._str_command(Command.BUFFER_READ)
        buffer = BufferData #(None, None, None, None, None, None, None, None, None, None)
        fields : List[_Field] = [
            _Field(buffer.temperature_2_colour,            4, _parse_float,         (10,)),
            _Field(buffer.temperature_1_colour_channel_1,  4, _parse_float,         (10,)),
            _Field(buffer.temperature_1_colour_channel_2,  4, _parse_float,         (10,)),
            _Field(buffer.setpoint_value_at_ramp_function, 4, _parse_float,         (10,)),
            _Field(buffer.controller_manipulated_variable, 4, _parse_float,         (10,)),
            _Field(buffer.signal_strength,                 4, _parse_float,         (10,)),
            _Field(buffer.data_status_byte_0,              2, _parse_data_status_0,    ()),
            _Field(buffer.data_status_byte_1,              2, _parse_data_status_1,    ()),
            _Field(buffer.data_status_byte_2,              2, _parse_data_status_2,    ()),
            _Field(buffer.data_status_byte_3,              2, _parse_data_status_3,    ()),
            _Field(buffer.analog_input,                    4, _parse_int,              ()),
            _Field(buffer._l_unused,                       4, _noop,                   ()),
            _Field(buffer.measured_temperature,            4, _parse_float,         (10,)),
            _Field(buffer._m_unused,                       4, _noop,                   ())
        ]
        data : Dict[str, Any] = {}

        index : int = 0
        for field in fields:
            field_data : bytes = answer[index:index + field.length]
            if self._debug:
                print(f'field: {field.name}, ' +
                      f'index: {index}, ' +
                      f'field_length: {field.length}, ' +
                      f'data:{field_data}')
            args = field.arguments
            value = field.parser(field_data, *args)
            field.name = value
            index = index + field.length
            if index >= len(answer):
                break
        # If the buffer type is 0, it needs to fix the data
        if len(answer) == 4:
            data['measured_temperature'] = data['temperature_2_colour']
            del data['temperature_2_colour']

        # Remove unused data
        del data['_l_unused']
        del data['_m_unused']

        return data

_Field = namedtuple('Field', ['name', 'length', 'parser', 'arguments'])

class _DataStatus0(TypedDict):
    """
    Data status byte 0
    """
    fahrenheit_active : bool
    digital_output_1  : bool
    digital_output_2  : bool
    digital_output_3  : bool
    digital_input_1   : bool
    digital_input_2   : bool
    digital_input_3   : bool

class _DataStatus1(TypedDict):
    """
    Data status byte 1
    """
    controlling_active             : bool
    auto_tune_active               : bool
    auto_tune_at_controller_start  : bool
    device_ready                   : bool
    device_hardware_error          : bool
    controller_finished_successful : bool
    targeting_light_active         : bool

class _DataStatus2(TypedDict):
    """
    Data status byte 2
    """
    setup0 : bool
    setup1 : bool
    setup2 : bool

class _DataStatus3(TypedDict):
    display0 : bool
    display1 : bool
    display2 : bool

def _parse_int(data : bytes) -> int:
    return int(data.decode('ascii'), 16)

def _parse_float(data : bytes, divider : int) -> float:
    return _parse_int(data) / divider

def _parse_bits(data : bytes) -> Tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
    i = _parse_int(data)
    return (
        (i & 1<<0) != 0,
        (i & 1<<1) != 0,
        (i & 1<<2) != 0,
        (i & 1<<3) != 0,
        (i & 1<<4) != 0,
        (i & 1<<5) != 0,
        (i & 1<<6) != 0,
        (i & 1<<7) != 0
    )

def _parse_data_status_0(data : bytes) -> _DataStatus0:
    bit_data = _parse_bits(data)
    return _DataStatus0(
        fahrenheit_active = bit_data[0],
        digital_output_1  = bit_data[1],
        digital_output_2  = bit_data[2],
        digital_output_3  = bit_data[3],
        digital_input_1   = bit_data[4],
        digital_input_2   = bit_data[5],
        digital_input_3   = bit_data[6]
    )

def _parse_data_status_1(data : bytes) -> _DataStatus1:
    bit_data = _parse_bits(data)
    return _DataStatus1(
        controlling_active             = bit_data[0],
        auto_tune_active               = bit_data[1],
        auto_tune_at_controller_start  = bit_data[2],
        device_ready                   = bit_data[3],
        device_hardware_error          = bit_data[4],
        controller_finished_successful = bit_data[5],
        targeting_light_active         = bit_data[6]
    )

def _parse_data_status_2(data : bytes) -> _DataStatus2:
    bit_data = _parse_bits(data)
    return _DataStatus2(
        setup0 = bit_data[0],
        setup1 = bit_data[1],
        setup2 = bit_data[2]
    )

def _parse_data_status_3(data : bytes) -> _DataStatus3:
    bit_data = _parse_bits(data)
    return _DataStatus3(
        display0 = bit_data[0],
        display1 = bit_data[1],
        display2 = bit_data[2]
    )

def _noop(_ : bytes) -> None:
    return None
