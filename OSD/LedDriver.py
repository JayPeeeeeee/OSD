import RPi.GPIO as GPIO

class LedDriver(object):
    """description of class"""

    def __init__(self, r, g, b):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(r, GPIO.OUT)

        GPIO.setup(g, GPIO.OUT)

        GPIO.setup(b, GPIO.OUT)

        

    def output(self, red, green, blue, brightness):
        print("R: " + str(red) + ", G: " + str(green) + ", B: " + str(blue) + " at " + str(brightness) + "%")
        pwm = GPIO.PWM(g, 1000)
        pwm.start(50)
