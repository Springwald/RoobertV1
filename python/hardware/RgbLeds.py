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
#     ##################################
#     # Roobert RGB LED control module #
#     ##################################
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
import os, sys
from PIL import Image
from neopixel import *
from Roomba import Roomba
from PowerManagement import PowerManagement

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../libs" )

from MultiProcessing import MultiProcessing

class RgbLeds(MultiProcessing):

	# LED strip configuration:
	LED_COUNT      = 64+1+24      # Number of LED pixels.
	LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
	LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
	LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
	LED_BRIGHTNESS = 64    # Set to 0 for darkest and 255 for brightest
	LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
	
	_strip 			= None
	_program_path 	= None
	_released		= False
	_dimmer			 = 1
	
	_hearthPic		= None
	
	_pulse_phase	= 1
	_pulse_step		= 0
	
	_power_management 	= None

	def __init__(self, power_management):
		
		self._power_management = power_management
		
		super().__init__(prio=20)
		
		# Create NeoPixel object with appropriate configuration.
		self._strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS)
		# Intialize the library (must be called once before other functions).
		self._strip.begin()
		
		self._hearthPic = self.loadImage()
		
		super().StartUpdating()
		
	def colorWipe(self, color, wait_ms=0.1):
		#Wipe color across display a pixel at a time.
		for i in range(self._strip.numPixels()):
			self._strip.setPixelColor(i, color)
			self._strip.show()
			time.sleep(wait_ms/1000.0)
			
	def speed(self):
		col = Color (0,0,0)
		for m in range(0, 25):
			for i in range(self._strip.numPixels()):
				self._strip.setPixelColor(i, col)
			self._strip.show()
		col = Color (200,200,255)
		for m in range(0, 1):
			for i in range(self._strip.numPixels()):
				self._strip.setPixelColor(i, col)
			self._strip.show()
		
			
	def theaterChase(self, color, wait_ms=50, iterations=10):
		"""Movie theater light style chaser animation."""
		strip = self._strip
		for j in range(iterations):
			for q in range(3):
				for i in range(0, strip.numPixels(), 3):
					strip.setPixelColor(i+q, color)
				strip.show()
				time.sleep(wait_ms/1000.0)
				for i in range(0, strip.numPixels(), 3):
					strip.setPixelColor(i+q, 0)
	
	def wheel(self,pos):
		"""Generate rainbow colors across 0-255 positions."""
		if pos < 85:
			return Color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Color(0, pos * 3, 255 - pos * 3)
					
	def rainbowCycle(self, wait_ms=20, iterations=5):
		"""Draw rainbow that uniformly distributes itself across all pixels."""
		strip = self._strip
		for j in range(256*iterations):
			for i in range(strip.numPixels()):
				strip.setPixelColor(i, self.wheel(((int(i * 256 / strip.numPixels()) + j) & 255)))
			strip.show()
			time.sleep(wait_ms/1000.0)
					
	def loadImage(self):
		image_filename = my_path + '/../../Gfx/Body/hearth.gif'
		im = Image.open(image_filename)
		
		im.seek(im.tell()+1)
		
		p = im.getpalette()
		last_frame = im.convert('RGBA')
		
		if not im.getpalette():
			im.putpalette(p)
		
		new_frame = Image.new('RGBA', im.size)
		new_frame.paste(im,(0,0), im.convert('RGBA'))
		
		#ixels = im.load()
		
		return new_frame
			
	def showImage(self, img): 
		number =0
		pos =0
		for y in range(8):
			for x in range(8):
				#color = Color (200,0,0)
				RGB = img.getpixel((x,y))
				R,G,B,A = RGB
				color = Color(int(B * self._dimmer), int(R * self._dimmer),int(G * self._dimmer))
				self._strip.setPixelColor(number, color) #pixels[0,0])
				number = number + 1
				#pos = pos + 3
		self._strip.show()
		
	def show_battery_level_on_ring(self):
		level = (min(self._power_management.battery_power_in_percent,100)-50) * 2
		on = max(1,int(24 / 100 * level))
		#print (str(level) + " " +str(on))
		r = 255
		g = 0
		b = 0
		brightness = 20 # of 255
		for p in range(on):
			r = r - 255 / 24
			g = g + 255 / 24
			color = Color(int(g*brightness/255.0 ), int(r*brightness/255.0 ),int(b*brightness/255.0 ))
			self._strip.setPixelColor(p+64, color) 
		for p in range(on+1,24):
			color = Color(0,0,0)
			self._strip.setPixelColor(p+64, color) 
		self._strip.show()
		
	def show_button_led(self, color):
		level = (self._power_management.battery_power_in_percent-50) * 2
		self._strip.setPixelColor(64+24, color) 
		self._strip.show()
		
	def Off(self):
		number =0
		for y in range(8):
			for x in range(8):
				self._strip.setPixelColor(number, 0) 
				self._strip.show()
				number = number + 1
							
	def Update(self):
		
		if (super().updating_ended == True):
			return
			
		#print("RgbLed: Update");
			
		self.show_battery_level_on_ring()
			
		steps = 15
		delay = 0.1
		
		self._pulse_step = self._pulse_step + self._pulse_phase
		if (self._pulse_step > steps or self._pulse_step < 1):
			self._pulse_phase = - self._pulse_phase

		self._dimmer = 0.5/ steps * self._pulse_step
		self.showImage(self._hearthPic)
		time.sleep(delay)
		
		#self.rainbowCycle(wait_ms=10, iterations=5)
		
		speed = 100
		r = abs((time.time()* speed % 512)-255) / 2
		g = 0
		b = 0
		
		self.show_button_led(Color(int(g),int(r),int(b)))

		#self.colorWipe(Color(255,0, 0))  # Red wipe
		#self.theaterChase(self._strip, Color(127, 127, 127))  # White theater chase
		#time.sleep(2)
		
	def Release(self):
		if (self._released == False):
			self._released = True
			print("RGB LEDs releasing")
			super().EndUpdating()
			self.Off()

	def __del__(self):
		self.Release()

if __name__ == "__main__":

	roomba = Roomba()
	power = PowerManagement(roomba)

	print("1")

	leds = RgbLeds(power) 
	
	print("2")
	
	ended = False
	
	print("3")

	for a in range(10):
		

		
		time.sleep(1)
	
	#while ended == False:
	#	time.sleep(1)
		#print("hu")
	#	a=1
		#leds.speed()
		#leds.Update()
		#leds.colorWipe(Color(0,0,255),10)
		#leds.theaterChase(Color(0,0,255),50)
		#leds.rainbowCycle(wait_ms=10, iterations=5)
		
	#time.sleep(13)
		
	leds.Release()
		
	power.Release()
	if (roomba != None):
		roomba.Release()

