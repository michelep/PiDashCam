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

from PiDashCam.config import Config
from PiDashCam.gpspoller import GpsPoller
from PiDashCam.camera import Camera
from PiDashCam.gy80 import GY80Poller
from PiDashCam.bmp085 import BMP085Poller
from PiDashCam.oled import OLEDDisplay

logging.basicConfig(filename='pidashcam.log', level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
Config.log = logging.getLogger(__file__)

Config.gpsd = None
gpsTime = False
TIMEZ = 2
 
def exit_handler(signal, frame):
    Config.log.info('PiDashCam STOP')
    sys.exit(0)
 
signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTSTP, exit_handler)

if __name__ == "__main__":
    Config.log.info('PiDashCam START')

    threads = []

    gps_thread = GpsPoller()
    threads.append(gps_thread)

    camera_thread = Camera()
    threads.append(camera_thread)

    gy80_thread = GY80Poller()
    threads.append(gy80_thread)

    bmp085_thread = BMP085Poller()
    threads.append(bmp085_thread)

    display_thread = OLEDDisplay()
    threads.append(display_thread)

    try:
	for t in threads:
	    t.start()

	while True:
	    time.sleep(5)
	    Config.log.debug("lat: %s lng: %s alt: %s"%(Config.gpsd.fix.latitude,Config.gpsd.fix.longitude,Config.gpsd.fix.altitude))

	    if Config.gpsd.utc != None and Config.gpsd.utc != '' and gpsTime != True:
		tzhour = int(Config.gpsd.utc[11:13])+TIMEZ
		if (tzhour>23):
		    tzhour = (int(Config.gpsd.utc[11:13])+TIMEZ)-24
		    gps_time = Config.gpsd.utc[0:4] + Config.gpsd.utc[5:7] + Config.gpsd.utc[8:10] + ' ' + str(tzhour) + Config.gpsd.utc[13:19]
		    Config.log.info("Setting system time to GPS time (%s)..."%str(tzhour))
		    os.system('sudo date --set="%s"' % gps_time)
		    gpsTime = True
	    
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
	print "\nKilling Thread..."
	for t in threads:
	    t.running = False
	    t.join()

