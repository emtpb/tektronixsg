*****
Usage
*****

To use Tektronix Signal Generator Interface in a project::

   from tektronixsg import SignalGenerator
   sg = SignalGenerator()
   # Set the frequency of the first channel to 100 kHz
   sg.channel[0].frequency = 1e5
   # Enable the output of the first channel
   sg.channel[0].output_on = True

