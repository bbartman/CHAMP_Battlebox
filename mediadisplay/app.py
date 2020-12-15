import os
# KIVY_BCM_DISPMANX_LAYER 

from kivy.config import Config
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
from kivy.core.window import Window
# from kivy.logger import Logger
# from math import floor
# import platform, re, random
# from datetime import datetime
from omxplayer.player import OMXPlayer

import pickle

# from kivy.core.video import Video

class MediaScreenManager(ScreenManager):
    pass
player = None 
class VideoScreen(Screen):
    slider = ObjectProperty()
    minimized = BooleanProperty(False)
    def __init__(self, **kwargs):
        super(VideoScreen, self).__init__(**kwargs)
        # self.play()

    @staticmethod
    def clearbckgrnd():
        Window.clearcolor = (0,0,0,0)

    @staticmethod
    def addbckgrnd():
        Window.clearcolor = (0,0,0,1)

    def play(self):
        global player
        player = self.player = OMXPlayer("media/rotating-logo.mkv", args=["--display", "7","--layer", "10000", "--loop"])
        self.player.set_video_pos(0,100,1280,800)
        #self.player.hide_video()
        #self.player.show_video()
        self.set_slider()
        Clock.schedule_once(self.quit, 20)
        Clock.schedule_interval(self.set_slider, 3)


    def playpause(self):
        self.player.play_pause()

    def quit(self, gg, **kwargs):
        self.player.quit()
        App.get_running_app().stop()


    def set_slider(self, *args):
        pos = self.player.position() # in seconds as int
        duration =  self.player.duration() # in seconds as float
        #return pos/duration
        self.slider.value_normalized = pos/duration
        #return 0.5

    def set_videopos(self, *args):
        pos = self.player.position() # in seconds as int
        duration =  self.player.duration() # in seconds as float
        if abs (pos/duration - self.slider.value_normalized) > 0.05:
            self.player.set_position(self.slider.value_normalized*duration)


    def change_size(self):
        #width 800
        #height 480
        if not self.minimized:
            self.player.set_video_pos(2,2,798,418)


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
# if movie doesn't work try the following.
# https://stackoverflow.com/questions/44955913/kivy-animation-class-to-animate-kivy-images/44957825
# This may be better!
# https://groups.google.com/forum/embed/?place=forum/kivy-users#!topic/kivy-users/18sZi27vQR4
# def run_media_subprocess(q, loggingq):
#     MediaApp(q, loggingq).run()

if __name__ == '__main__':
    app = MediaApp()
    try:
        app.run()
    finally:
        pass
        player.stop()
        # os.system('killall dbus-daemon')