import os
import cv2 as cv
import sysv_ipc as ipc
import time 
import random
from subprocess import call
from threading import Thread
from ButtonInput import ButtonInput
from MenuItem import MenuItem
from Settings import Settings
from Setting import Setting
from NumberSetting import NumberSetting
from BooleanSetting import BooleanSetting
from TupleSetting import TupleSetting
from ColorSetting import ColorSetting
from InputManager import InputManager
from SettingsManager import SettingsManager
from LedDriver import LedDriver
from StateMachine import StateMachine
from .SACOnScreenDisplay.OSD import OSD
from picamera.array import PiRGBArray
from picamera import PiCamera
from Lepton import Lepton
import numpy as np

buttonInput = None
settingsManager = SettingsManager()
stateMachine = StateMachine()
inputManager = InputManager(5, 6, 13)
ledDriver = LedDriver(17, 27, 22)
faceDet = cv.CascadeClassifier("/home/pi//SACLeptonRPi/haarcascade_frontalface_default.xml")
l = Lepton()
osd = OSD(inputManager, settingsManager)


# Target screen is 12", 1024x768 or 768x1024 in portrait mode
screenWidth = 768
screenHeight = 1024
# Sensor size is 80x60
sensorWidth = 80
sensorHeight = 60
# Lepton offset in degC
corrVal = 0
maxVal = 0
feverThresh = 35.4

def measureTemperature(image):
    print("measuring")
    raw,_ = l.capture()

    maxVal = np.amax(raw)
    print("max val: " + str(maxVal))

def startDisplay():
    call(["../../SACLeptonRPi/SACDisplayMixer/OGLESSimpleImageWithIPC"])
   
th1 = Thread(target=startDisplay)
th1.start()
time.sleep(1)

key = ipc.ftok(".", ord('i'))
shm = ipc.SharedMemory(key, 0, 0)

camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
camera.meter_mode = 'spot'
getSettings()
time.sleep(0.5)

shm.attach()

for data in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    frame = data.array

    # if OSD is running -> OSD.Run()
    # else
    # if there was an input -> statemachine.stop() + OSD.Run()
    # else -> statemachine.run()

    osd.run(frame)
                
    #key = cv.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    shm.write(cv.flip(frame, 0))
    
    

# When everything done, release the capture
ledDriver.stop()
shm.detach()
cap.release()
cv.destroyAllWindows()