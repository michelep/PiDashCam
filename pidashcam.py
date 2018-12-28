#!/usr/bin/env python
#
# PiDashCam
#
# Michele <o-zone@zerozone.it> Pinassi
#

import os
import time
import logging
import signal
import sys

import pygame

from PiDashCam.config import Config
from PiDashCam.gpspoller import GpsPoller
from PiDashCam.camera import Camera
from PiDashCam.gy80 import GY80Poller
from PiDashCam.bmp085 import BMP085Poller

logging.basicConfig(filename='pidashcam.log', level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
Config.log = logging.getLogger(__file__)

Config.gpsd = None
gpsTime = False
TIMEZ = 2
Config.isRun = True

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

def exit_handler(signal, frame):
    if(Config.isRun):
	Config.isRun=False
	print "[INFO] exitHandler(). Please wait..."
	Config.log.info('PiDashCam EXIT Handler')

signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTSTP, exit_handler)

if __name__ == "__main__":
    Config.log.info('PiDashCam START')

    os.environ['SDL_VIDEODRIVER'] = 'fbcon'
    os.environ["SDL_FBDEV"] = "/dev/fb0"

    print("[INFO] Initializing display...")

    try:
        pygame.init()
	pygame.display.init()
	pygame.font.init()

        display_info = pygame.display.Info()

	print display_info

	screen = pygame.display.set_mode([display_info.current_w,display_info.current_h], pygame.FULLSCREEN)

	font = pygame.font.Font(None, 10)
	clock = pygame.time.Clock()
    except:
	print "[FATAL] Error initilizing display"
	Config.log.error("Unable to initialize display")
	exit()

    print("[INFO] Display done. Initializing modules...")

    screen.fill(BLACK)

    text = font.render("PiDashCam initializing...", True, WHITE)
    screen.blit(text, [10, 10])

    pygame.display.flip()
    
    # Launch threads...
    threads = []

    gps_thread = GpsPoller()
    threads.append(gps_thread)

    camera_thread = Camera()
    threads.append(camera_thread)

    gy80_thread = GY80Poller()
    threads.append(gy80_thread)

    bmp085_thread = BMP085Poller()
    threads.append(bmp085_thread)

    try:
	for t in threads:
	    t.start()
    except:
	print "[FATAL] Something wrong starting threads..."
	exit()

    print "[INIT] Modules intialized. Go."

    screen.fill(BLACK)
    pygame.draw.line(screen, GREEN, [0, 50], [640,50], 3)

    while Config.isRun:
        for event in pygame.event.get():
	    print event
	    if event.type == pygame.QUIT:
	        Config.isRun = False

	# Update screen
	text = font.render("lat:%s lng:%s alt:%s"%(Config.gpsd.fix.latitude,Config.gpsd.fix.longitude,Config.gpsd.fix.altitude), True, WHITE)
	screen.blit(text,[10,10])

	# time.sleep(1)
	# Config.log.debug("lat: %s lng: %s alt: %s"%(Config.gpsd.fix.latitude,Config.gpsd.fix.longitude,Config.gpsd.fix.altitude))

	# Sync time if needed
	if Config.gpsd.utc != None and Config.gpsd.utc != '' and gpsTime != True:
	    tzhour = int(Config.gpsd.utc[11:13])+TIMEZ
	    if (tzhour>23):
	        tzhour = (int(Config.gpsd.utc[11:13])+TIMEZ)-24
	        gps_time = Config.gpsd.utc[0:4] + Config.gpsd.utc[5:7] + Config.gpsd.utc[8:10] + ' ' + str(tzhour) + Config.gpsd.utc[13:19]
	        Config.log.info("Setting system time to GPS time (%s)..."%str(tzhour))
	        os.system('sudo date --set="%s"' % gps_time)
	        gpsTime = True

    	# Update the screen
	clock.tick(60)
	pygame.display.flip()

    pygame.quit()

    print "[INFO] Quitting. Killing Threads..."

    for t in threads:
        t.running = False
        t.join()

