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

.. code-block:: console

    $ pip install tektronixsg

Usage
=====

Example how to use tektronixsg::

   from tektronixsg import SignalGenerator
   sg = SignalGenerator()
   # Set the voltage amplitude of the first channel to 1V
   sg.channel[0].voltage_amplitude = 1
   # Set the signal type of the first channel to sine
   sg.channel[0].signal_type = "sine"
   # Set the frequency of the first channel to 100 kHz
   sg.channel[0].frequency = 1e5
   # Enable the output of the first channel
   sg.channel[0].output_on = True
