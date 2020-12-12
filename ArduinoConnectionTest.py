#!/usr/bin/python3
from kivy.config import Config
Config.read("BattleBox.ini")
import serial, time
from arena.arduinocommunicator import ArduinoCommunicator

if __name__ == '__main__':
  print("Running program!")
  arduino = serial.Serial(
      Config.get("arena", "led_arduino_com", fallback="/dev/ttyUSB0"),
      int(Config.get("arena", "arduino_baud_rate", fallback=115200)),
      timeout=float(Config.get("arena", "arduino_time_out", fallback=0.1)))

  com = ArduinoCommunicator(arduino)
  while not com.is_ready:
    time.sleep(0.1)
  x = time.time()
  com.write_line("pixels.fill, {0}, {1}, {2}, 0".format(255, 255, 255))
  print(time.time() - x)
  x = time.time()
  com.write_line("pixels.show")
  print(time.time() - x)
  x = time.time()
  time.sleep(3)
  x = time.time()
  com.write_line("pixels.clear")
  print(time.time() - x)
  x = time.time()
  com.write_line("pixels.show")
  print(time.time() - x)
  time.sleep(3)
  print("Complete")