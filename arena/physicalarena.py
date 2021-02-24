import sys, serial, time, sys, traceback, threading, atexit
from kivy.config import Config
from arena.pins import getPin
from RPi import GPIO
from kivy.clock import Clock, mainthread
#from arena.L298N import L298NMotor
from arena.relaymotorcontroller import RelayMotorController
from arena.button import PhysicalButton
from arena import NormallyClosed, NormallyOpen
from BattleBox.arena import Player
from kivy.event import EventDispatcher
from kivy.logger import Logger
from arena.arduinocommunicator import ArduinoCommunicator
from itertools import groupby
from operator import itemgetter

def parseLEDRanges(ledRanges):
    items = set()
    for splitRange in ledRanges.split(","):
        splitRange.strip()
        if '-' in splitRange:
            r = splitRange.split('-')
            if len(r) != 2:
                raise Exception("Failed to split on '-' range {0}".format(splitRange))
            r[0].strip()
            r[1].strip()
            try:
                start = int(r[0])
                end = int(r[1])
            except:
                raise Exception("Invalid range or led number {0}".format(splitRange))
            for x in range(start, end):
                if x in items:
                    raise Exception("Duplicate item {0}".format(x))
                items.update([x])
        else:
            try:
                val = int(splitRange)
            except:
                raise Exception("Invalid range or led number {0}".format(splitRange))
            if val in items:
                raise Exception("Duplicate item in range {0}".format(val))
            items.update([val])
    ret = sorted([x for x in items])
    return ret

def build_quick_send_led_range(ledsForPlayer):
    if len(ledsForPlayer) == 0:
        raise ValueError("Invalid LED range set, no LED's provided")
    ret = []
    for k, g in groupby(enumerate(ledsForPlayer), lambda ix : ix[0] - ix[1]):
        temp = [x for x in map(itemgetter(1), g)]
        if len(temp) == 0:
            continue
        ret.append((temp[0], temp[-1] - temp[0] + 1))
    return ret                
    
class Arena(EventDispatcher):
    NO_NC_vars = { "NC":NormallyClosed, "NO": NormallyOpen}
    Pull_vars = { "UP":GPIO.PUD_UP, "DOWN": GPIO.PUD_DOWN, "OFF":GPIO.PUD_OFF}
    player_1 = Player(name = "Player1")
    player_2 = Player(name = "Player2")
    def __init__(self, **kwargs):
        super(Arena, self).__init__(**kwargs)
        #self.motor_enable_1 = getPin(Config.get("arena", "motor_enable_1_pin"))
        #self.motor_in_1 = getPin(Config.get("arena", "motor_in_1_pin"))
        #self.motor_in_2 = getPin(Config.get("arena", "motor_in_2_pin"))
        #self.motor_enable_2 = getPin(Config.get("arena", "motor_enable_2_pin"))
        #self.motor_in_3 = getPin(Config.get("arena", "motor_in_3_pin"))
        #self.motor_in_4 = getPin(Config.get("arena", "motor_in_4_pin"))
        self.motor_1_dir = Config.get("arena", "player_1_door_motor_direction",
                                      vars={ "forward": 0, "backward": 1 },
                                      fallback=0)
        self.motor_2_dir = Config.get("arena", "player_2_door_motor_direction",
                                      vars={"forward" : 0,"backward" : 1},
                                      fallback=0)
        self.player_1_ready_pin = getPin(Config.get("arena", "player_1_ready_pin"))
        self.player_1_ready_button_wiring = Config.get("arena", "player_1_ready_wiring",
                                                       vars=Arena.NO_NC_vars,
                                                       fallback=NormallyOpen)
        self.player_1_ready_pull = Config.get("arena", "player_1_ready_pull",
                                              vars=Arena.Pull_vars, fallback=GPIO.PUD_DOWN)

        self.player_2_ready_pin = getPin(Config.get("arena", "player_2_ready_pin"))
        self.player_2_ready_button_wiring = Config.get("arena", "player_2_ready_wiring",
                                                       vars=Arena.NO_NC_vars,
                                                       fallback=NormallyOpen)
        self.player_2_ready_pull = Config.get("arena", "player_2_ready_pull",
                                              vars=Arena.Pull_vars, fallback=GPIO.PUD_DOWN)

        self.player_1_door_sensor_pin = getPin(Config.get("arena", "player_1_door_pin"))
        self.player_1_door_sensor_wiring = Config.get("arena", "player_1_door_wiring",
                                                      vars=Arena.NO_NC_vars,
                                                      fallback=NormallyOpen)
        self.player_1_door_pull = Config.get("arena", "player_1_door_pull",
                                             vars=Arena.Pull_vars,
                                             fallback=GPIO.PUD_DOWN)

        self.player_2_door_sensor_pin = getPin(Config.get("arena", "player_2_door_pin"))
        self.player_2_door_sensor_wiring = Config.get("arena", "player_2_door_wiring",
                                                      vars=Arena.NO_NC_vars,
                                                      fallback=NormallyOpen)
        self.player_2_door_pull = Config.get("arena", "player_2_door_pull",
                                             vars=Arena.Pull_vars,
                                             fallback=GPIO.PUD_DOWN)

        self.led_light_count = int(Config.get("arena", "led_light_count", fallback="43"))

        self.player_1_leds = parseLEDRanges(Config.get("arena", "player_1_leds"))
        self.player_2_leds = parseLEDRanges(Config.get("arena", "player_2_leds"))

        overlappingLEDs = set(self.player_1_leds) & set(self.player_2_leds)
        if len(overlappingLEDs) > 0:
            raise Exception("some lights have been assigned " +
                            "to both players {0}",
                            ",".join([str(x) for x in overlappingLEDs]))
        # Building the fastest way to send single player led ranges without
        # overloading the arduino and causing fragmented message errors, I hope.
        self.player_1_led_ranges = build_quick_send_led_range(self.player_1_leds)
        self.player_2_led_ranges = build_quick_send_led_range(self.player_2_leds)

        GPIO.setmode(GPIO.BCM)

        # Creating all of the different buttons and things we
        # will need to interact with the system.
        #self.player_1_motor = RelayMotorController(self.motor_in_1.gpio_number,
        #    self.motor_in_2.gpio_number, self.motor_1_dir)

        # Second half of the motor controller.
        #self.player_2_motor = RelayMotorController(self.motor_in_3.gpio_number,
        #    self.motor_in_4.gpio_number, self.motor_2_dir)


        self.player_1_ready_button = PhysicalButton(self.player_1_ready_pin,
                                                    self.player_1_ready_button_wiring,
                                                    self.player_1_ready_pull,
                                                    self.player_1_ready_button_pressed,
                                                    self.player_1_ready_button_released)

        self.player_2_ready_button = PhysicalButton(self.player_2_ready_pin,
                                                    self.player_2_ready_button_wiring,
                                                    self.player_2_ready_pull,
                                                    self.player_2_ready_button_pressed,
                                                    self.player_2_ready_button_released)

        self.player_1_door_sensor = PhysicalButton(self.player_1_door_sensor_pin,
                                                   self.player_1_door_sensor_wiring,
                                                   self.player_1_door_pull,
                                                   self.player_1_door_sensor_pressed,
                                                   self.player_1_door_sensor_released)

        self.player_2_door_sensor = PhysicalButton(self.player_2_door_sensor_pin,
                                                   self.player_2_door_sensor_wiring,
                                                   self.player_2_door_pull,
                                                   self.player_2_door_sensor_pressed,
                                                   self.player_2_door_sensor_released)
        # Assigning initial data values so that we have the correct information on start up.
        self.player_1.ready_button = self.player_1_ready_button.pressed
        self.player_1.door_button = self.player_1_door_sensor.pressed
        self.player_2.ready_button = self.player_2_ready_button.pressed
        self.player_2.door_button = self.player_2_door_sensor.pressed
        
        # self.mutex = threading.Lock()
        # self.arduino_ready = False
        # Setting up arduino communication
        self.serial_arduino = serial.Serial(
            Config.get("arena", "led_arduino_com", fallback="/dev/ttyUSB0"),
            int(Config.get("arena", "arduino_baud_rate", fallback=115200)),
            timeout=float(Config.get("arena", "arduino_time_out", fallback=0.5)),
            rtscts=True)
        self.arduino = ArduinoCommunicator(self.serial_arduino)
        # TODO: Put a time out here so I can disable sending to and from the arduino.
        # if it is broken or something else strange occurs.
        # A minimal amount of time something like 3 seconds should be fine.
        while not self.arduino.is_ready:
            time.sleep(0.01)

        self.arduino.write_line("pixels.reset, {0}, {1}".format(
            self.led_light_count, int(Config.get("arena", "arduino_lights_pin")) ))

        atexit.register(self.turn_off_lights)

    def turn_off_lights(self):
        self.arduino.write_line("pixels.clear")
        self.arduino.write_line("pixels.show")

    def shutdown_connection(self):
        self.arduino.stop()


    @mainthread
    def player_1_ready_button_pressed(self):
        self.player_1.ready_button = True

    @mainthread
    def player_1_ready_button_released(self):
        self.player_1.ready_button = False

    @mainthread
    def player_2_ready_button_pressed(self):
        self.player_2.ready_button = True

    @mainthread
    def player_2_ready_button_released(self):
        self.player_2.ready_button = False

    @mainthread
    def player_1_door_sensor_pressed(self):
        self.player_1.door_button = True

    @mainthread
    def player_1_door_sensor_released(self):
        self.player_1.door_button = False

    @mainthread
    def player_2_door_sensor_pressed(self):
        self.player_2.door_button = True

    @mainthread
    def player_2_door_sensor_released(self):
        self.player_2.door_button = False

    def init(self):
        pass

    def set_led(self, index, red, green, blue):
        self.arduino.write_line("pixels.setPixelColor, {0}, {1}, {2}, {3}".format(
            int(index), int(green), int(red), int(blue) ))
        self.arduino.write_line("pixels.show")

    def led_fill(self, red, green, blue):
        self.arduino.write_line("pixels.fill, {0}, {1}, {2}, 0".format(
            int(green), int(red), int(blue) ))
        self.arduino.write_line("pixels.show")

    def led_brightness_and_fill(self, brightness, red, green, blue):
        self.arduino.write_line("pixels.fill, {0}, {1}, {2}, 0".format(
            int(green), int(red), int(blue) ))
        self.arduino.write_line("pixels.setBrightness, {0}".format( int(brightness) ))
        self.arduino.write_line("pixels.show")

    def led_n_fill(self, red, green, blue, start=0, count=-1):
        if count <= -1:
            count = self.led_light_count
        cmd = "pixels.fill, {0}, {1}, {2}, {3}, {4}".format(
            int(green), int(red), int(blue), int(start), int(count) )
        self.arduino.write_line(cmd)
        self.arduino.write_line("pixels.show")

    def led_player_1_lights(self, red, green, blue):
        for x in self.player_1_led_ranges:
            self.arduino.write_line("pixels.fill, {0}, {1}, {2}, {3}, {4}".format(
                                    int(green), int(red), int(blue), int(x[0]), int(x[1])))
        self.arduino.write_line("pixels.show")

    def led_player_2_lights(self, red, green, blue):
        for x in self.player_2_led_ranges:
            self.arduino.write_line("pixels.fill, {0}, {1}, {2}, {3}, {4}".format(
                                    int(green), int(red), int(blue), int(x[0]), int(x[1])))
        self.arduino.write_line("pixels.show")

    def led_brightness(self, brightness):
        self.arduino.write_line("pixels.setBrightness, {0}".format(
                                        int(brightness)) )
        self.arduino.write_line("pixels.show")

    def get_led_count(self):
        return self.led_light_count

    def close_player_1_door(self):
        self.arduino.write_line("m1.close")

    def open_player_1_door(self):
        self.arduino.write_line("m1.open")    
        
    def stop_player_1_door(self):
        self.arduino.write_line("m1.off")
        
    def close_player_2_door(self):
        self.arduino.write_line("m2.open")
        
    def open_player_2_door(self):        
        self.arduino.write_line("m2.close")
        
    def stop_player_2_door(self):
        self.arduino.write_line("m2.off")
        