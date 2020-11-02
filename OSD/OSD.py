import os
import cv2 as cv
import jsonpickle
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
from LedDriver import LedDriver
from StateMachine import StateMachine
from picamera.array import PiRGBArray
from picamera import PiCamera
from Lepton import Lepton
import numpy as np

settingsFile = "..\OSD Settings.json"
settings = None
areMenusActive = False
activeMenu = None
selectedMenu = None
root = None
editToken = None
buttonInput = None
inputManager = InputManager(5, 6, 13)
ledDriver = LedDriver(17, 27, 22)
faceDet = cv.CascadeClassifier("/home/pi//SACLeptonRPi/haarcascade_frontalface_default.xml")
l = Lepton()
stateMachine = StateMachine()


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


def readInput():
    global inputManager
    return inputManager.read()

    #input = cv.waitKey(1) & 0xFF

    #if input == ord('u'):
    #    buttonInput = ButtonInput.UP

    #if input == ord('d'):
    #    buttonInput = ButtonInput.DOWN

    #if input == ord('o'):
    #    buttonInput = ButtonInput.OK
    
    return buttonInput

def handleMenuNavigation():
    global inputManager
    keyPressed = inputManager.read()

    global activeMenu, selectedMenu

    activeMenuIndex = selectedMenu.menuItems.index(activeMenu)    

    if keyPressed == ButtonInput.UP:
        if activeMenuIndex > 0:
            activeMenu = selectedMenu.menuItems[activeMenuIndex - 1]

    if keyPressed == ButtonInput.DOWN:
        if activeMenuIndex < len(selectedMenu.menuItems) - 1:
            activeMenu = selectedMenu.menuItems[activeMenuIndex + 1]

    if keyPressed == ButtonInput.OK:
        selectedMenu = activeMenu
        if selectedMenu.menuItems != None and len(selectedMenu.menuItems) > 0 :
            activeMenu = selectedMenu.menuItems[0]

    return True

def getSettings():
    global settingsFile, settings

    if settings == None:
        if os.path.isfile(settingsFile):
            print("Reading settings from file")
            f = open(settingsFile, "r")
            settings = jsonpickle.decode(f.read())
            f.close()        
            print("OK R" + str(settings.okColor.red))
        else:
            print(settingsFile + " is not a file, getting default settings alo")
            settings = getDefaultSettings()
            saveSettings()

    return settings

def getDefaultSettings():
    settings = Settings()
    showMeanTemperature = BooleanSetting("Show mean temperature")
    showMeanTemperature.value = False
    settings.showMeanTemperature = showMeanTemperature

    showFoundFace = BooleanSetting("Show found face")
    showFoundFace.value = False
    settings.showFoundFace = showFoundFace

    showWarmestZones = BooleanSetting("Show warmest zones")
    showWarmestZones.value = False
    settings.showWarmestZones = showWarmestZones

    screenPosition = TupleSetting("Screen position")
    screenPosition.value = (0, 50)
    settings.screenPosition = screenPosition

    screenDimensions = TupleSetting("Screen dimensions")
    screenDimensions.value = (360, 270)
    settings.screenDimensions = screenDimensions

    threshold = NumberSetting("Threshold")
    threshold.value = 35.7
    threshold.unit = 'deg'
    threshold.step = 0.1
    threshold.decimals = 1
    threshold.minimum = 35
    threshold.maximum = 40
    settings.threshold = threshold

    offset = NumberSetting("Offset")
    offset.value = 0.5
    offset.unit = 'deg'
    offset.step = 0.1
    offset.decimals = 1
    offset.minimum = 0
    offset.maximum = 2
    settings.offset = offset

    epsilon = NumberSetting("Epsilon")
    epsilon.value = 1.5
    epsilon.unit = "err"
    epsilon.step = 0.1
    epsilon.decimals = 1
    epsilon.minimum = 0
    epsilon.maximum = 3
    settings.epsilon = epsilon

    measurementsPerMean = NumberSetting("Measurements per mean")
    measurementsPerMean.value = 3
    measurementsPerMean.unit = "m/m"
    measurementsPerMean.step = 1
    measurementsPerMean.decimals = 0
    measurementsPerMean.minimum = 1
    measurementsPerMean.maximum = 5
    settings.measurementsPerMean = measurementsPerMean

    brightness = NumberSetting("Brightness")
    brightness.value = 75
    brightness.unit = "%"
    brightness.step = 1
    brightness.decimals = 0
    brightness.minimum = 0
    brightness.maximum = 100
    settings.brightness = brightness

    alarmColor = ColorSetting("Alarm color")
    alarmColor.red = 255
    alarmColor.green = 0
    alarmColor.blue = 0
    settings.alarmColor = alarmColor

    okColor = ColorSetting("OK color")
    okColor.red = 0
    okColor.green = 255
    okColor.blue = 0
    settings.okColor = okColor

    idleColor = ColorSetting("Idle color")
    idleColor.red = 0
    idleColor.green = 0
    idleColor.blue = 255
    settings.idleColor = idleColor

    return settings

def saveSettings():
    # TODO!
    global settingsFile, settings
    f = open(settingsFile, "w")
    f.write(jsonpickle.encode(settings))
    f.close()
    return False

def initMenus():
    global root, activeMenu, selectedMenu

    if root == None:
        root = MenuItem()
        root.menuItems = createMenus()

    activeMenu = root.menuItems[0]
    selectedMenu = root

def createMenus():
    settings = getSettings()

    smtMenu = MenuItem()
    smtMenu.setting = settings.showMeanTemperature

    sffMenu = MenuItem()
    sffMenu.setting = settings.showFoundFace

    swzMenu = MenuItem()
    swzMenu.setting = settings.showWarmestZones

    spMenu = MenuItem()
    spMenu.setting = settings.screenPosition

    sdMenu = MenuItem()
    sdMenu.setting = settings.screenDimensions

    viewItems = MenuItem()
    viewItems.name = "View"
    viewItems.menuItems = [smtMenu, sffMenu, swzMenu, spMenu, sdMenu]

    thresholdMenu = MenuItem()
    thresholdMenu.setting = settings.threshold

    offsetMenu = MenuItem()
    offsetMenu.setting = settings.offset

    epsilonMenu = MenuItem()
    epsilonMenu.setting = settings.epsilon

    mpmMenu = MenuItem()
    mpmMenu.setting = settings.measurementsPerMean

    measureItems = MenuItem()
    measureItems.name = "Measure"
    measureItems.menuItems = [thresholdMenu, offsetMenu, epsilonMenu, mpmMenu]

    brightnessMenu = MenuItem()
    brightnessMenu.setting = settings.brightness

    alarmColorMenu = MenuItem()
    alarmColorMenu.setting = settings.alarmColor

    okColorMenu = MenuItem()
    okColorMenu.setting = settings.okColor

    idleColorMenu = MenuItem()
    idleColorMenu.setting = settings.idleColor

    ledsItems = MenuItem()
    ledsItems.name = "LEDs"
    ledsItems.menuItems = [brightnessMenu, alarmColorMenu, okColorMenu, idleColorMenu]

    return [viewItems, measureItems, ledsItems]

def exitMenus():
    global areMenusActive
    areMenusActive = False

def editSetting(setting, frame):
    global inputManager
    setting.show(frame)
    #read GPIO
    buttonInput = inputManager.read()
    #edit + current stage
    global editToken
    editToken = setting.edit(buttonInput, editToken)

    if editToken == None:
        return True

    return False

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

    

    if not areMenusActive:
        keyPressed = inputManager.read()
        if keyPressed != None:
            areMenusActive = True
            initMenus()
        else:
            # Measure temp
            measureTemperature(frame)
            temp = random.randint(33, 38)
            brightness = settings.brightness.value
            if temp > settings.threshold.value:
                alarmColor = settings.alarmColor
                ledDriver.output(alarmColor.red, alarmColor.green, alarmColor.blue, brightness)
            else:
                okColor = settings.okColor
                ledDriver.output(okColor.red, okColor.green, okColor.blue, brightness)
    else:
        # Display the resulting frame
        if selectedMenu.menuItems != None and len(selectedMenu.menuItems) > 0:
            menuOffsetY = 30
            menuItemNumber = 0
            for menuItem in selectedMenu.menuItems:
                color = (0, 0, 255, 255)
                if menuItem == activeMenu:
                    color = (0, 255, 0, 255)
                cv.putText(frame, menuItem.getDisplayName(), (20,20 + menuOffsetY * menuItemNumber), cv.FONT_HERSHEY_SIMPLEX, 1, color, 1)
                menuItemNumber += 1
            if not handleMenuNavigation():
                break;
        else:        
            if editSetting(selectedMenu.setting, frame):
                saveSettings()
                exitMenus()
                
    #key = cv.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    shm.write(cv.flip(frame, 0))
    
    

# When everything done, release the capture
ledDriver.stop()
shm.detach()
cap.release()
cv.destroyAllWindows()