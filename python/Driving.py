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
#     ##########################
#     # Roobert driving module #
#     ##########################
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

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/libs" )

# import the necessary packages
from MultiProcessing import MultiProcessing
import time

class Driving(MultiProcessing):

	__posXFaceKey 			= MultiProcessing.get_next_key() #-1 # -1=no face, 0=max left, 1=max right
	__posYFaceKey 			= MultiProcessing.get_next_key() #-1 # -1=no face, 0=max bottom, 1=max top
	
	_released				= False

	def __init__(self):
		print("driving init")
		super().__init__(prio=20)
		
		
		
		super().StartUpdating()
		
	## multi process properties START ##

	@property
	def posXFace(self):
		return self.GetSharedValue(self.__posXFaceKey)
	@posXFace.setter
	def posXFace(self, value):
		self.SetSharedValue(self.__posXFaceKey, value)

	@property
	def posYFace(self):
		return self.GetSharedValue(self.__posYFaceKey)
	@posYFace.setter
	def posYFace(self, value):
		self.SetSharedValue(self.__posYFaceKey, value)
	
	## multi process properties END ##

	def Update(self):
		return

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down driving")
			super().EndUpdating()

	def __del__(self):
			self.Release()

if __name__ == '__main__':

	testDriving = Driving() 

	while (True):
		time.sleep(0.01)
