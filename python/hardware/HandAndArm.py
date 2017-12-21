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
#     #####################################
#     # Roobert hand and arm servo module #
#     #####################################
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
import time, sys, os

import atexit

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../libs" )

from MultiProcessing import *
from RelaisI2C import RelaisI2C
from I2cIoExpanderPcf8574 import I2cIoExpanderPcf8574

from array import array
import Adafruit_PCA9685

from SharedInts import SharedInts
from SharedFloats import SharedFloats

class HandAndArm(MultiProcessing):
	
	_pwm		= None
	_released 	= False
	
	_arm1		= 0
	_arm2		= 1
	_arm3		= 3
	
	_finger1	= 4
	_finger2	= 5
	_finger3	= 6
	_finger4	= 7
	_finger5	= 8
	
	_lastUpdateTime	= time.time()
	
	_actualSpeedDelay = 0.01
	_maxStepsPerSecond = 90
	
	_handArmServosMinMax = None
	_handArmHomeValues = None
	
	_name 		= "undefined"
	
	__targets 					= SharedInts(max_length=9)
	__values					= SharedFloats(max_length=9)
	
	__shared_ints__				= None
	__targets_reached_int__		= 0
		
	__key_last_servo_set_time	= MultiProcessing.get_next_key()
	__key_power					= MultiProcessing.get_next_key()

	#									arm1	arm2				arm3	finger1	  finger2	finger3		finger4	finger5
	_rightHandArmServosMinMax = 	[[640,100],[230,640],[0,0,0],[150,600],[440,320],[450,320],[250,350],[200,405],[250,430]]
	
	_rightHandArmHomeValues = 		[	0,			15,		0,		60,			100,	100,		100,	100,	100]
	
	#									arm1	arm2				arm3	finger1	  finger2	finger3		finger4	finger5
	_leftHandArmServosMinMax = 		[[100,600],[550,640],[0,0,0],[150,600],[320,390],[300,400],[300,350],[320,405],[340,380]]
	
	_leftHandArmHomeValues = 		[	0,			0,			0,		60,		0,			0,			0,		0,			0]
	
	_power_relais			= None		# the relais to activate the servo voltage 
	_relais_bit			=	-1		# the bit to set for the power relais (0-7)
	
	### GESTURES START
	
	def gestureGreet(self):
		for i in range(0,4):
			self.setArm(100,30,10) #self._handArmHomeValues[self._arm3])
			self.waitTillTargetReached()
			self.setArm(100,10,20) #self._handArmHomeValues[self._arm3])
			self.waitTillTargetReached()
			
	def gesturePointForward(self):
		self.setArm(50,0,self._handArmHomeValues[self._arm3])
		self.setHand(0,0,0,100,0)
		self.waitTillTargetReached()

	##GESTURES END
	
	def __init__(self, rightArm, i2cAdress, busnum,  power_relais, relais_bit):
		# Uncomment to enable debug output.
		#import logging
		#logging.basicConfig(level=logging.DEBUG)
		
		super().__init__(prio=-20)
		
		self.__shared_ints__			= SharedInts(max_length=3)
		self.__targets_reached_int__	= self.__shared_ints__.get_next_key()
				
		self._power = True
		
		if (rightArm == True):
			self._handArmServosMinMax = self._rightHandArmServosMinMax
			self._handArmHomeValues = self._rightHandArmHomeValues
			self._name = "right arm"
		else:
			self._handArmServosMinMax = self._leftHandArmServosMinMax
			self._handArmHomeValues = self._leftHandArmHomeValues
			self._name = "left arm"
			
		self._processName = self._name
		
		self.__last_servo_set_time = 0
		self._power_relais = power_relais
		self._relais_bit = relais_bit
		self.power_off()

		# Initialise the PCA9685 using the default address (0x40).
		#self._pwm = Adafruit_PCA9685.PCA9685()
		# Alternatively specify a different address and/or bus:
		self._pwm = Adafruit_PCA9685.PCA9685(address=i2cAdress, busnum=busnum)
		
		# Set frequency to 60hz, good for servos.
		self._pwm.set_pwm_freq(60)
		
		# reset servos
		for i in range(0,9):
			self.__targets.set_value(i, int(self._handArmHomeValues[i]))
			self.__values.set_value(i, self._handArmHomeValues[i])
			self.setServo(i,self._handArmHomeValues[i])	
			
		self.allTargetsReached = False
		
		super().StartUpdating()

	## multi process properties START ##
	
	@property
	def __last_servo_set_time(self):
		return self.GetSharedValue(self.__key_last_servo_set_time)
	@__last_servo_set_time.setter
	def __last_servo_set_time(self, value):
		self.SetSharedValue(self.__key_last_servo_set_time, value)
		
	@property
	def _power(self):
		return self.GetSharedValue(self.__key_power)
	@_power.setter
	def _power(self, value):
		self.SetSharedValue(self.__key_power, value)

	@property
	def allTargetsReached(self):
		#print (self.__shared_ints__.get_value(self.__targets_reached_int__)== 1)
		return self.__shared_ints__.get_value(self.__targets_reached_int__)== 1
	@allTargetsReached.setter
	def allTargetsReached(self, value):
		if (value == True):
			self.__shared_ints__.set_value(self.__targets_reached_int__,1)
		else:
			self.__shared_ints__.set_value(self.__targets_reached_int__,0)

	## multi process properties END ##
		
	def Update(self):
		#print("update start " + str(time.time()))
		if (super().updating_ended == True):
			return
		
		#print("update 1")
		
		timeDiff = time.time() - self._lastUpdateTime
		if (timeDiff < self._actualSpeedDelay):
			time.sleep(self._actualSpeedDelay - timeDiff)
		time.sleep(self._actualSpeedDelay)
		timeDiff = time.time() - self._lastUpdateTime
		timeDiff = min(timeDiff, self._actualSpeedDelay * 2)
		allReached = True
		maxSpeed = self._maxStepsPerSecond * timeDiff
		#print(maxSpeed)
		for i in range(0,9):
			reachedThis = True
			diff = int(self.__targets.get_value(i) - self.__values.get_value(i))
			plus = 0
			if (diff > 0):
				plus = max(0.1, min(diff , maxSpeed))
				reachedThis = False
			if (diff < 0):
				plus = min(-0.1, max(diff , -maxSpeed))
				reachedThis = False
			if (reachedThis == False):
				allReached = False
				newValue = self.__values.get_value(i) + plus
				self.__values.set_value(i,newValue)
				self.setServo(i,newValue)
		self.allTargetsReached = allReached
		self._lastUpdateTime = time.time()
		
		if (self.__last_servo_set_time + 5 < time.time()):
			# long time nothing done
			self.power_off()
			time.sleep(0.5)
		
		#print("update end")

	def setHand(self, finger1, finger2, finger3, finger4, finger5):
		# values 0 to 100
		self.__targets.set_value(self._finger1, finger1)
		self.__targets.set_value(self._finger2, finger2)
		self.__targets.set_value(self._finger3, finger3)
		self.__targets.set_value(self._finger4, finger4)
		self.__targets.set_value(self._finger5, finger5)
		self.allTargetsReached = False

	def setArm(self, arm1, arm2, arm3):
		# values 0 to 100
		self.__targets.set_value(self._arm1, arm1)
		self.__targets.set_value(self._arm2, arm2)
		self.__targets.set_value(self._arm3, arm3)
		self.allTargetsReached = False

	def waitTillTargetReached(self):
		while (self.allTargetsReached == False):
			time.sleep(self._actualSpeedDelay)

	def setServo(self, port, value):
		# values 0 to 100
		value = min(100,max(1,value))
		#inverse = self._inverseServo[port]
		minV = self._handArmServosMinMax[port][0]
		maxV = self._handArmServosMinMax[port][1]
		servo_space =  maxV-minV
		#if (inverse==True):
		#	value = 100-value
		self._pwm.set_pwm(port, 0, minV + int(value * servo_space / 100))
		self.__last_servo_set_time = time.time()
		self.power_on()
		
	# Helper function to make setting a servo pulse width simpler.
	#def set_servo_pulse(channel, pulse):
#		ipulse_length = 1000000				# 1,000,000 us per second
#		ipulse_length //= 60				# 60 Hz
#		iprint('{0}us per period'.format(pulse_length))
#		ipulse_length //= 4096				# 12 bits of resolution
#		iprint('{0}us per bit'.format(pulse_length))
#		ipulse *= 1000
#		ipulse //= pulse_length
#		ipwm.set_pwm(channel, 0, pulse)
		
	def power_off(self):
		if (self._power == False):
			return
		self._power = False
		self._power_relais.SetBit(self._relais_bit, 1)

	def power_on(self):
		if (self._power == True):
			return
		self._power = True
		self._power_relais.SetBit(self._relais_bit, 0)
		
	def portDemo(self, port):
		self.setServo(port,0)
		self.allTargetsReached = False
		time.sleep(1)
		self.setServo(port,100)
		self.allTargetsReached = False
		time.sleep(1)
		self.setServo(port, int(self._handArmHomeValues[port]))
		self.allTargetsReached = False
		time.sleep(1)
		
	def handDemo(self):
		self.setHand(0,0,0,0,0)
		time.sleep(3)
		self.setHand(100,100,100,100,100)
		time.sleep(3)
		
	def home(self):
		print("home " + self._name)
		for i in range(0,9):
			self.__targets.set_value(i, self._handArmHomeValues[i])
		self.allTargetsReached = False
		self.waitTillTargetReached()
		
	def turnOff(self):
		print("turning off " + self._name)
		for i in range(0,9):
			self._pwm.set_pwm(i, 0, 0)
		self.power_off()

	def Release(self):
		if (self._released == False):
			print("releasing " + self._name)
			self.home()
			self._released = True
			self.turnOff()
			print("super().EndUpdating() " + self._name)
			super().EndUpdating()
			
	def __del__(self):
		self.Release()
		
def exit_handler():
	right.Release()

if __name__ == "__main__":
	
	relais = RelaisI2C(I2cIoExpanderPcf8574(address=0x39, useAsInputs=False))
	
	right = HandAndArm(rightArm = True, i2cAdress=0x40, busnum=1, power_relais = relais, relais_bit=5)
	#left = HandAndArm(rightArm = False, i2cAdress=0x41, busnum=1, power_relais = relais, relais_bit=7)
	
	atexit.register(exit_handler)
	
	#handArm.setArm(50,0,100)
	
	ended = False
	
	right.gestureGreet()
	#left.gestureGreet()
	#right.gesturePointForward()
	#left.gesturePointForward()
	#handArm.setArm(100,handArm._handArmHomeValues[handArm._arm2],0) #self._handArmHomeValues[self._arm3])
	#time.sleep(1)
	#handArm.armGestureGreet()
	#time.sleep(1)
	#handArm.setArm(100,handArm._handArmHomeValues[handArm._arm2],0) #self._handArmHomeValues[self._arm3])
	#handArm.handGestureOpen()
	#time.sleep(4)
	
	#handArm.handGesturePoint()
	#handArm.armGesturePointFront()
	
	#right.setServo(right._arm1,50)
	#right.portDemo(right._arm1)
	
	#for i in range(1,3):
		#right.portDemo(right._arm1)
		#left.portDemo(left._arm1)
		#left.portDemo(left._finger4)
		#right.portDemo(right._finger5)
		#handArm.handDemo()
		
	time.sleep(2)
