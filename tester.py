"""
This module is meant as a testing sandbox for other modules, during implementation.
"""
import controllers
import calculations
import environment as env
import planning
import simulaton
import dynamixel
import periphery

import time
import random
import udpServer as udpServer
import threading
import numpy as np

def forceSending(frequency):
    while True:
        udpServer.send(controller.fA)
        time.sleep(1.0 / frequency)

def initSendingThread():
    udpSendingThread = threading.Thread(target = forceSending, args = (20, ), name = 'udp_sending_thread', daemon = False)
    udpSendingThread.start()
    print("UDP thread is running.")

if __name__ == "__main__":
    controller = controllers.VelocityController(True)
    # udpServer = udpServer.UdpServer('192.168.1.32')
    # initSendingThread()
    time.sleep(3)

    # controller.startForceMode(0)
    # controller.moveLegAsync(0, [0.0, 0.0, -0.35], 'l', 3, 'minJerk')
    # time.sleep(3)
    while True:
        controller.moveLegAsync(0, [0.15, 0.15, -0.35], 'l', 3, 'minJerk')
        time.sleep(3.1)
        # controller.moveLegAsync(0, [0.0, 0.0, -0.35], 'l', 4, 'minJerk')
        # time.sleep(6)
        controller.moveLegAsync(0, [-0.15, 0.15, -0.35], 'l', 3, 'minJerk')
        time.sleep(3.1)
        print(controller.motorDriver.syncReadMotorsPositionsInLegs([0], True))
    #     time.sleep(4)
        # controller.moveLegAsync(0, [0.0, 0.0, -0.35], 'l', 4, 'minJerk')
        # time.sleep(4)
