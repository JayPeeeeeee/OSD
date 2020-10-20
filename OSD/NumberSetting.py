from Setting import Setting
from ButtonInput import ButtonInput
import cv2 as cv

class NumberSetting(Setting):
    """description of class"""

    def __init__(self, name):
        super().__init__(name)
        self.value: float = None
        self.unit: str = None
        self.step: float = None
        self.minimum: float = None
        self.maximum: float = None

    def show(self, image):
        color = (0, 0, 255, 255)
        cv.putText(image, "{:.1f}".format(self.value) + self.unit, (0,50) , cv.FONT_HERSHEY_SIMPLEX, 1, color, 1)

    def edit(self, input: ButtonInput, token: str) -> str:
        if input == ButtonInput.OK:
            return None

        if input == ButtonInput.UP:
            newValue = self.value + self.step
            if newValue <= self.maximum:
                self.value = newValue

        if input == ButtonInput.DOWN:
            newValue = self.value - self.step
            if newValue > self.minimum:
                self.value = newValue

        return "A"
