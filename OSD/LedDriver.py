import RPi.GPIO as GPIO

class LedDriver(object):
    """description of class"""

    def __init__(self, r, g, b):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(r, GPIO.OUT)
        self.r = GPIO.PWM(r, 255)
        self.r.start(0)

        GPIO.setup(g, GPIO.OUT)
        self.g = GPIO.PWM(g, 255)
        self.g.start(0)

        GPIO.setup(b, GPIO.OUT)
        self.b = GPIO.PWM(b, 255)
        self.b.start(255)

        

    def output(self, red, green, blue, brightness):
        print("R: " + str(red) + ", G: " + str(green) + ", B: " + str(blue) + " at " + str(brightness) + "%")
        self.r.ChangeDutyCycle(red)
        self.g.ChangeDutyCycle(green)
        self.b.ChangeDutyCycle(blue)

    def stop():
        self.r.stop()
        self.g.stop()
        self.b.stop()
        GPIO.cleanup()
