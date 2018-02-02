# IndoorLocation
To set up the Raspberry Pi:

0) Clone repository
- cd /home/pi/Documents/Python
- git clone https://github.com/GammonDigital/IndoorLocation.git
- git config --global user.name "username"
- git config --global user.email "email"
- git config credential.helper store

1) Install BlueZ
- sudo apt-get update
- sudo apt-get install bluez(bluetooth blueman)
// sudo reboot
// sudo systemctl start bluetooth

2) Install bluepy
- sudo apt-get install python3-pip libglib2.0-dev
- sudo pip3 install bluepy

// 3) Install paho-mqtt
// - sudo pip3 install paho-mqtt

3) Config parameters.csv, run.sh, rc.local, crontab

// 4) Download the python scripts and the beacon register file

// 5) Edit the script
// - Under # Variables, give a name to the Raspberry Pi (this will be used as the scannerId, e.g. "P0DJ") and edit the RSSI threshold.

6) Config to run on boot
- sudo nano /etc/rc.local
- systemctl start bluetooth
- python3 /home/pi/20171219_BLEScanFiltered.py &

// git add scanlog_scannerId.csv
// git push
