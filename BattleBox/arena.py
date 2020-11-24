from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
                            BoundedNumericProperty, NumericProperty, BooleanProperty
import threading

class Player(EventDispatcher):
    name = StringProperty()
    door_button = BooleanProperty(False)
    ready_button = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)

    def open_door(self):
        print("{0} Open door!".format(self.name))

    def secure_door_closed(self):
        print("{0} Securing door closed".format( self.name))

    def on_door_button(self, instance, value):
        print("{0} door closed button pressed!".format( self.name))

    def on_ready_button(self, instance, value):
        print("{0} ready button pressed!".format( self.name))

class HardwareInterface(EventDispatcher):
    Player1 = Player(name = "Player1")
    Player2 = Player(name = "Player2")

    def __init__(self, **kwargs):
        super(HardwareInterface, self).__init__(**kwargs)

    def init(self):
        print("Called init")

    def set_led(self, index, red, green, blue):
        print("set_led index = {0} red = {1} green = {2} blue = {3}".format(index, red, green, blue))

    def led_fill(self, red, green, blue):
        print("led_fill red = {0} green = {1} blue = {2}".format(red, green, blue))

    def led_brightness(self, brightness):
        print("led_brightness {0}".format(brightness))

    def leds_clear(self):
        print("clear leds")

    def leds_show(self):
        print("leds_show")

