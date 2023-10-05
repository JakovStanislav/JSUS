# JSUS-Just a Simple UI for Seismologists

**J**ust a **S**imple **U**I for **S**eismologists (JSUS) is a user interface that helps seismologists quickly inspect and visualize seismogram and accelerogram data. At the moment it is possible to read all formats that can be read using [ObsPy](https://docs.obspy.org/) package as well as files with the .v1 extension. In JSUS users can pick **P** and **S** earthquake phases and visualize the Fourier amplitude spectrum (FAS) and spectrogram.

## Installing JSUS

JSUS works with Python 3.7 and higher.

To install JSUS, first, you need to download the *Installing/Env_setup.bat* file from the repository by opening the terminal and typing:

    curl -o Env_setup.bat https://raw.githubusercontent.com/JakovStanislav/JSUS/main/Installing/Env_setup.bat --ssl-no-revoke

After downloading the *Env_setup.bat* file run it. *Env_setup.bat* should, in the folder where the *Env_setup.bat* file is started, automatically create virtual environment and clone the git repository. All required packages will also be installed inside the new environment and the *setup.py* file will be installed.  
After the *Env_setup.bat* file is finished run the *Run_JSUS.bat* file, which should start JSUS.

## Using JSUS
The JSUS main window consists of a table (left side) that contains information on all loaded records. On the right side of the main window, there are three figures, one for each of the record´s components. Above the figures, there is a navigation toolbar that is used for navigating through the plotted data set. Also, on the right of the navigation toolbar, there are two fields that show the selected times of the **P** and **S** phases.

<p align="center">
    <img src="Screenshots/Main_window.png">
</p>

### Loading data
Loading records into JSUS works by going to `Files → Read batch`, this will open a window where a user needs to select a folder from which he wants to read records. JSUS will automatically find all suitable records inside that folder and inside all subfolders of the selected folder.

<p align="center">
    <img src="Screenshots/Reading_files.png">
</p>

### Plotting data
To plot records press the right mouse button over the row of the record you want to draw and then click `Draw record`.
<p align="center">
    <img src="Screenshots/Draw_record.png">
</p>

To plot the FAS of the selected record you need to click `Calculate FAS`.
<p align="center">
    <img src="Screenshots/Calculate_FAS.png">
</p>

### FAS window
In the FAS window, the Fourier amplitude spectrum of existent channels will be displayed.
<p align="center">
    <img src="Screenshots/FAS_window.png">
</p>

Here it is possible to change the scale of both axes (**X** and **Y**) by pressing the right mouse button over the figures. Also, it is possible to turn on/off a grid by pressing `Toggle grid`.
<p align="center">
    <img src="Screenshots/FAS_window_scale.png">
</p>

Finally from the FAS window, it is possible to show the spectrogram by pressing `Show spectrogram`.

#### Spectrogram window
In the spectrogram window, the user can select which channels spectrogram will be drawn by selecting a channel and pressing `Show spectrogram`.
<p align="center">
    <img src="Screenshots/Spectrogram_window.png">
</p>

It is possible to change the colormap of the spectrogram by right-clicking over the spectrogram figure and pressing `Change colormap`. This will open a new window where it is possible to select colormap. Choosing a colormap is done by first selecting a [category](https://matplotlib.org/stable/users/explain/colors/colormaps.html) from which the colormap will be selected. When the category is selected, an image with all available colormaps from that category will appear. Now from the drop-down menu user can select the colormap that he wants. 

<p align="center">
    <img src="Screenshots/Spectrogram_window_colormaps.png">
</p>

### Phases picking
In JSUS it is possible to pick **P** and **S** earthquake phases. To pick the **P** phase user needs to press `Ctrl+D` and to pick the **S** phase user needs to press `Ctrl+S` while the mouse cursor is over the appropriate position. It is also possible to delete picked phases by hovering the mouse cursor over the phase (line) you want to delete and pressing the `Middle mouse button`. Phase picking can be done on the main window and on the spectrogram window. The phase picked on one window will automatically be shown in another window. 

