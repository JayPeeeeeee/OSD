from SettingType import SettingType

class Setting(object):
    """description of class"""

    def __init__(self, name):
        self.name = name
        #self.value = None
        #self.type: SettingType = SettingType.NUMBER

    def show(self, image):
        print("Showing " + self.name)


