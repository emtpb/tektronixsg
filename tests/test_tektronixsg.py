"""Tests for `tektronixsg` package."""
import pytest

from tektronixsg import SignalGenerator, list_connected_devices
device = SignalGenerator()

def test_connecting_to_resource():
    SignalGenerator()


def test_list_devices():
    assert len(list_connected_devices() == 1)


def test_reset():
    device.channels[0].voltage_max = 3
    device.reset()
    assert device.channels[0].voltage_max == 0.5


def test_send_trigger():
    device.send_trigger()
    device.reset()


def test_instrument_info():
    device.instrument_info


def test_wait():
    device.wait()
    device.reset()


def test_write_read_emom_31000():
    data_1 = [0, 5000, 14000]
    device.write_data_emom(data_1, memory=1)
    assert device.read_data_emom(memory=1) == data_1
    data_2 = [0, 1000, 2000, 5000, 10000]
    device.write_data_emom(data_2, memory=2)
    assert device.read_data_emom(memory=2) == data_2
    assert device.read_data_emom(memory=1) != data_2


def test_write_read_emom_1022():
    data = [0, 5000]
    device.write_data_emom()