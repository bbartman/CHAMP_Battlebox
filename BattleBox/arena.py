from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
                            BoundedNumericProperty, NumericProperty, BooleanProperty
from kivy.logger import Logger

class Player(EventDispatcher):
    name = StringProperty()
    door_button = BooleanProperty(False)
    ready_button = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)

    def on_door_button(self, instance, value):
        Logger.info("{0} door closed button {1}".format(value, self.name))

    def on_ready_button(self, instance, value):
        Logger.info("{0} ready button {1}".format(value, self.name))

class HardwareInterface(EventDispatcher):
    Player1 = Player(name = "Player1")
    Player2 = Player(name = "Player2")

    def __init__(self, **kwargs):
        super(HardwareInterface, self).__init__(**kwargs)

    def init(self):
        pass

    def set_led(self, index, red, green, blue):
        pass

    def led_fill(self, red, green, blue):
        pass

    def led_brightness(self, brightness):
        pass
    
    def leds_clear(self):
        print("clear leds")

    def leds_show(self):
        print("leds_show")

