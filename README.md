# MQTT-homie-nas
MQTT script using the homie convention to controll a NAS device through openhab.
This script is designed to work on a raspberry pi on the local network.

Based on [homie-python](https://github.com/jalmeroth/homie-python) 

# Install
###step 1: install packages
```
sudo pip install wakeonlan
sudo pip install homie
```
Note: to check the state of the nas this script will use the ping command. if you don't want to run this script as sudo (and you shouldn't), run this to allow ping to work without sudo:
```
sudo apt-get install --reinstall iputils-ping
```
###step 2: adjust the settings in the mqtt-nas.json file to your own situation
###setp 3: Add some Nas settings in the mqtt-nas.py file
```
nasHostname = "ip of nas"
nasMacAddress = 'mac address of nas'
nasCheckStatusInterval = 90 #check nas state each 90 seconds
nasWakeGraceInterval = 30 #gracetime when waking up
```
###step 4: run the script to start the mqtt homie magic 
```
python mqtt-nas.py
```
note: this script needs to be running the entire time! I advise using the screen package to do this

###step 5: setup the item in openhab
```
Switch Nas { mqtt=">[mqttbroker:home/room/nas/switch/on/set:command:OFF:false],>[mqttbroker:home/room/nas/switch/on/set:command:ON:true],<[mqttbroker:home/room/nas/switch/on:state:MAP(onoff.map)]", autoupdate="false"}
```
###step 6: setup the onoff mapping in openhab (in the transform folder)
create a file named onoff.map and insert this into it
```
false=OFF
true=ON
```
##Done!