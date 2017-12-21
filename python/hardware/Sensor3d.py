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
#     #######################################
#     # Roobert 3D ultrasonic sensor module #
#     #######################################
#
#     Licensed under MIT License (MIT)
#
#     Copyright (c) 2016 Daniel Springwald | daniel@springwald.de
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

from MultiProcessing import MultiProcessing
from RelaisI2C import RelaisI2C
from I2cIoExpanderPcf8574 import I2cIoExpanderPcf8574
from array import array
import Adafruit_PCA9685
import RPi.GPIO as GPIO

class sensor3D(MultiProcessing):
	
	_pwm				= None
	_released 			= False
	
	_xAxis				= 0
	_yAxis				= 1
	
	_resolutionX 		= 3
	_resolutionY 		= 2
	
	_power_relais		= None		# the relais to activate the servo voltage 
	_relais_bit			= -1		# the bit to set for the power relais (0-7)
	
	_sensorport 		= 11 #=pin17
	
	_lastUpdateTime		= time.time()
	
	fast				= False
	
	_actualSpeedDelay 	= 0.01
	_measures_per_point	= 3

	#_servosMinMax 		= 	[[220,500],[300,500]] # wide range
	_servosMinMax 		= 	[[230,440],[320,520]] # small range
	
	__keyActualServoX 	= MultiProcessing.get_next_key()
	__keyActualServoY 	= MultiProcessing.get_next_key()
	__key_run_x 		= MultiProcessing.get_next_key()
	__key_run_Y		 	= MultiProcessing.get_next_key()
	__key_direction_x	= MultiProcessing.get_next_key()
	__key_direction_y	= MultiProcessing.get_next_key()
	__key_depth_map		= MultiProcessing.get_next_key()
	__key_active		= MultiProcessing.get_next_key()
	
	def __init__(self, i2cAdress, busnum, power_relais, relais_bit):
		# Uncomment to enable debug output.
		#import logging
		#logging.basicConfig(level=logging.DEBUG)
		
		super().__init__(prio=20)

		# Initialise the PCA9685 using the default address (0x40).
		#self._pwm = Adafruit_PCA9685.PCA9685()
		# Alternatively specify a different address and/or bus:
		self._pwm = Adafruit_PCA9685.PCA9685(address=i2cAdress, busnum=busnum)
		
		# Set frequency to 60hz, good for servos.
		self._pwm.set_pwm_freq(60)
		
		
		
		self.actualServoX = 0
		self.actualServoY = 0
		
		map = []
		for x in range(0, self._resolutionX+1):
			for y in range(0, self._resolutionY+1):
				map.append(100)
		self._depth_map = map

		y = 0
		self._run_x = 0
		self._run_y = 0
		self._direction_x = 1
		self._direction_y = 1

		self._power_relais = power_relais
		self._relais_bit = relais_bit
		
		# reset servos
		self.home()
		
		self.active = False
		
		# init GPIO for sensor
		GPIO.setmode(GPIO.BOARD)
			
		super().StartUpdating()

	## multi process properties START ##
	
	@property
	def active(self):
		return self.GetSharedValue(self.__key_active)
	@active.setter
	def active(self, value):
		if (value == True):
			self.power_on()
		else :
			self.power_off()
		self.SetSharedValue(self.__key_active, value)

	@property
	def actualServoX(self):
		return self.GetSharedValue(self.__keyActualServoX)
	@actualServoX.setter
	def actualServoX(self, value):
		self.SetSharedValue(self.__keyActualServoX, value)

	@property
	def actualServoY(self):
		return self.GetSharedValue(self.__keyActualServoY)
	@actualServoY.setter
	def actualServoY(self, value):
		self.SetSharedValue(self.__keyActualServoY, value)

	@property
	def _run_x(self):
		return self.GetSharedValue(self.__key_run_x)
	@_run_x.setter
	def _run_x(self, value):
		self.SetSharedValue(self.__key_run_x, value)

	@property
	def _run_y(self):
		return self.GetSharedValue(self.__key_run_Y)
	@_run_y.setter
	def _run_y(self, value):
		self.SetSharedValue(self.__key_run_Y, value)

	@property
	def _direction_x(self):
		return self.GetSharedValue(self.__key_direction_x)
	@_direction_x.setter
	def _direction_x(self, value):
		self.SetSharedValue(self.__key_direction_x, value)

	@property
	def _direction_y(self):
		return self.GetSharedValue(self.__key_direction_y)
	@_direction_y.setter
	def _direction_y(self, value):
		self.SetSharedValue(self.__key_direction_y, value)

	@property
	def _depth_map(self):
		return self.GetSharedValue(self.__key_depth_map)
	@_depth_map.setter
	def _depth_map(self, value):
		self.SetSharedValue(self.__key_depth_map, value)

	## multi process properties END ##

	@property
	def nearest(self):
		map = self._depth_map
		near = 1000
		for i in range(0, len(map)):
			if (near > map[i]):
				near = map[i]
		return near

	@property
	def x_weight(self):
		map = self._depth_map
		#elf._depth_map[x + (y * self._resolutionX)]
		x = 0
		left = 0
		right = 0
		measure_max = 100 # only measure till this depth
		maximum = 1
		for i in range(0, len(map)):
			if (map[i] > maximum):
				maximum = map[i]
		maximum = min(maximum, measure_max)
		for i in range(0, len(map)):
			if (x < self._resolutionX / 2):
				left = left + (maximum - min(measure_max,map[i]))
			else:
				right = right + (maximum - min(measure_max,map[i]))
			x = x + 1
			if (x >= self._resolutionX):
				x = 0
		
		both = max(1,left + right)
		#print (str(left) + " :: " + str(right))
		value = 0.5 - 0.5 * left / both + 0.5 * right / both
		#print(value)
		return value

	def Update(self):
		if (super().updating_ended == True):
			return
			
		if (self.active == False):
			time.sleep(1)
			return

		self._run_x = self._run_x + self._direction_x
		
		self.moveToTarget(self._run_x * 100 / (self._resolutionX-1),self._run_y  * 100 / (self._resolutionY-1))
		self.measure(self._run_x,self._run_y)
		
		if (int(self._run_x)==0 or int(self._run_x)==self._resolutionX-1):
			self._direction_x = -self._direction_x
			
			self._run_y = self._run_y + self._direction_y
			self.moveToTarget(self._run_x * 100 / (self._resolutionX-1),self._run_y  * 100 / (self._resolutionY-1))
			self.measure(self._run_x,self._run_y)
			
			if (int(self._run_y)==0 or int(self._run_y)==self._resolutionY-1):
				self._direction_y = -self._direction_y
					
	def power_off(self):
		self._power_relais.SetBit(self._relais_bit, 1)
		
	def power_on(self):
		self._power_relais.SetBit(self._relais_bit, 0)
				
	def measure(self, x, y):
		distance = 1000
		for i in range(0,self._measures_per_point):
				
			GPIO.setup(self._sensorport, GPIO.OUT)

			#cleanup output
			GPIO.output(self._sensorport, 0)

			time.sleep(0.002)

			#send signal
			GPIO.output(self._sensorport, 1)

			time.sleep(0.005)
			max_wait = time.time()+1

			GPIO.output(self._sensorport, 0)

			GPIO.setup(self._sensorport, GPIO.IN)

			start = False
			
			while GPIO.input(self._sensorport)==0 and time.time() < max_wait:
				starttime=time.time()
				start = True

			if (start == True):
				end = False
				while GPIO.input(self._sensorport)==1 and time.time() < max_wait:
					endtime=time.time()
					end = True
				
				if (end == True and time.time() < max_wait):
					duration=endtime-starttime
					value=duration*34000/2
					if (value < distance):
						distance = value

		if (distance < 1000):
			self._set_depth(self._resolutionX-x,y, distance)
		#print (str(distance) + " > " + str(self._get_depth(x,y)))

	def moveToTarget(self, targetX, targetY):
		if (self.fast==True):
			self.setServo(self._xAxis, targetX)
			self.setServo(self._yAxis, targetY)
			time.sleep(0.01)
			return
		
		actX = self.actualServoX
		actY = self.actualServoY
		while (int(actX) != int(targetX) or int(actY) != int(targetY)):
			if (actX < targetX):
				actX=actX+1
			if (actX > targetX):
				actX=actX-1
			if (actY < targetY):
				actY=actY+1
			if (actY > targetY):
				actY=actY-1
			self.setServo(self._xAxis, actX)
			self.setServo(self._yAxis, actY)
			time.sleep(0.006)
		self.actualServoX = actX
		self.actualServoY = actY

	def setServo(self, port, value):
		# values 0 to 100
		value = min(100,max(1,value))
		#inverse = self._inverseServo[port]
		minV = self._servosMinMax[port][0]
		maxV = self._servosMinMax[port][1]
		servo_space =  maxV-minV
		#if (inverse==True):
		#	value = 100-value
		self._pwm.set_pwm(port, 0, minV + int(value * servo_space / 100))
		
	def home(self):
		print("home 3d sensor" )
		for i in range(0,1):
			self.setServo(i,50)
	
	def print_measure(self):
	# show the depth table as ascii
		os.system('clear') 
		chars = ['.',':','-','=','+','*','#','%','@']
		max_depth = 100 # in cm
		for y in range(self._resolutionY-1,-1,-1):
			#sys.stdout.write(str(y) + ">")
			for x in range(0,self._resolutionX):
				depth = self._get_depth(x,y)
				char_no = int(len(chars)-1 - (len(chars) * depth / max_depth))
				if (char_no > len(chars)-1):
					char_no = len(chars-1)
				if (char_no < 0):
					char_no = 0
				sys.stdout.write(chars[char_no])
				#sys.stdout.write(str(x) + ":" + str(y)+  " ")
				#sys.stdout.write(str(self._get_depth(x,y)))
			print("")

	def turnOff(self):
		print("turning off 3d sensor")
		for i in range(0,1):
			self._pwm.set_pwm(i, 0, 0)
		self.power_off()

	def _get_depth(self, x, y):
		# Get depth with two coordinates.
		return self._depth_map[x + (y * self._resolutionX)]

	def _set_depth(self, x, y, value):
		# Set depth with two coordinates.
		map = self._depth_map;
		map[x + (y * self._resolutionX)] = value
		self._depth_map = map

	def Release(self):
		self.active = False
		if (self._released == False):
			print("releasing 3d sensor")
			self._released = True
			self.turnOff()
			super().EndUpdating()
			time.sleep(1)

	def __del__(self):
		self.Release()

if __name__ == "__main__":
	
	relais = RelaisI2C(I2cIoExpanderPcf8574(address=0x39, useAsInputs=False))
	
	sens3d = sensor3D(i2cAdress=0x46, busnum=1, power_relais = relais, relais_bit=6)
		
	ended = False
	
	#sens3d.setServo(sens3d._xAxis,50)
	#sens3d.setServo(sens3d._yAxis,50)
	#right.portDemo(right._arm1)
	
	#for i in range(1,3):
		#right.portDemo(right._arm1)
		#left.portDemo(left._arm1)
		#left.portDemo(left._finger4)
		#right.portDemo(right._finger5)
		#handArm.handDemo()
		
	sens3d.active = True
	
	while True:
	#for i in range(1,10):
		sens3d.print_measure()
		print(str(sens3d.nearest) + " / " + str(sens3d.x_weight))
		time.sleep(1)
		
	
	#while ended == False:
	#	print ("")

					
	sens3d.Release()
	#left.Release()
