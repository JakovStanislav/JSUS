# JSUS -Just a Simple UI for Seismologists

Just a Simple UI for Seismologists (JSUS) is a user interface that helps seismologists quickly inspect 
and visualize seismograph and accelerograph data. At the moment it is possible to read all formats that 
can be read using [ObsPy](https://docs.obspy.org/) package as well as files with the .v1 extension.
In JSUS users can pick P and S earthquake phases and visualize the Fourier amplitude spectrum and spectrogram.

## Installing JSUS

Argos works with Python 3.7 and higher.

First clone repository:

    git clone https://github.com/JakovStanislav/JSUS
    
Then run the setup file:

    python setup.py install
    
Finally, run the main:

    python main.py
    
## Using JSUS
