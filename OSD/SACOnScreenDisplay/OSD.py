import cv2 as cv

from MenuItem import MenuItem
from Settings import Settings
from InputManager import InputManager
from SettingsManager import SettingsManager
from ButtonInput import ButtonInput

class OSD(object):
    """description of class"""

    def __init__(self, inputManager, settingsManager):
        self.inputManager = inputManager
        self.settingsManager = settingsManager
        self.settings = None
        
        self.areMenusActive = False
        self.activeMenu = None
        self.selectedMenu = None
        self.root = None
        self.editToken = None

    def __handleMenuNavigation(self):
        keyPressed = inputManager.read()
        activeMenuIndex = self.selectedMenu.menuItems.index(self.activeMenu)    

        if keyPressed == ButtonInput.UP:
            if activeMenuIndex > 0:
                self.activeMenu = self.selectedMenu.menuItems[activeMenuIndex - 1]

        if keyPressed == ButtonInput.DOWN:
            if activeMenuIndex < len(self.selectedMenu.menuItems) - 1:
                self.activeMenu = self.selectedMenu.menuItems[activeMenuIndex + 1]

        if keyPressed == ButtonInput.OK:
            self.selectedMenu = self.activeMenu
            if self.selectedMenu.menuItems != None and len(self.selectedMenu.menuItems) > 0 :
                self.activeMenu = self.selectedMenu.menuItems[0]

    def __initMenus(self):
        if self.root == None:
            self.root = MenuItem()
            self.root.menuItems = self.__createMenus()

        self.activeMenu = self.root.menuItems[0]
        self.selectedMenu = root

    def __createMenus(self):
        self.settings = self.settingsManager.getSettings()

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

    def __exitMenus(self):
        self.areMenusActive = False

    def __editSetting(self, setting, image):
        setting.show(frame)
        #read GPIO
        buttonInput = self.inputManager.read()
        #edit + current stage
        self.editToken = setting.edit(buttonInput, self.editToken)

        if self.editToken == None:
            return True

        return False

    def run(self, image):
        print("Running OSD...")
        if not self.areMenusActive:
            keyPressed = self.inputManager.read()
            if keyPressed != None:
                areMenusActive = True
                self.__initMenus()
        else:
            # Display the resulting frame
            if self.selectedMenu.menuItems != None and len(self.selectedMenu.menuItems) > 0:
                menuOffsetY = 30
                menuItemNumber = 0
                for menuItem in self.selectedMenu.menuItems:
                    color = (0, 0, 255, 255)
                    if menuItem == activeMenu:
                        color = (0, 255, 0, 255)
                    cv.putText(image, menuItem.getDisplayName(), (20,20 + menuOffsetY * menuItemNumber), cv.FONT_HERSHEY_SIMPLEX, 1, color, 1)
                    menuItemNumber += 1
                self.__handleMenuNavigation()
            else:        
                if editSetting(self.selectedMenu.setting, image):
                    self.settingsManager.saveSettings(this.settings)
                    exitMenus()