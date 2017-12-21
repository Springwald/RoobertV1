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
#     #########################
#     # relais control module #
#     #########################
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

import time

from I2cIoExpanderPcf8574 import I2cIoExpanderPcf8574


class RelaisI2C:
	
	_i2cIoExpanderPcf8574   	= None      # the I2cIoExpanderPcf8574 to control the relais
	

	def __init__(self, i2cIoExpanderPcf8574=None):
		self._i2cIoExpanderPcf8574=i2cIoExpanderPcf8574
		self._i2cIoExpanderPcf8574.setByte(255) # all relais off

	def SetBit(self, bit, value):
		# 1 = open relais, 0 = close relais
		self._i2cIoExpanderPcf8574.setBit(bit,value)

	def Release(self):
		self._i2cIoExpanderPcf8574.setByte(255)# all relais off

if __name__ == "__main__":
	i2c = I2cIoExpanderPcf8574(0x39)

	relais = RelaisI2C(i2c)

	for i in range(1, 2):
		print("on")
		for a in range(0, 8):
			relais.SetBit(a,0);
			time.sleep(0.05);
		print("off")
		for b in range(0, 8):
			relais.SetBit(b,1);
			time.sleep(0.05);
		
	relais.SetBit(7,0);
	time.sleep(1);
		
	print("release")
	relais.Release()

