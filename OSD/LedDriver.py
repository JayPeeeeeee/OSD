import RPi.GPIO as GPIO

class LedDriver(object):
    """description of class"""

    def __init__(self, r, g, b):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(r, GPIO.OUT)
        self.r = GPIO.PWM(r, 100)
        self.r.start(0)

        GPIO.setup(g, GPIO.OUT)
        self.g = GPIO.PWM(g, 100)
        self.g.start(0)

        GPIO.setup(b, GPIO.OUT)
        self.b = GPIO.PWM(b, 100)
        self.b.start(100)

        

    def output(self, red, green, blue, brightness):
        print("R: " + str(red) + ", G: " + str(green) + ", B: " + str(blue) + " at " + str(brightness) + "%")
        self.r.ChangeDutyCycle(_map(red, 0, 255, 0, 100))
        self.g.ChangeDutyCycle(_map(green, 0, 255, 0, 100))
        self.b.ChangeDutyCycle(_map(blue, 0, 255, 0, 100))

    def stop():
        self.r.stop()
        self.g.stop()
        self.b.stop()
        GPIO.cleanup()

    def _map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
