# Oled Display Thread

import threading
from config import Config

from lib_oled96 import ssd1306
from time import sleep
from PIL import ImageFont, ImageDraw, Image

from smbus import SMBus                  #  These are the only two variant lines !!

class OLEDDisplay(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)

	self.i2cbus = SMBus(1)                        #
	# 1 = Raspberry Pi but NOT early REV1 board
	self.oled = ssd1306(self.i2cbus)
	self.font = ImageFont.truetype('FreeSerif.ttf', 15)
	self.draw = self.oled.canvas   # "draw" onto this canvas, then call display() to send the canvas contents to the hardware.

	self.draw.text((2, 2),'PiDashCam starting...',  font=self.font, fill=1)
	self.oled.display()
	self.running = True

    def exit(self):
	self.oled.cls()
	self.oled.onoff(0)
    
    def run(self):
	while self.running:
	    pass