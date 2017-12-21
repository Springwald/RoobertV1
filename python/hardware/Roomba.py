#!/usr/bin/env python

#      Roobert - home robot project
#      ________            ______             _____ 
#      ___  __ \______________  /_______________  /_
#      __  /_/ /  __ \  __ \_  __ \  _ \_  ___/  __/
#      _  _, _// /_/ / /_/ /  /_/ /  __/  /   / /_  
#      /_/ |_| \____/\____//_.___/\___//_/    \__/
#
#     Project website: http://roobert.springwald.de
#
#     ######################################
#     # Roomba vacuum robot control module #
#     ######################################
#
#     Licensed under MIT License (MIT)
#
#     Copyright (c) 2017 Daniel Springwald | daniel@springwald.de
#
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#     THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.

import os, sys
import subprocess
from _thread import start_new_thread
import pygame
from pygame.locals import *
import time

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/pycreate" )

from create import *

SERIAL_PORT = "/dev/ttyUSB0"

import atexit


class Roomba:

	_released 			=False
	_create				= None
	maxDegPerSecond 	= 30
	maxCmPerSecond		= 5

	def __init__(self):
		print("Roomba init")
		self._create = Create(SERIAL_PORT,SAFE_MODE);
		time.sleep(1);
		
		return
		self.rotate(-90);
		#return
		self.rotate(90);
		return;
		
		self._create.go(cmPerSec=5, degPerSec=0)
		time.sleep(2)
		self._create.stop()
		time.sleep(.2)
		
		self._create.go(cmPerSec=-5, degPerSec=0)
		time.sleep(2)
		self._create.stop()
		time.sleep(.2)
	
	def move(self, deltaCm):
		if (deltaCm > 0):
			self._create.go(cmPerSec=self.maxCmPerSecond, degPerSec=0)
		else:
			self._create.go(cmPerSec=-self.maxCmPerSecond, degPerSec=0)
		time.sleep(abs(deltaCm) / self.maxCmPerSecond)
		self._create.stop()
		time.sleep(.2)

	def rotate(self,deltaDegree):
		correctionFactor = 1 #360 / 490 # // on low speed ( < 20° per second) my roomba makes 490° if we say to him to rotate 360°
		deltaDegree = deltaDegree * correctionFactor
		if (deltaDegree > 0):
			self._create.go(cmPerSec=0, degPerSec=self.maxDegPerSecond)
		else:
			self._create.go(cmPerSec=0, degPerSec=-self.maxDegPerSecond)
		time.sleep(abs(deltaDegree) / self.maxDegPerSecond)
		self._create.stop()
		time.sleep(.2)
		
	def BatteryPercent(self):
		#print("Sensor-data is ok:" + str(self._create.sensorDataIsOK()))
		batteryCharge = self._create.getSensor("BATTERY_CHARGE")
		batteryCapacity = self._create.getSensor("BATTERY_CAPACITY")
		if (batteryCapacity == 0 or batteryCapacity==None):
			batteryLevel = -1
		else:
			batteryLevel = 100 * batteryCharge / batteryCapacity
		if (batteryLevel > 100):
			return 0;
		if (batteryLevel < 0):
			return 0;
		return batteryLevel
	
	def BatteryRaw(self):
		#print("Sensor-data is ok:" + str(self._create.sensorDataIsOK()))
		batteryCharge = self._create.getSensor("BATTERY_CHARGE")
		batteryCapacity = self._create.getSensor("BATTERY_CAPACITY")
		if (batteryCapacity == 0 or batteryCapacity==None):
			batteryLevel = -1
		else:
			batteryLevel = str(batteryCharge) + " / " + str(batteryCapacity)
		return batteryLevel
		
	def ChargingStateI(self):
		return self._create.getSensor("CHARGING_STATE")
		
	def ForceCharging(self):
		self._create.seekDock();
		
	def ChargingStateTitle(self):
		state = self._create.getSensor("CHARGING_STATE")
		return {
		  0:  "not charging",
		  1:  "charging recovery",
		  2:  "charging",
		  3:  "tickle charging",
		  4:  "waiting",
		  5:  "charging error",
		}[state]
		
	def Release(self):
		if (self._released == False):
			print("Roomba releasing")
			self._create.stop()
			self._create.toSafeMode()
			self._create.shutdown()
			
def exit_handler():
	#print ('My application is ending!')
	roomba.Release()

if __name__ == "__main__":
	
	roomba = Roomba()
	
	atexit.register(exit_handler)
	
	#while True:
	for i in range(1, 5):
		os.system('clear') 
		print ("Battery: " + str(int(roomba.BatteryPercent())) + "%")
		print ("Battery: " + str(roomba.BatteryRaw()))
		print ("Charging: " + roomba.ChargingStateTitle())
		
		#print (time.time())
		
		#roomba.rotate(10)
		#roomba.rotate(-10)
		
		time.sleep(1)
		
	roomba.ForceCharging();

