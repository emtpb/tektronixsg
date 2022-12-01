*****
Usage
*****

To use Tektronix Signal Generator Interface in a project::

   from tektronixsg import SignalGenerator
   sg = SignalGenerator()
   # Set the frequency of the first channel to 100 kHz
   sg.channels[0].frequency = 1e5
   # Enable the output of the first channel
   sg.channels[0].output_on = True

