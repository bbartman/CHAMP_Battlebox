from kivy.config import Config
# Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.read("Media.ini")
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty, NumericProperty, BooleanProperty
# from BattleBox.data import BBViewModelProp, BBDeathMatchProp, BBSoccerMatchProp, BBRunDeathMatchProp
# from BattleBox.arena import HardwareInterface
# from kivy.core.window import Window
# from kivy.logger import Logger
# from math import floor
# import platform, re, random
# from datetime import datetime
import pickle
import multiprocessing as mp 

class MediaScreenManager(ScreenManager):
    pass

class MediaApp(App):
    def __init__(self, **kwargs):
        super(MediaApp, self).__init__(**kwargs)

    # def read_q(self, clock):
    #     try:
    #         something = self.q.get(0.005)
    #     except mp.TimeoutError as e:
    #         return True
    #     try:
    #         func = pickle.loads(something)
    #         func(self)
    #     except pickle.PickleError as e:
    #         Logger.error("Error reading pickle data", e)


    def build(self):
        root_widget = MediaScreenManager()
        return root_widget

# def run_media_subprocess(q, loggingq):
#     MediaApp(q, loggingq).run()

if __name__ == '__main__':
    MediaApp().run()