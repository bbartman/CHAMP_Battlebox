import board

class PiPin:
    def __init__(self, pin_number, gpio_name, blinka_name,
                 blinka_pin, supports_pwm=False):
        self._internal_pin = pin_number
        self._gpio_name = gpio_name
        self._blinka_name = blinka_name
        self._blinka_pin = blinka_pin
        self._supports_pwm = supports_pwm

    @property
    def pin_number(self):
        return self._internal_pin

    @property
    def gpio_name(self):
        return self._gpio_name

    @property
    def gpio_number(self):
        return int(self.gpio_name[4:])

    @property
    def blinka_name(self):
        return self._blinka_name

    @property
    def supports_pwm(self):
        return self._supports_pwm

    @property
    def blinka_pin(self):
        return self._blinka_pin

    def __repr__(self):
        return "pin(" + str(self.pin_number) + ", " + self.gpio_name + ", " + self.blinka_name + ")"


__allpins__ = [
    PiPin(3, "GPIO2", "SDA", board.SDA),
    PiPin(5, "GPIO3", "SCL", board.SCL),
    PiPin(7, "GPIO4", "D4", board.D4),
    PiPin(8, "GPIO14", "TXD", board.D14),
    PiPin(10, "GPIO15", "RXD", board.D15),
    PiPin(11, "GPIO17", "D17", board.D17),
    PiPin(12, "GPIO18", "D18", board.D18, True),
    PiPin(13, "GPIO27", "D27", board.D27),
    PiPin(15, "GPIO22", "D22", board.D22),
    PiPin(16, "GPIO23", "D23", board.D23),
    PiPin(18, "GPIO24", "D24", board.D24),
    PiPin(19, "GPIO10", "MOSI", board.D10),
    PiPin(21, "GPIO9", "MISO", board.D9),
    PiPin(22, "GPIO25", "D25", board.D25),
    PiPin(23, "GPIO11", "SCLK", board.SCLK),
    PiPin(24, "GPIO8", "CE0", board.CE0),
    PiPin(26, "GPIO7", "CE1", board.CE1),
    PiPin(29, "GPIO5", "D5", board.D5),
    PiPin(31, "GPIO6", "D6", board.D6),
    PiPin(32, "GPIO12", "D12", board.D12, True),
    PiPin(33, "GPIO13", "D13", board.D13, True),
    PiPin(35, "GPIO19", "D19", board.D19, True),
    PiPin(36, "GPIO16", "D16", board.D16),
    PiPin(37, "GPIO26", "D26", board.D26),
    PiPin(38, "GPIO20", "D20", board.D20),
    PiPin(40, "GPIO21", "D21", board.D21)
]


pinLookup = {str(x.pin_number):x for x in __allpins__ }
pinLookup.update({x.gpio_name : x for x in __allpins__})
pinLookup.update({x.blinka_name : x for x in __allpins__})

def getPin(NameOrNumber, RequirePWM=False):
    if not RequirePWM:
        if NameOrNumber not in pinLookup:
            raise Exception("Invalid pin name {0}, could not be found".format(NameOrNumber))
        return pinLookup.get(NameOrNumber)

    x = pinLookup.get(NameOrNumber, None)
    if x is None:
        raise Exception("Invalid Pin name {0}".format(NameOrNumber))
    if x.supports_pwm:
        raise Exception("requested pin must support pwm {0} does not".format(NameOrNumber))
    return x