"""Tests for `tektronixsg` package."""
import pytest
import numpy as np
import time
from tektronixsg import SignalGenerator, generator, channel

test_device = SignalGenerator()


@pytest.fixture
def default_device():
    test_device.reset()
    yield test_device
    time.sleep(0.1)


def test_send_trigger(default_device):
    device = default_device
    device.send_trigger()


def test_instrument_info(default_device):
    device = default_device
    device.instrument_info


def test_wait(default_device):
    device = default_device
    device.wait()


def test_write_read_emom(default_device):
    device = default_device
    if device.connected_device == "AFG31052":
        data_1 = [0, 5000, 14000]
        time.sleep(0.5)
        device.write_data_emom(data_1, memory=1)
        assert device.read_data_emom(memory=1) == data_1
        data_2 = [0, 1000, 2000, 5000, 10000]
        device.write_data_emom(data_2, memory=2)
        assert device.read_data_emom(memory=2) == data_2
        assert device.read_data_emom(memory=1) != data_2
    elif device.connected_device == "AFG 1022":
        data = [0, 1000, 2000, 3000, 4000]
        device.write_data_emom(data)
        assert data == device.read_data_emom()


def test_trigger_source(default_device):
    device = default_device
    if device.connected_device == "AFG31052":
        for trigger_source in generator.TRIGGER_SOURCE.keys():
            device.trigger_source = trigger_source
            assert device.trigger_source == trigger_source


@pytest.mark.parametrize("trigger_time", [600e-6, 20, 100])
def test_trigger_timer(default_device, trigger_time):
    device = default_device
    if device.connected_device == "AFG31052":
        device.trigger_timer = trigger_time
        assert device.trigger_timer == trigger_time


def test_output_on(default_device):
    device = default_device
    for device_channel in device.channels:
        assert device_channel.output_on is False
        device_channel.output_on = True
        assert device_channel.output_on is True


@pytest.mark.parametrize("voltage_max", [2, 0.5, 2e-3])
def test_voltage_max(default_device, voltage_max):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.voltage_max = voltage_max
            assert device_channel.voltage_max == voltage_max


@pytest.mark.parametrize("voltage_min", [2, 0.5, 2e-3])
def test_voltage_min(default_device, voltage_min):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.voltage_min = voltage_min
            assert device_channel.voltage_min == voltage_min


@pytest.mark.parametrize("voltage_offset", [2, 0.5, 2e-3])
def test_voltage_offset(default_device, voltage_offset):
    device = default_device
    for device_channel in device.channels:
        device_channel.voltage_offset = voltage_offset
        assert device_channel.voltage_offset == voltage_offset


@pytest.mark.parametrize("voltage_amplitude", [2, 0.5, 2e-3])
def test_voltage_amplitude(default_device, voltage_amplitude):
    device = default_device
    for device_channel in device.channels:
        device_channel.voltage_amplitude = voltage_amplitude
        assert device_channel.voltage_amplitude == voltage_amplitude


def test_signal_type(default_device):
    device = default_device
    for device_channel in device.channels:
        if device.connected_device == "AFG1022":
            for signal_type in channel.SIGNAL_TYPES_AFG1022.keys():
                device_channel.signal_type = signal_type
        elif device.connected_device == "AFG31052":
            for signal_type in channel.SIGNAL_TYPES_AFG31000.keys():
                device_channel.signal_type = signal_type


@pytest.mark.parametrize("impedance", [30, 50, 500])
def test_impedance(default_device, impedance):
    device = default_device
    for device_channel in device.channels:
        device_channel.impedance = impedance
        assert device_channel.impedance == impedance


@pytest.mark.parametrize("frequency", [10, 1000, 1e6])
def test_frequency(default_device, frequency):
    device = default_device
    for device_channel in device.channels:
        device_channel.frequency = frequency
        assert device_channel.frequency == frequency


@pytest.mark.parametrize("phase", [np.pi, np.pi/2, np.pi/4])
def test_phase(default_device, phase):
    device = default_device
    for device_channel in device.channels:
        device_channel.phase = phase
        assert np.isclose(device_channel.phase, phase)


def test_burst_on(default_device):
    device = default_device
    for device_channel in device.channels:
        if device.connected_device == "AFG1022" and \
                device_channel.channel_number == "2":
            continue
        device_channel.burst_on = True
        assert device_channel.burst_on is True


def test_burst_mode(default_device):
    device = default_device
    for device_channel in device.channels:
        if device.connected_device == "AFG1022" and \
                device_channel.channel_number == "2":
            continue
        for burst_mode in channel.BURST_MODE.keys():
            device_channel.burst_mode = burst_mode
            assert device_channel.burst_mode == burst_mode


@pytest.mark.parametrize("burst_cycles", [1, 10, 1000])
def test_burst_cycles(default_device, burst_cycles):
    device = default_device
    for device_channel in device.channels:
        if device.connected_device == "AFG1022" and \
                device_channel.channel_number == "2":
            continue
        device_channel.burst_cycles = burst_cycles
        assert device_channel.burst_cycles == burst_cycles


@pytest.mark.parametrize("burst_delay", [1, 1e-5, 1e-3])
def test_burst_delay(default_device, burst_delay):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.burst_delay = burst_delay
            assert device_channel.burst_delay == burst_delay


@pytest.mark.parametrize("pulse_width", [7e-4, 1e-5, 1e-3])
def test_pulse_width(default_device, pulse_width):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.frequency = 10
            device_channel.pulse_width = pulse_width
            assert device_channel.pulse_width == pulse_width


@pytest.mark.parametrize("pulse_duty", [0.1, 0.5, 0.4])
def test_pulse_duty(default_device, pulse_duty):
    device = default_device
    for device_channel in device.channels:
        device_channel.frequency = 10
        device_channel.pulse_duty = pulse_duty
        assert device_channel.pulse_duty == pulse_duty


@pytest.mark.parametrize("pulse_delay", [0.01, 6e-5, 0.005])
def test_pulse_delay(default_device, pulse_delay):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.frequency = 10
            device_channel.pulse_delay = pulse_delay
            assert device_channel.pulse_delay == pulse_delay


def test_pulse_hold(default_device):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            for pulse_hold in channel.PULSE_HOLD.keys():
                device_channel.pulse_hold = pulse_hold
                assert device_channel.pulse_hold == pulse_hold


@pytest.mark.parametrize("pulse_period", [0.01, 2, 0.4])
def test_pulse_period(default_device, pulse_period):
    device = default_device
    for device_channel in device.channels:
        device_channel.pulse_period = pulse_period
        assert device_channel.pulse_period == pulse_period


@pytest.mark.parametrize("pulse_leading_transition", [2e-7, 5e-8, 8e-9])
def test_leading_transition(default_device, pulse_leading_transition):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.frequency = 10
            device_channel.pulse_leading_transition = pulse_leading_transition
            assert device_channel.pulse_leading_transition == pulse_leading_transition


@pytest.mark.parametrize("pulse_trailing_transition", [2e-7, 5e-8, 8e-9])
def test_trailing_transition(default_device, pulse_trailing_transition):
    device = default_device
    if device.connected_device == "AFG31052":
        for device_channel in device.channels:
            device_channel.frequency = 10
            device_channel.pulse_trailing_transition = pulse_trailing_transition
            assert device_channel.pulse_trailing_transition == pulse_trailing_transition


def test_set_arbitrary_signal(default_device):
    device = default_device
    voltage_vector = np.array([1, 2, 3, 4, 2, 1, 1.5, 1.6, 1.7])
    voltage_range = 3
    voltage_offset = 2.5

    device.channels[0].set_arbitrary_signal(voltage_vector=voltage_vector)
    assert device.channels[0].voltage_amplitude == voltage_range
    assert device.channels[0].voltage_offset == voltage_offset
