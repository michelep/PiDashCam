#!/usr/bin/env python
#
# PyDashCam
#
#
import io
import random
import picamera
# from PIL import Image, ImageDraw, ImageFont

import threading
from config import Config

# Video Resolution
VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280

class Camera(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)
	Config.log.debug('[INIT] Camera thread')
	self.camera = picamera.PiCamera()
	self.camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
        self.camera.framerate = 30
	self.stream = picamera.PiCameraCircularIO(self.camera, seconds=20)
	self.camera.start_recording(self.stream, format='h264')
	self.running = True

    def write_video(self):
	Config.log.debug('Writing video to disk')
	with self.stream.lock:
    	    # Find the first header frame in the video
    	    for frame in self.stream.frames:
        	if frame.frame_type == picamera.PiVideoFrameType.sps_header:
            	    self.stream.seek(frame.position)
            	    break
    	    # Write the rest of the stream to disk
#    	    with io.open('./cap/motion.h264', 'wb') as output:
#        	output.write(self.stream.read())

    def exit(self):
    	self.camera.stop_recording()
    
    def run(self):
	while self.running:
    	    self.camera.wait_recording(1)
    	    self.camera.wait_recording(10)
    	    self.write_video()
