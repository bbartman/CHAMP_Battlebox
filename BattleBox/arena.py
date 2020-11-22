#from BattleBox.data import BBDeathMatchProp
from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
                            BoundedNumericProperty, NumericProperty, BooleanProperty

import platform

#import gpiozero
#import sys
#import time
#import adafruit_blinka.agnostic as agnostic

#try:
#    import board
#except:
#    import BattleBox.mockboard as board

#import digitalio


#print("hello blinka!")

#print(
#    "Found system type: %s (sys.platform %s implementation %s) "
#    % (agnostic.board_id, sys.platform, sys.implementation.name)
#)

#print("board contents: ", dir(board))
##import gpiozero

##if platform.system() != 'Windows':
##    Device.pin_factory = MockFactory()
#x = board.D7
#led = digitalio.DigitalInOut(x)
#led.direction = digitalio.Direction.OUTPUT

#led.value = True
#time.sleep(0.5)
#led.value = False
#time.sleep(0.5)


class Player(EventDispatcher):
    door_detector = BooleanProperty(false)
    ready_button = BooleanProperty(false)

    def on_door_detector(self, *args):
        pass

    def on_ready_button(self, *args):
        pass

class LEDLightStrip(EventDispatcher):
    brightness = NumericProperty(1.0)
    auto_write = BooleanProperty(false)
    # NEO_GRB + NEO_KHZ800
    bytes_per_pixel = NumericProperty(3)
    ordering = StringProperty("NEO_GRB")
    length = NumericProperty(42)
    pixels = ListProperty()
    
    def on_brightness(self, *args):
        pass
    
    def on_auto_write(self, *args):
        pass
    
    def on_bytes_per_pixel(self, *args):
        pass
    
    def on_ordering(self, *args):
        pass
    
    def on_length(self, *args):
        pass

    def on_pixels(self, *args):
        pass
    

    

class Arena(EventDispatcher):
    Player1 = Player()
    Player2 = Player()
    def __init__(self, **kwargs):
        pass

    #def 