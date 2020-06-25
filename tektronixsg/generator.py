import pyvisa as vi
import usbtmc
import platform

FUNCTIONS = {"sine": "SIN", "square": "SQU", "pulse": "PULS", "ramp": "RAMP",
             "noise": "PRN", "dc": "DC",
             "gauss": "GAUS", "lorentz": "LOR", "expo rise": "ERIS",
             "expo decay": "EDEC", "haversine": "HAV",
             "memory1": "EMEM", "memory2": "EMEM2", "file": "EFIL"}

TRIGGER_SOURCE = {"timer": "TIM", "external": "EXT"}

BURST_MODE = {"triggered": "TRIG", "gated": "GAT"}

PULSE_HOLD = {"width": "WIDT", "duty": "DUTY"}


class SignalGenerator:
    """Interface of the AFG31000 arbitrary signal generator."""

    def __init__(self, resource=None):
        if platform.system() == "Windows":
            rm = vi.ResourceManager()
            if not resource:
                connected_resources = rm.list_resources()
                if len(connected_resources) == 0:
                    raise RuntimeError("No device connected.")
                else:
                    resource = connected_resources[0]
            self._instrument = rm.open_resource(resource)
        elif platform.system() == 'Linux':
            if not resource:
                connected_resources = usbtmc.list_resources()
                if len(connected_resources) == 0:
                    raise RuntimeError("No device connected.")
                else:
                    resource = connected_resources[0]
            self._instrument = usbtmc.Instrument(resource)
        else:
            raise Exception('Unknown platform.system(): ' + platform.system())

        self.channel_1 = Channel(self._instrument, self, "1")
        self.channel_2 = Channel(self._instrument, self, "2")

    def reset(self):
        """Reset the instrument."""
        self._instrument.write("*RST")

    def clear(self):
        """Clear event registers and error queue."""
        self._instrument.write("*CLS")

    def send_trigger(self):
        """Trigger signal generator."""
        self._instrument.write("*TRG")

    @property
    def instrument_info(self):
        """Get instrument information."""
        return self.query_str("*IDN?")

    def write_data_emom(self, data, memory=1):
        """Write data to an edit memory.

        Args:
            data(numpy.ndarray): Data to be written to the editable memory.
                                 Data has to be a list or numpy array
                                 with values ranging from 0 to 16383.
                                 0 corresponds to the minimum
                                 voltage and 16383 to the maximum voltage
                                 of the current set voltage range.
            memory(int): Memory to which should be written (There only exists
                         memory 1 and 2).
        """
        self._instrument.write_binary_values(
            "DATA:DATA EMEM{},".format(memory), data, datatype="h",
            is_big_endian=True)

    def read_data_emom(self, memory=1):
        """Read data form an edit memory.

        Args:
            memory(int): Memory which should be read.
        Returns:
            list: Values ranging from 0 to 16383. 0 corresponds to the minimum voltage and 16383 to the maximum
            voltage of the current set voltage range.
        """
        self._instrument.query_binary_values(
            "DATA:DATA? EMEM{}".format(memory), datatype="h",
            is_big_endian=True)

    @property
    def trigger_source(self):
        value = self.query_str("TRIG:SOUR?")
        for item in TRIGGER_SOURCE.items():
            if item[1] == value:
                return item[0]

    @trigger_source.setter
    def trigger_source(self, value):
        self._instrument.write("TRIG:SOUR {}".format(TRIGGER_SOURCE[value]))

    @property
    def trigger_timer(self):
        return self.query_str("TRIG:TIM?")

    @trigger_timer.setter
    def trigger_timer(self, value):
        self._instrument.write("TRIG:TIM {}".format(value))

    def query_int(self, input_string):
        return int(
            float(self._instrument.query(input_string).replace("\n", "")))

    def query_float(self, input_string):
        return float(self._instrument.query(input_string).replace("\n", ""))

    def query_str(self, input_string):
        return self._instrument.query(input_string).replace("\n", "")

    def query_bool(self, input_string):
        return bool(
            int(self._instrument.query(input_string).replace("\n", "")))


class Channel:
    def __init__(self, instrument, generator, channel_number):
        self._instrument = instrument
        self.generator = generator
        self.channel_number = channel_number

    @property
    def output_on(self):
        return self.generator.query_bool("OUTP{}?".format(self.channel_number))

    @output_on.setter
    def output_on(self, value):
        self._instrument.write(
            "OUTP{} {}".format(self.channel_number, int(value)))

    @property
    def voltage_max(self):
        return self.generator.query_float(
            "SOUR{}:VOLT:HIGH?".format(self.channel_number))

    @voltage_max.setter
    def voltage_max(self, value):
        self._instrument.write(
            "SOUR{}:VOLT:HIGH {}".format(self.channel_number, value))

    @property
    def voltage_min(self):
        return self.generator.query_float(
            "SOUR{}:VOLT:LOW?".format(self.channel_number))

    @voltage_min.setter
    def voltage_min(self, value):
        self._instrument.write(
            "SOUR{}:VOLT:LOW {}".format(self.channel_number, value))

    @property
    def voltage_offset(self):
        return self.generator.query_float(
            "SOUR{}:VOLT:OFFS?".format(self.channel_number))

    @voltage_offset.setter
    def voltage_offset(self, value):
        self._instrument.write(
            "SOUR{}:VOLT:OFFS {}".format(self.channel_number, value))

    @property
    def voltage_amplitude(self):
        return self.generator.query_float(
            "SOUR{}:VOLT?".format(self.channel_number))

    @voltage_amplitude.setter
    def voltage_amplitude(self, value):
        self._instrument.write(
            "SOUR{}:VOLT {}".format(self.channel_number, value))

    @property
    def function(self):
        value = self.generator.query_str(
            "SOUR{}:FUNC?".format(self.channel_number))
        for item in FUNCTIONS.items():
            if item[1] == value:
                return item[0]

    @function.setter
    def function(self, value):
        self._instrument.write(
            "SOUR{}:FUNC {}".format(self.channel_number, FUNCTIONS[value]))

    @property
    def impedance(self):
        return self.generator.query_float(
            "OUTP{}:IMP?".format(self.channel_number))

    @impedance.setter
    def impedance(self, value):
        self._instrument.write(
            "OUTP{}:IMP {}".format(self.channel_number, value))

    @property
    def frequency(self):
        return self.generator.query_float(
            "SOUR{}:FREQ?".format(self.channel_number))

    @frequency.setter
    def frequency(self, value):
        self._instrument.write(
            "SOUR{}:FREQ {}".format(self.channel_number, value))

    @property
    def phase(self):
        return self.generator.query_float(
            "SOUR{}:PHAS?".format(self.channel_number))

    @phase.setter
    def phase(self, value):
        self._instrument.write(
            "SOUR{}:PHAS {}".format(self.channel_number, value))

    @property
    def burst_on(self):
        return self.generator.query_bool(
            "SOUR{}:BURS?".format(self.channel_number))

    @burst_on.setter
    def burst_on(self, value):
        self._instrument.write(
            "SOUR{}:BURS {}".format(self.channel_number, int(value)))

    @property
    def burst_mode(self):
        value = self.generator.query_str(
            "SOUR{}:BURS:MODE?".format(self.channel_number))
        for item in BURST_MODE.items():
            if item[1] == value:
                return item[0]

    @burst_mode.setter
    def burst_mode(self, value):
        self._instrument.write(
            "SOUR{}:BURS:MODE {}".format(self.channel_number,
                                         BURST_MODE[value]))

    @property
    def burst_cycles(self):
        return self.generator.query_int(
            "SOUR{}:BURS:NCYC?".format(self.channel_number))

    @burst_cycles.setter
    def burst_cycles(self, value):
        self._instrument.write(
            "SOUR{}:BURS:NCYC {}".format(self.channel_number, value))

    @property
    def burst_delay(self):
        return self.generator.query_float(
            "SOUR{}:BURS:TDEL?".format(self.channel_number))

    @burst_delay.setter
    def burst_delay(self, value):
        self._instrument.write(
            "SOUR{}:BURS:TDEL {}".format(self.channel_number, value))

    @property
    def pulse_width(self):
        return self.generator.query_float(
            "SOUR{}:PULS:WIDT?".format(self.channel_number))

    @pulse_width.setter
    def pulse_width(self, value):
        self._instrument.write(
            "SOUR{}:PULS:WIDT {}".format(self.channel_number, value))

    @property
    def pulse_duty(self):
        return self.generator.query_float(
            "SOUR{}:PULS:DCYC?".format(self.channel_number))

    @pulse_duty.setter
    def pulse_duty(self, value):
        self._instrument.write(
            "SOUR{}:PULS:DCYC {}".format(self.channel_number, value))

    @property
    def pulse_delay(self):
        return self.generator.query_float(
            "SOUR{}:PULS:DEL?".format(self.channel_number))

    @pulse_delay.setter
    def pulse_delay(self, value):
        self._instrument.write(
            "SOUR{}:PULS:DEL {}".format(self.channel_number, value))

    @property
    def pulse_hold(self):
        value = self.generator.query_str(
            "SOUR{}:PULS:HOLD?".format(self.channel_number))
        for item in PULSE_HOLD.items():
            if item[1] == value:
                return item[0]

    @pulse_hold.setter
    def pulse_hold(self, value):
        self._instrument.write(
            "SOUR{}:PULS:HOLD {}".format(self.channel_number, PULSE_HOLD[value]))

    @property
    def pulse_period(self):
        return self.generator.query_float(
            "SOUR{}:PULS:PER?".format(self.channel_number))

    @pulse_period.setter
    def pulse_period(self, value):
        self._instrument.write(
            "SOUR{}:PULS:PER {}".format(self.channel_number, value))

    @property
    def pulse_leading_transition(self):
        return self.generator.query_float(
            "SOUR{}:PULS:TRAN:LEAD?".format(self.channel_number))

    @pulse_leading_transition.setter
    def pulse_leading_transition(self, value):
        self._instrument.write(
            "SOUR{}:PULS:TRAN:LEAD {}".format(self.channel_number, value))

    @property
    def pulse_trailing_transition(self):
        return self.generator.query_float(
            "SOUR{}:PULS:TRAN:TRA?".format(self.channel_number))

    @pulse_leading_transition.setter
    def pulse_trailing_transition(self, value):
        self._instrument.write(
            "SOUR{}:PULS:TRAN:TRA {}".format(self.channel_number, value))
