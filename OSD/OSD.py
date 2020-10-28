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
faceDet = cv2.CascadeClassifier("/home/pi//SACLeptonRPi/haarcascade_frontalface_default.xml")
l = Lepton()


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
    global sensorWidth, sensorHeight, maxVal

    runningAvg = 0
    thSampleCount = 0
    thSampleAcc = []
    thDataValid = False
    nThSamplesToAverage = 6

    gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    rects = faceDet.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(180,180))
    faceBoxes = [(y,x+w, y+h, x) for (x,y,w,h) in rects]
    if len(faceBoxes) > 0:
        tcFace1 = faceBoxes[0] # true color ROI
        # transform the coordinates from true color image space to thermal image space using the affine transform matrix M
        # See https://docs.opencv.org/2.4/modules/imgproc/doc/geometric_transformations.html
        M = np.array([[1.5689e-1, 8.6462e-3, -1.1660e+1],[1.0613e-4, 1.6609e-1, -1.4066e+1]])
        P_slt = np.array([[tcFace1[3]],[tcFace1[0]],[1]]) # 'slt' source left top
        P_srt = np.array([[tcFace1[1]],[tcFace1[0]],[1]]) # 'srt' source right top
        P_slb = np.array([[tcFace1[3]],[tcFace1[2]],[1]]) # 'slb' source left bottom
        P_srb = np.array([[tcFace1[1]],[tcFace1[2]],[1]]) # 'srb' source right bottom
        P_dlt = np.dot(M, P_slt)
        P_drt = np.dot(M, P_srt)
        P_dlb = np.dot(M, P_slb)
        P_drb = np.dot(M, P_srb)
        thFace1Cnts = np.array([P_dlt, P_drt, P_dlb, P_drb], dtype=np.float32)
        for (top,right,bottom,left) in faceBoxes:
            cv.rectangle(image,(left,top),(right,bottom), (100,255,100), 1)

    # get thermal image from Lepton
    raw,_ = l.capture()
    # find maximum value in raw lepton data array in thRoi (face1) slice of raw data.
    if len(faceBoxes) > 0:
        thRoi = cv.boundingRect(thFace1Cnts)
        x,y,w,h = thRoi
        # x any shold not be negative. Clip the values.
        x = max(0, min(x, sensorWidth))
        y = max(0, min(y, sensorHeight))
        thRoiData = raw[y:y+h, x:x+w]
        maxVal = np.amax(thRoiData)
	    # get running average over N thermal samples
        if (thSampleCount < nThSamplesToAverage):
            thSampleCount += 1
            thSampleAcc.append(maxVal)
        else:
            thDataValid = True
            thSampleAcc.append(maxVal)
            thSampleAcc.pop(0)
            runningAvg = sum(thSampleAcc)/len(thSampleAcc)
            maxCoord = np.where(thRoiData == maxVal)
    else:
	    # No faces found.
        runningAvg = 0
        thSampleCount = 0
        del thSampleAcc[:]
        thDataValid = False

    # text position
    txtPosition = (500,50)

    cv.normalize(raw, raw, 0, 65535, cv.NORM_MINMAX) # extend contrast
    np.right_shift(raw, 8, raw) # fit data into 8 bits
    # draw roi if any
    if len(faceBoxes) > 0:
            x,y,w,h = thRoi
            cv.rectangle(raw, (x,y), (x+w,y+h), 255, 1)
    # make uint8 image
    thermal = np.uint8(raw)
    # convert grayscale to BGR
    thermal = cv.cvtColor(thermal, cv.COLOR_GRAY2BGR)
    color = image

    # Put data on top of the image if a face was detected.
    if len(faceBoxes) == 1 and thDataValid:
#            measTemp = (float(maxVal/100.0)-273.15) + corrVal
        measTemp = (float(runningAvg/100.0)-273.15)
        if measTemp > feverThresh:
            cv.putText(color, "{}degC".format(measTemp), txtPosition, cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255,255), 2)
        else:
            cv.putText(color, "{}degC".format(measTemp), txtPosition, cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0,255),2)

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
#cap = cv.VideoCapture(0)
#cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640)
#cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
getSettings()
time.sleep(0.5)

shm.attach()

for data in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
#while(True):
    # Capture frame-by-frame
    #ret, frame = cap.read()
    frame = data.array

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