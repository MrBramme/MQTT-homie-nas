#!/usr/bin/env python
import time
import homie
import logging
import subprocess
from wakeonlan import wol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------- #
# NAS stuff #
# --------- #
nasHostname = "ip of nas"
nasMacAddress = 'mac address of nas'
nasCheckStatusInterval = 90 #check nas state each 90 seconds
nasWakeGraceInterval = 30 #gracetime when waking up
nasState = 0 #assume it's offline on startup
nasWakeUpGraceTime = 0

def sendWol():
    wol.send_magic_packet(nasMacAddress)


def isHostUp():
    try:
        response = subprocess.check_output(
            ['ping', '-c', '3', '-W', '3', nasHostname],
            stderr=subprocess.STDOUT,  
            universal_newlines=True  
        )
        return 1
    except subprocess.CalledProcessError:
        return 0


def checkHost():
    global nasState
    currentNasState = isHostUp()
    if not currentNasState == nasState:
        nasState = currentNasState
        logger.info("nas state: " + str(nasState))
        if nasState == 1:
            Homie.setNodeProperty(switchNode, "on", "true", True)
        else:
            Homie.setNodeProperty(switchNode, "on", "false", True)

def isUpdateTime(nextStatusCheck):
    return nextStatusCheck < time.time()

def isNasStarting():
    return nasWakeUpGraceTime > time.time()

# ------------- #
# MQTT settings #
# ------------- #

Homie = homie.Homie("mqtt-nas.json")
switchNode = Homie.Node("switch", "switch")

def switchOnHandler(mqttc, obj, msg):
    global nasWakeUpGraceTime
    global nasState
    payload = msg.payload.decode("UTF-8").lower()
    if payload == 'true':
        logger.info("Switch: ON")
        if not isNasStarting():
            logger.debug("Sending WOL package")
            sendWol()
            nasWakeUpGraceTime = time.time() + nasWakeGraceInterval
            logger.debug("new wakeupgrace is: " + str(nasWakeUpGraceTime))
            Homie.setNodeProperty(switchNode, "on", "true", True)
    else:
        logger.info("Switch: OFF")
        #my Nas doesn't have a shutdown so adjust this code if needed. I'm allowing the state to be put offline and letting a next loop of the state check handle this
        nasState = 0
        Homie.setNodeProperty(switchNode, "on", "false", True)


def main():
    Homie.setFirmware("Homie-Nas", "1.0.0")
    Homie.subscribe(switchNode, "on", switchOnHandler)
    Homie.setup()
    nextStatusCheck = time.time()

    while True:
        if isUpdateTime(nextStatusCheck):
            logger.debug("checking for nas")
            checkHost()
            nextStatusCheck += nasCheckStatusInterval
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Quitting.")