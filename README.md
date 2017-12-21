# IndoorLocation
To set up the Raspberry Pi:

1) Install BlueZ
- sudo apt-get install bluetooth bluez blueman
- sudo reboot
- sudo systemctl start bluetooth

2) Install bluepy
- sudo apt-get install python-pip libglib2.0-dev
- sudo pip install bluepy

3) Install paho-mqtt
- sudo pip3 install paho-mqtt

4) Download the python scripts and the beacon register file

5) Edit the script
- Under # Variables, give a name to the Raspberry Pi (this will be used as the scannerId, e.g. "P0DJ") and edit the RSSI threshold.

6) Config to run on boot
- /etc/rc.local
