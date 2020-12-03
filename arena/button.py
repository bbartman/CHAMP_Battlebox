from RPi import GPIO
from arena import NormallyClosed, NormallyOpen

class PhysicalButton:
    def __init__(self, pi_pin, wiring, pull=GPIO.PUD_OFF, on_pressed=None, on_released=None):
        self._pi_pin = pi_pin
        self._pin = self.pi_pin.gpio_number
        self._wiring = wiring
        self._pressed = on_pressed
        self._released = on_released
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull)
        self._current_state = self.pressed
        GPIO.add_event_detect(self.pin, GPIO.BOTH)
        GPIO.add_event_callback(self.pin, self._do_cb)

    def _do_cb(self, value):
        temp = self.pressed
        if self._current_state == temp:
            return
        if temp:
            if self._pressed is not None:
                self._pressed()
        else:
            if self._released is not None:
                self._released()
        self._current_state = not self._current_state

    @property
    def pi_pin(self):
        return self._pi_pin

    @property
    def pin(self):
        return self._pin

    @property
    def wiring(self):
        return self._wiring

    @property
    def pressed(self):
        val = GPIO.input(self.pin)
        if self.wiring == NormallyClosed:
            if val == GPIO.LOW:
                return True
            return False
        else:
            return bool(val)

