# IndoorLocation
To set up the Raspberry Pi:

1. Clone repository
- cd /home/pi/Documents/Python
- sudo git clone https://github.com/GammonDigital/IndoorLocation.git
- sudo git config --global user.name "username"
- sudo git config --global user.email "email"
- sudo git config credential.helper store
- cd /home/pi/Documents/Python/IndoorLocation
- sudo git clone https://github.com/GammonDigital/IndoorLocationRecords.git
- (later) sudo git add scanlog_0000000...

2. Install BlueZ
- sudo apt-get update
- sudo apt-get install bluez

3. Install Python packages and their dependencies
- sudo apt-get install python3-pip libglib2.0-dev
- sudo pip3 install bluepy
- sudo pip3 install paho-mqtt

4. Fill in and rename parameters.csv download root.cer

5. Make run.sh and scanlogpush.sh executable
- chmod -x run.sh
- chmod -x scanlogpush.sh

6. Config to run on boot
- Raspberry Pi setting: wait for network to boot
- sudo nano /etc/rc.local
- sudo /home/pi/Documents/Python/Indoorlocation/run.sh

7. Config nightly reboot+update and hourly backup of scanlog 
- sudo crontab -e
- 59 3 * * * sudo reboot
- 30 * * * * sudo /home/pi/Documents/Python/Indoorlocation/scanlogpush.sh

8. For gspread
- sudo pip3 install gspread
- sudo pip3 install oauth2client
- sudo pip3 install --upgrade pyasn1-modules
- download drive_client_secret.json
