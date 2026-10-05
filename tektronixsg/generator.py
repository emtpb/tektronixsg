import warnings

import pyvisa as vi
import time

from .channel import Channel

TRIGGER_SOURCE = {"timer": "TIM", "external": "EXT"}

busy_resources = {}

MANUFACTURER_IDS = [
    "1689",  # Tektronix manufacturer ID
    "0x699",  # Tektronix hex
]

DEVICE_IDS = [
    "851",  # AFG1022 model code
    "0x0353",  # AFG1022 hex
    "856",  # AFG31052 model code
    "0x0358",  # AFG31052 hex
]


def list_connected_devices():
    """List all connected VISA device addresses.

    Returns:
        list: All connected VISA devices. Those can be used to explicitly
        initialize a specific device via the resource parameter of
        :class:`.SignalGenerator`.
    """
    rm = vi.ResourceManager()
    resources = rm.list_resources()
    return resources


def get_device_id(resource):
    """
    Get the Identification Number of the specified resource.

    Args:
        resource (str): The resource from which to get the IDN.

    Returns:
        dict[str, str]: The 'Manufacturer', 'Model' and 'Serial Number'.
    """
    try:
        if resource not in busy_resources:
            rm = vi.ResourceManager()
            device = rm.open_resource(resource)
            idn = device.query("*IDN?")
            parts = idn.split(",")
            resource_info = {
                "Resource": resource,
                "Manufacturer": parts[0],
                "Model": parts[1],
                "Serial Number": parts[2],
            }
            busy_resources[resource] = resource_info
            return resource_info
        else:
            return busy_resources[resource]

    except (vi.errors.VisaIOError, ValueError):
        return None


def list_connected_tektronix_generators():
    """List all connected signal generators from tektronix."""
    resource_list = list_connected_devices()

    # delete old unplugged devices from the busy_resources list
    wrong_keys = []
    for key in busy_resources:
        if key not in resource_list:
            wrong_keys.append(key)
    for wrong_key in wrong_keys:
        busy_resources.pop(wrong_key, None)

    device_list = []
    for res_num in range(len(resource_list)):
        parts = resource_list[res_num].split("::")

        if len(parts) < 3:
            continue

        if (
            "USB" in parts[0]
            and (parts[1] in MANUFACTURER_IDS)
            and (parts[2] in DEVICE_IDS)
        ):
            device = get_device_id(resource_list[res_num])
            if device is not None:
                device_list.append(device)

    return device_list


class SignalGenerator:
    """Interface for tektronix signal generators.

    Supports the AFG 1022 and the AFG 31052.

    Attributes:
        channels (list): List of all channels.
        connected_device (str): The specific tektronix device which is
                                connected.
    """

    def __init__(self, resource: str | None = None, serial_number: str | None = None):
        """Initialize the instrument connection using the VISA interface.

        The device selection follows this precedence:

        1. If ``resource`` is specified, it is used to connect to the instrument.
           In this case, ``serial_number`` is ignored.
        2. If only ``serial_number`` is specified, the connected Tektronix device
           with the matching serial number is selected.
        3. If neither is specified, the first detected Tektronix device is used.

        Args:
            resource (str, optional): VISA resource name of the instrument. If
                specified, this takes precedence over ``serial_number``. If not
                specified, the device is selected using ``serial_number`` or, if
                that is also unspecified, the first device returned by
                ``list_connected_tektronix_generators()``.

            serial_number (str, optional): Serial number of the Tektronix device
                to connect to. This parameter is ignored if ``resource`` is
                specified.

        Raises:
            RuntimeError: If no Tektronix device is detected, or if the device
                specified by ``resource`` or ``serial_number`` cannot be found.
        """

        visa_name = ""
        if resource:
            visa_name = resource
        else:
            possible_devices = list_connected_tektronix_generators()

            if not possible_devices:
                raise RuntimeError("Could not find any tektronix devices")

            if serial_number:
                not_found = True
                for device in possible_devices:
                    if device["Serial Number"] == serial_number:
                        visa_name = device["Resource"]
                        not_found = False
                        break
                if not_found:
                    raise RuntimeError("Could not find specified tektronix device")
            else:
                # Fallback to first detected tektronix device
                visa_name = possible_devices[0]["Resource"]

        connected_resource = None
        self._resource_manager = vi.ResourceManager()
        self._instrument = self._resource_manager.open_resource(visa_name)
        connected_resource = visa_name

        if connected_resource is not None:
            idn = self._instrument.query("*IDN?")
            parts = idn.split(",")
            resource_info = {
                "Manufacturer": parts[0],
                "Model": parts[1],
                "Serial Number": parts[2],
            }
            busy_resources[connected_resource] = resource_info

        self.channels = [Channel(self, "1"), Channel(self, "2")]
        self.connected_device = self.instrument_info.split(",")[1]

    def reset(self):
        """Reset the instrument."""
        self.write("*RST")
        # Delay preventing a buffer overflow since reset operation takes time
        time.sleep(0.5)

    def clear(self):
        """Clear event registers and error queue."""
        self.write("*CLS")

    def send_trigger(self):
        """Trigger signal generator."""
        self.write("*TRG")

    @property
    def instrument_info(self):
        """Get instrument information."""
        return self._instrument.query("*IDN?")

    @property
    def _identification_number(self):
        """
        Get the instrument type and software version.

        Returns:
            str: The IDN in the following format: <manufacturer_string>,<model>,<serial_number>,<software_revision>
        """
        return self._query("*IDN?")

    @property
    def device_model(self):
        """
        Get the device model.

        Returns:
            str: The device model
        """
        return self._identification_number.split(",")[1]

    @property
    def serial_number(self):
        """
        Get the device serial number.

        Returns:
            str: The device serial number
        """
        return self._identification_number.split(",")[2]

    def wait(self):
        """Prevent instrument from executing further commands until
        all pending commands are complete."""
        self.write("*WAI")

    def close(self):
        """Closes the instrument."""
        self._instrument.close()

    def error_check(self):
        """Checks for errors.

        Raises:
            ValueError: If an error occurs the error message will be
                included in exception.
        """
        # Used to clear the error bit in the device
        if self.connected_device == "AFG31052":
            self._instrument.query("*ESR?")
        error = self._instrument.query("SYSTem:ERRor?")
        error_code, error_message = error.split(",")
        error_code = int(error_code)
        # Ignore events
        if self.connected_device == "AFG31052" and -899 <= error_code <= -500:
            return
        if error_code != 0:
            warnings.warn(error_message)

    def write_data_emom(self, data, memory=1):
        """Write arbitrary data to an edit memory.

        Args:
            data(numpy.ndarray): Data to be written to the editable memory.
                                 Data has to be a list or numpy array
                                 with values ranging from 0 to 16383
                                 (8191 AFG 1022).
                                 0 corresponds to the minimum
                                 voltage and 16383 to the maximum voltage
                                 of the current set voltage range.
            memory(int): Memory to which should be written. Ignored when
                         connected device is an AFG1022. Else determines
                         channel number the signal is available on.
        """
        if self.connected_device == "AFG1022":
            memory = ""
        self._instrument.write_binary_values(
            "DATA:DATA EMEM{},".format(memory), data, datatype="h",
            is_big_endian=True)

    def read_data_emom(self, memory=1):
        """Read arbitrary data from an edit memory.

        Args:
            memory(int): Memory which should be read. Ignored when connected
                         device is an AFG1022. Else determines channel number
                         the signal is available on.
        Returns:
            list: Values ranging from 0 to 16383.
            0 corresponds to the minimum voltage and 16383 to the
            maximum voltage of the current set voltage range.
        """
        if self.connected_device == "AFG1022":
            memory = ""
        return self._instrument.query_binary_values(
            "DATA:DATA? EMEM{}".format(memory),
            datatype="h", is_big_endian=True)

    @property
    def trigger_source(self):
        """Get or set the trigger source of the burst.

        Possible options are stated in TRIGGER_SOURCE.

        Not supported by the AFG1022.
        """
        if self.connected_device == "AFG1022":
            raise NotImplementedError
        value = self.query_str("TRIG:SOUR?")
        for item in TRIGGER_SOURCE.items():
            if item[1] == value:
                return item[0]

    @trigger_source.setter
    def trigger_source(self, value):
        if self.connected_device == "AFG1022":
            raise NotImplementedError
        self.write("TRIG:SOUR {}".format(TRIGGER_SOURCE[value]))

    @property
    def trigger_timer(self):
        """Set or get the period of timer in seconds.

        The timer periodically forces an internal trigger.

        Not supported by the AFG1022.
        """
        if self.connected_device == "AFG1022":
            raise NotImplementedError
        return self.query_float("TRIG:TIM?")

    @trigger_timer.setter
    def trigger_timer(self, value):
        if self.connected_device == "AFG1022":
            raise NotImplementedError
        self.write("TRIG:TIM {}".format(value))

    def query_int(self, query_string):
        """Query from the signal generator and return type as int."""
        return int(
            float(self.query(query_string).replace("\n", "")))

    def query_float(self, query_string):
        """Query from the signal generator and return type as float."""
        return float(self.query(query_string).replace("\n", ""))

    def query_str(self, query_string):
        """Query from the signal generator and return type as str."""
        return self.query(query_string).replace("\n", "")

    def query_bool(self, query_string):
        """Query from the signal generator and return type as bool."""
        return bool(
            int(self.query(query_string).replace("\n", "")))

    def query(self, query_string):
        """Query from the instrument."""
        query = self._instrument.query(query_string)
        self.error_check()
        return query

    def write(self, write_string):
        """Write a string to the instrument."""
        self._instrument.write(write_string)
        # Add a delay to prevent too many writes to the instrument
        time.sleep(0.10)
        self.error_check()
