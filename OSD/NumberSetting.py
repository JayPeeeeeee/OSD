from Setting import Setting

class NumberSetting(Setting):
    """description of class"""

    def __init__(self, name):
        super().__init__(name)
        self.value = None
        self.unit = None
        self.step = None
        self.minimum = None
        self.maximum = None

    def show(self, image):
        print("Showing number setting é")

