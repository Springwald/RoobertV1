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
#     # Roobert 3D power management module #
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

from __future__ import division
import time, os, sys

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../libs" )

from RelaisI2C import RelaisI2C
from Roomba import Roomba

class PowerManagement():

	_roomba				= None
	_released 			= False

	def __init__(self, roomba):
		self._roomba = roomba
		return

	@property
	def battery_power_in_percent(self):
		if (self._roomba == None):
			return 80
		else:
			return self._roomba.BatteryPercent()

	def power_off(self):
		self._power_relais.SetBit(self._relais_bit, 1)

	def power_on(self):
		self._power_relais.SetBit(self._relais_bit, 0)

	def Release(self):
		if (self._released == False):
			print("releasing power management")

			self._released = True

	def __del__(self):
		self.Release()

if __name__ == "__main__":
	
	#power = RelaisI2C(I2cIoExpanderPcf8574(address=0x39, useAsInputs=False))
	
	roomba = None #Roomba()
	power = PowerManagement(roomba)

	for i in range(1,3):
		time.sleep(1)

	
	power.Release()
	if (roomba != None):
		roomba.Release()

