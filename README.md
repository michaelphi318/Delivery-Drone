# Delivery-Drone

This is autonomous medical delivery drone prject from team 8 - Senior Design Drexel 2022 by

Manh Cuong Phi
Tri Pham
Binh Tran
Jordan Lanzoni
Brendan Higgins

Software requirements are listed below by type of connection to the drone.

All drones: Python 3

I use the https://www.anaconda.com/download/:: installer and package manager for python. Note, when you install anaconda, install the Visual Studio option, especially if you have windows. Otherwise you will need to install Visual Studio separately. The zeroconf package (listed below) requires developer tools because it needs to be compiled.

All drones: untangle package (this is used to parse the xml files in the parrot SDK)

pip install untangle
Vision: If you intend to process the camera files, you will need to install opencv and then either ffmpeg
or VLC. I installed ffmpeg using brew for the mac but apt-get on linux should also work. For VLC, you MUST install the actual `VLC <https://www.videolan.org/vlc/index.html`_ program (and not just the library in python) and it needs to be version 3.0.1 or greater.

Wifi connection: zeroconf To install zeroconf software do the following:
pip install zeroconf

git clone https://github.com/amymcgovern/pyparrot
cd pyparrot

pip install pyparrot

pip install untangle
pip install pyparrot
pip install zeroconf


Reference Links:

https://pyparrot.readthedocs.io/en/latest/

https://github.com/N-Bz/bybop

https://github.com/amymcgovern/pyparrot
