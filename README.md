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
- sudo apt-get install bluez

2) Install Python packages and their dependencies
- sudo apt-get install python3-pip libglib2.0-dev
- sudo pip3 install bluepy
- sudo pip3 install paho-mqtt

3) Fill in parameters.csv download root.cer

4) Make run.sh and scanlogpush.sh executable
- chmod -x run.sh
- chmod -x scanlogpush.sh

5) Config to run on boot
- Raspberry Pi setting: wait for network to boot
- sudo nano /etc/rc.local
- sudo /home/pi/Documents/Python/Indoorlocation/run.sh

6) Config nightly reboot+update and hourly backup of scanlog 
- sudo crontab -e
- 59 3 * * * sudo reboot
- 30 * * * * sudo /home/pi/Documents/Python/Indoorlocation/scanlogpush.sh
