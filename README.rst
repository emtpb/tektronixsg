************************************
Tektronix Signal Generator Interface
************************************

Interface for Tektronix signal generators.


Features
========

* Support basic functions for model AFG31052
* Support basic functions for model AFG1022


Installation
============

To install the Tektronix Signal Generator Interface, run this command in your terminal::

   $ pip install tektronixsg

Note that usage in Windows will require a driver, for example the `IO Libraries Suite`_ by Keysight.


Usage
=====

Example how to use tektronixsg::

   from tektronixsg import SignalGenerator
   sg = SignalGenerator()
   # Set the voltage amplitude of the first channel to 1V
   sg.channels[0].voltage_amplitude = 1
   # Set the signal type of the first channel to sine
   sg.channels[0].signal_type = "sine"
   # Set the frequency of the first channel to 100 kHz
   sg.channels[0].frequency = 1e5
   # Enable the output of the first channel
   sg.channels[0].output_on = True


.. _IO Libraries Suite: https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html
