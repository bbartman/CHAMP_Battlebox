from RPi import GPIO

class L298NMotor:
    def __init__(self, enablePin, in1Pin, in2Pin, direction=0):
        self.en = enablePin
        self.in1 = in1Pin
        self.in2 = in2Pin
        self.dir = direction
        GPIO.setup(self.en, GPIO.OUT)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        # Setting both pins to low so motor doesn't move
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.p = GPIO.PWM(self.en, 100)

    def goForward(self, dutyCycle):
        if self.dir == 0:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        else:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
        self.p.start(dutyCycle)

    def goBackward(self, dutyCycle):
        if self.dir == 1:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        else:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
        self.p.start(dutyCycle)

    def stop(self):
        self.p.stop()
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)