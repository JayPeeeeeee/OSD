import RPi.GPIO as GPIO

class LedDriver(object):
    """description of class"""

    def __init__(self, r, g, b):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(r, GPIO.OUT)
        self.r = GPIO.PWM(r, 1000)
        self.r.start(100)

        GPIO.setup(g, GPIO.OUT)
        self.g = GPIO.PWM(g, 1000)
        self.g.start(100)

        GPIO.setup(b, GPIO.OUT)
        self.b = GPIO.PWM(b, 1000)
        self.b.start(100)

        

    def output(self, red, green, blue, brightness):
        print("R: " + str(red) + ", G: " + str(green) + ", B: " + str(blue) + " at " + str(brightness) + "%")

    def stop():
        self.r.stop()
        self.g.stop()
        self.b.stop()
