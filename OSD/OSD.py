import cv2 as cv
import jsonpickle
from MenuItem import MenuItem
from Settings import Settings
from Setting import Setting
from NumberSetting import NumberSetting
from BooleanSetting import BooleanSetting
from TupleSetting import TupleSetting
from ColorSetting import ColorSetting

areMenusActive = False
activeMenu = None
selectedMenu = None
root = None

def readInput():
    return cv.waitKey(1) & 0xFF

def handleMenuNavigation():
    keyPressed = readInput()

    if keyPressed & 0xFF == ord('q'):
        return False

    global activeMenu, selectedMenu

    activeMenuIndex = selectedMenu.menuItems.index(activeMenu)    

    if keyPressed == ord('u'):
        if activeMenuIndex > 0:
            activeMenu = selectedMenu.menuItems[activeMenuIndex - 1]

    if keyPressed == ord('d'):
        if activeMenuIndex < len(selectedMenu.menuItems) - 1:
            activeMenu = selectedMenu.menuItems[activeMenuIndex + 1]

    if keyPressed == ord('o'):
        selectedMenu = activeMenu
        if selectedMenu.menuItems != None and len(selectedMenu.menuItems) > 0 :
            activeMenu = selectedMenu.menuItems[0]

    return True

def getSettings():
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
    settings.threshold = threshold

    offset = NumberSetting("Offset")
    offset.value = 0.5
    settings.offset = offset

    epsilon = NumberSetting("Epsilon")
    epsilon.value = 1.5
    settings.epsilon = epsilon

    measurementsPerMean = NumberSetting("Measurements per mean")
    measurementsPerMean.value = 3
    settings.measurementsPerMean = measurementsPerMean

    brightness = NumberSetting("Brightness")
    brightness.value = 0.75
    settings.brightness = brightness

    alarmColor = ColorSetting("Alarm color")
    alarmColor.value = (0, 255, 0, 255)
    settings.alarmColor = alarmColor

    okColor = ColorSetting("OK color")
    okColor.value = (0, 0, 255, 255)
    settings.okColor = okColor

    idleColor = ColorSetting("Idle color")
    idleColor.value = (255, 0, 0, 255)
    settings.idleColor = idleColor

    return settings

def saveSettings():
    # TODO!
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
    f = open("D:\Projects\OSD\OSD Settings.json", "w")
    f.write(jsonpickle.encode(settings))
    f.close()

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

def showEditNumberScreen(frame, setting: Setting, unit: str, step: float):
    color = (0, 0, 255, 255)
    cv.putText(frame, "{:.1f}".format(setting.value) + unit, (0,50) , cv.FONT_HERSHEY_SIMPLEX, 1, color, 1)
    keyPressed = readInput()

    if keyPressed == ord('o'):
        return True

    if keyPressed == ord('u'):
        setting.value += step

    if keyPressed == ord('d'):
        setting.value -= step

    return False


def editSetting(setting: Setting, frame):
    setting.show()

    return False

cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not areMenusActive:
        keyPressed = readInput()
        if keyPressed == ord('u') or keyPressed == ord('d') or keyPressed == ord('o'):
            areMenusActive = True
            initMenus()
    else:
        # Display the resulting frame
        if selectedMenu.menuItems != None and len(selectedMenu.menuItems) > 0:
            menuOffsetY = 30
            menuItemNumber = 0
            for menuItem in selectedMenu.menuItems:
                color = (0, 0, 255, 255)
                if menuItem == activeMenu:
                    color = (0, 255, 0, 255)
                cv.putText(frame, menuItem.getDisplayName(), (0,20 + menuOffsetY * menuItemNumber), cv.FONT_HERSHEY_SIMPLEX, 1, color, 1)
                menuItemNumber += 1
            if not handleMenuNavigation():
                break;
        else:        
            if editSetting(selectedMenu.setting, frame):
                exitMenus()

    cv.imshow('frame', frame)
    
    

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()