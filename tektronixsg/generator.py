import pyvisa as vi
import time

from .channel import Channel

TRIGGER_SOURCE = {"timer": "TIM", "external": "EXT"}


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


class SignalGenerator:
    """Interface for tektronix signal generators.

    Supports the AFG 1022 and the AFG 31052.

    Attributes:
        channels (list): List of all channels.
        connected_device (str): The specific tektronix device which is
                                connected.
    """

    def __init__(self, resource=None):
        rm = vi.ResourceManager()
        if not resource:
            connected_resources = rm.list_resources()
            self.instrument = None
            for resource in connected_resources:
                manufacturer_id = resource.split("::")[1]
                if manufacturer_id == "1689":
                    self.instrument = rm.open_resource(resource)
                    break
            if not self.instrument:
                raise RuntimeError("Could not find any tektronix devices")
        else:
            self.instrument = rm.open_resource(resource)
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
        return self.instrument.query("*IDN?")

    def wait(self):
        """Prevent instrument from executing further commands until
        all pending commands are complete."""
        self.write("*WAI")

    def close(self):
        """Closes the instrument."""
        self.instrument.close()

    def error_check(self):
        if self.connected_device == "AFG31052":
            self.instrument.query("*ESR?")
        error = self.instrument.query("SYSTem:ERRor?")
        error_code, error_message = error.split(",")
        if int(error_code) != 0:
            raise ValueError(error_message)

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
        self.instrument.write_binary_values(
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
        return self.instrument.query_binary_values(
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
        query = self.instrument.query(query_string)
        self.error_check()
        return query

    def write(self, write_string):
        """Write a string to the instrument."""
        self.instrument.write(write_string)
        # Add a delay to prevent too many writes to the instrument
        time.sleep(0.10)
        self.error_check()
