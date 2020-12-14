from kivy.config import Config
# Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.read("BattleBox.ini")
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
from BattleBox.data import BBViewModelProp, BBDeathMatchProp, BBSoccerMatchProp, BBRunDeathMatchProp
from BattleBox.arena import HardwareInterface
from kivy.core.window import Window
from kivy.logger import Logger
from math import floor
import platform, re, random
from datetime import datetime
import subprocess as subp
import pickle

random.seed(datetime.now())

# Coloring = Red->Green->Blue
RED = (255, 0, 0)
MATCH_COUNT_DOWN_RED = (218, 83, 10)
YELLOW = (255, 255, 0)
DD_YELLOW = (200, 255, 0)
GREEN = (0, 255, 0)
SOCCER_GREEN = (0, 255, 68)
ORANGE = (255, 68, 0)
PURPLE = (93, 0, 255)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PINK = (255, 0, 149)
DOOR_NOT_CLOSED_WARNING_COLOR = (255, 174, 0)
PLAYER_2_COLOR = (0, 110, 255)
PLAYER_1_COLOR = RED
STOP_LIGHT_RED = (184, 29, 19)
STOP_LIGHT_ORANGE =	(218, 83, 10)
STOP_LIGHT_YELLOW = (239, 183, 0)
STOP_LIGHT_GREEN = (0, 255, 0)

BrightnessPerMillis = 1/30

class MainScreen(Screen):
    lights_brightness = NumericProperty(0)

    def __init__(self, **kwargs): 
        super(MainScreen, self).__init__(**kwargs)
        self.Breath = None
        self.on_enter()

    def on_enter(self):
        App.get_running_app().arena.led_brightness_and_fill(10, *WHITE)
        self.lights_brightness = 10
        self.breath_anim = (Animation(lights_brightness=255,
                s=BrightnessPerMillis, duration=1.0, t="linear") +
            Animation(lights_brightness=10, s=BrightnessPerMillis,
                duration=1.0, t="linear"))
        self.breath_anim.repeat = True
        self.breath_anim.start(self)

    def on_lights_brightness(self, instance, value):
        App.get_running_app().arena.led_brightness(floor(value))

    def on_pre_leave(self):
        Animation.cancel_all(self)
        App.get_running_app().arena.led_brightness(255)

class UIntInput(TextInput):
    pat = re.compile('[^0-9]*')
    def insert_text(self, substring, from_undo=False):
        s = re.sub(self.pat, '', substring)
        return super(UIntInput, self).insert_text(s, from_undo=from_undo)

    def on_text(self, instance, value):
        ''' This makes sure the value is never empty and we always have something
        even if it's a zero
        '''
        if value == "":
            self.text = "0"

class DeathmatchScreen(Screen):
    def reset_screen(self, app):
        app.data.death_match.reset()
        self.ids.dm_door_drop.do_update_main_button(app.data.death_match.door_drop)
    
    data = ObjectProperty(None)
    lights_brightness = NumericProperty()

    def __init__(self, **kwargs): 
        super(DeathmatchScreen, self).__init__(**kwargs)

    def on_enter(self):
        App.get_running_app().arena.led_brightness_and_fill(10, 255, 0, 0)
        self.lights_brightness = 10
        self.breath_anim = (Animation(lights_brightness=255,
                s=BrightnessPerMillis, duration=1.0, t="linear") +
            Animation(lights_brightness=10, s=BrightnessPerMillis,
                duration=1.0, t="linear"))
        self.breath_anim.repeat = True
        self.breath_anim.start(self)

    def on_lights_brightness(self, instance, value):
        App.get_running_app().arena.led_brightness(floor(value))

    def on_pre_leave(self):
        Animation.cancel_all(self)
        App.get_running_app().arena.led_brightness(255)

    def drop_down_changed(self, instance, x):
        if x == 'Drop Both':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Never drop doors':
            self.ids.dm_door_drop_duration.disabled = True
        elif x == 'Doors Always Open':
            self.ids.dm_door_drop_duration.disabled = True
        elif x == 'Drop Player 1 Door Only':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Drop Player 2 Door Only':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Drop Random Door':
            self.ids.dm_door_drop_duration.disabled = False

    def on_battle_validation(self, app, root):
        if self.data.duration == 0:
            create_popup("death match", "Match duration cannot be zero")
            return

        if not self.ids.dm_door_drop_duration.disabled:
            if self.data.door_drop_duration == 0:
                create_popup("death match", "Door drop duration cannot be zero.\n\nIf you want them open all of the time please select that option from the drop down.")
                return

            if self.data.door_drop_duration >= self.data.duration:
                create_popup("death match", "Door drop duration must be less then the match duration.")
                return
        
        self.data.player_one_name.strip()
        if self.data.player_one_name != "":
            if len(self.data.player_one_name) >= 20:
                create_popup("death match", "Player one's name must be less then 20 charactres")
                return

        self.data.player_two_name.strip()
        if self.data.player_two_name != "":
            if len(self.data.player_two_name) >= 20:
                create_popup("death match", "Player two's name must be less then 20 charactres")
                return

        if self.data.player_one_name != "" and self.data.player_two_name != "":
            if self.data.player_one_name == self.data.player_two_name:
                create_popup("death match", "Players one and two cannot both have the same names")
                return
        # If this is disabled then we need to make sure the doors are closed before
        # we begin.
        if self.ids.dm_door_drop_duration.disabled:
            temp = app.root.get_screen('WaitForPlayers')
            temp.reset_screen("RunDeathmatch", "Player", self.name, "FIGHT!!!")
            app.root.current = 'WaitForPlayers'
            root.manager.transition.direction = 'left'
            return
        temp = app.root.get_screen('WaitForPlayersAndDoors')
        temp.reset_screen("RunDeathmatch", "Player", self.name, "FIGHT!!!")
        app.root.current = 'WaitForPlayersAndDoors'
        root.manager.transition.direction = 'left'

class CountDownTrigger:
    __doc__ = '''All runtimes given in seconds'''
    def __init__(self, arena):
        self.arena = arena
        self.stop_time = 0
        self.start_time = 0
        self.increment = 0
        self.time_increment_elapsed = 0
        self.is_active = False
        self.did_complete = False
        self.light_color = None
        self.on_complete = None
        self.number_of_lights_on = 0

    def duration(self):
        return self.start_time - self.stop_time
    
    def reset(self, completionTime, runDuration, lightCount, matchDuration, color, on_complete):
        self.is_active = False
        self.did_complete = False
        self.stop_time = completionTime
        self.start_time = completionTime + runDuration
        if self.start_time > matchDuration:
            runDuration = self.start_time - matchDuration
            self.start_time = matchDuration
        # self.increment = runDuration / lightCount
        self.number_of_lights_on = 0
        self.time_increment_elapsed = 0
        self.color = color
        self.on_complete = on_complete
    
    def on_seconds_tick(self, seconds):
        if self.did_complete:
            return
        if not self.is_active:
            if self.start_time <= seconds:
                self.is_active = True
                self.arena.set_led(0, *self.color)
                self.time_increment_elapsed += self.increment
                while self.time_increment_elapsed <= seconds:
                    self.arena.set_led(self.number_of_lights_on, *self.color)
                    self.number_of_lights_on += 1
        else:
            # turn on any lights that remain.
            while self.time_increment_elapsed <= seconds:
                self.arena.set_led(self.number_of_lights_on, *self.color)
                self.number_of_lights_on += 1
            if seconds <= self.stop_time:
                self.did_complete = True
                self.on_complete()
        
    def dump(self, name):
        print("Stats for", name)
        print("self.stop_time", self.stop_time)
        print("self.start_time", self.start_time)
        print("self.increment", self.increment)
        print("self.time_increment_elapsed", self.time_increment_elapsed)
        print("self.is_active", self.is_active)
        print("self.did_complete", self.did_complete)
        print("self.light_color", self.light_color)
        print("self.on_complete", self.on_complete)
        print("self.number_of_lights_on", self.number_of_lights_on)

    def does_overlap(self, other):
        return self.stop_time > other.stop_time and other.stop_time < self.start_time

class SelectADeathMatchWinnerScreen(Screen):
    pass

class RunDeathmatchScreen(Screen):
    data = ObjectProperty(None)
    dmData = ObjectProperty(None)
    
    # cd = count down
    cd_lights_on = NumericProperty(0)

    match_over_lights = NumericProperty(0)

    # Used to trigger the dropping of the doors
    doors_closed = BooleanProperty(False)

    def __init__(self, **kwargs): 
        self.register_event_type("on_drop_doors")
        super(RunDeathmatchScreen, self).__init__(**kwargs)
        self.match_over_trigger = CountDownTrigger(App.get_running_app().arena)
        self.door_drop_trigger = CountDownTrigger(App.get_running_app().arena)
        self.will_drop_doors = False
        self.match_over_active = False
        self.cd_animation = None
        self.ddColor = DD_YELLOW
        self.match_olver_color = MATCH_COUNT_DOWN_RED

    def reset_screen(self, app, root):
        self.dd_seconds = 0
        self.will_drop_doors = False
        self.match_over_trigger.reset(0, 30,
            App.get_running_app().get_led_count(),
            self.dmData.duration,
            self.match_olver_color,
            self.on_complete_match_count_down)

        if self.dmData.door_drop == 'Drop Both':
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Never drop doors':
            self.will_drop_doors = False
        elif self.dmData.door_drop == 'Doors Always Open':
            self.will_drop_doors = False
            App.get_running_app().open_player_1_door(1)
            App.get_running_app().open_player_2_door(1)
        elif self.dmData.door_drop == 'Drop Player 1 Door Only':
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Drop Player 2 Door Only':
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Drop Random Door':
            self.will_drop_doors = True
        else:
            print("Value for door drop = ", self.dmData.door_drop)
        if self.will_drop_doors:
            self.door_drop_trigger.reset(self. dmData.door_drop_duration,
                15, App.get_running_app().get_led_count(), self.dmData.duration,
                DD_YELLOW, self.on_completed_door_drop_count_down)


    def on_completed_door_drop_count_down(self):
        print("COmpleted door drop count down")

    def on_complete_match_count_down(self):
        print("Complete match count down")

    def cancel_count_downs(self):
        Animation.cancel_all(self)

    def on_seconds(self, instance, value):
        if self.will_drop_doors:
            if not self.door_drop_trigger.is_active:
                if value <= self.door_drop_trigger.start_time:
                    self.cd_lights_on = 0
                    self.prevTick = -1
                    self.cd_animation = Animation(cd_lights_on=int(App.get_running_app().get_led_count())-1,
                                                  duration=self.door_drop_trigger.duration(),
                                                  t="linear")
                    self.cd_animation.bind(on_complete=self.on_dd_complete)
                    self.door_drop_trigger.is_active = True
                    self.cd_animation.start(self)
                    self.ddColor = self.door_drop_trigger.color

        if not self.match_over_trigger.is_active:
            if value <= self.match_over_trigger.start_time:
                self.match_over_trigger.is_active = True
                self.match_over_prev_tick = -1
                self.match_over_lights = 0
                self.match_over_animation = Animation(match_over_lights=int(App.get_running_app().get_led_count())-1,
                                                      duration=self.match_over_trigger.duration(),
                                                      t="linear")
                self.match_over_animation.bind(on_complete=self.on_match_complete)
                self.match_over_animation.start(self)


    def on_dd_complete(self, animation, value):
        App.get_running_app().do_door_drop()

    def on_cd_lights_on(self, instance, value):
        if self.prevTick == -1:
            self.prevTick = floor(value)
            App.get_running_app().arena.set_led(self.prevTick, *self.ddColor)
        elif self.prevTick != floor(value):
            self.prevTick = int(floor(value))
            App.get_running_app().arena.set_led(self.prevTick, *self.ddColor)

    def on_match_complete(self, animation, value):
        print("Match over!")

    def on_match_over_lights(self, instance, value):
        if self.match_over_prev_tick == -1:
            self.match_over_prev_tick = floor(value)
            App.get_running_app().arena.set_led(self.match_over_prev_tick,
                *self.match_over_trigger.color)
        elif self.match_over_prev_tick != floor(value):
            self.match_over_prev_tick = int(floor(value))
            App.get_running_app().arena.set_led(self.match_over_prev_tick,
                *self.match_over_trigger.color)


    def on_data(self, instance, value):
        pass

    def on_drop_doors(self):
        pass

    def on_pre_enter(self):
        pass

    def on_leave(self):
        pass


class ErrorMessagePopUp(Popup):
    message = StringProperty("")
    def __init__(self, **kwargs):
        super(ErrorMessagePopUp, self).__init__(**kwargs)

def create_popup(screenName, msg):
    ErrorMessagePopUp(title='Invalid {0} configuration'.format(screenName),
        message=msg,
        size_hint=(None, None), size=(400, 400),
        auto_dismiss=False).open()

class SoccerScreen(Screen):
    data = ObjectProperty(None)
    lights_brightness = NumericProperty()


    def __init__(self, **kwargs):
        super(SoccerScreen, self).__init__(**kwargs)
    
    def on_enter(self):
        App.get_running_app().arena.led_brightness_and_fill(10, *SOCCER_GREEN)
        self.lights_brightness = 10
        self.breath_anim = (Animation(lights_brightness=255,
                s=BrightnessPerMillis, duration=1.0, t="linear") +
            Animation(lights_brightness=10, s=BrightnessPerMillis,
                duration=1.0, t="linear"))
        self.breath_anim.repeat = True
        self.breath_anim.start(self)

    def on_lights_brightness(self, instance, value):
        App.get_running_app().arena.led_brightness(floor(value))

    def on_pre_leave(self):
        Animation.cancel_all(self)
        App.get_running_app().arena.led_brightness(255)

    def reset_screen(self, app):
        app.data.soccer_match.reset()

    def on_match_validation(self, app, root):
        if self.data.duration == 0:
            create_popup("soccer match", "Match duration cannot be zero")
            return

        if self.data.points == 0:
            create_popup("soccer match", "Number of match points cannot be zero.")
            return

        self.data.team_one_name.strip()
        if self.data.team_one_name != "":
            if len(self.data.team_one_name) >= 20:
                create_popup("soccermatch", "Player one's name must be less then 20 charactres")
                return

        self.data.team_two_name.strip()
        if self.data.team_two_name != "":
            if len(self.data.team_two_name) >= 20:
                create_popup("soccer match", "Player two's name must be less then 20 charactres")
                return

        if self.data.team_one_name != "" and self.data.team_two_name != "":
            if self.data.team_one_name == self.data.team_two_name:
                create_popup("soccer match", "teams one and two cannot both have the same names")
                return
        app.data.run_soccer_match.team_one_score = 0
        app.data.run_soccer_match.team_two_score = 0
        temp = app.root.get_screen('WaitForPlayers')
        temp.reset_screen("RunSoccer", "Team", self.name, "GO!!!")
        app.root.current = 'WaitForPlayers'
        root.manager.transition.direction = 'left'


class ManualSoccerScoreAdjustmentScreen(Screen):
    pass

class RunSoccerScreen(Screen):
    data = ObjectProperty(None, allownone=False)
    PauseGameStr = "Pause\nGame"
    ResumeGameStr = "Resume\nGame"
    pause_play_button_text = StringProperty("Pause\nGame")
    cd_lights = NumericProperty()
    
    def __init__(self, **kwargs): 
        self.register_event_type("on_max_score_reached")
        super(RunSoccerScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        App.get_running_app().open_player_1_door(1)
        App.get_running_app().open_player_2_door(1)


    def on_data(self, instance, value):
        self.data.bind(team_one_score=self.on_team_one_scored,
                       team_two_score=self.on_team_one_scored)
    
    def on_pause_play_button_text(self, instance, value):
        pass

    def play_pause_pressed(self):
        if self.pause_play_button_text == RunSoccerScreen.PauseGameStr:
            self.ids.countDownClock.pause()
        else:
            self.ids.countDownClock.resume()
            self.pause_play_button_text = RunSoccerScreen.PauseGameStr

    def pause_count_down(self):
        print("Paused count down")
        Animation.cancel_all(self)

    def resume_count_down(self):
        print("Resuemed count down?")
        duration = self.ids.countDownClock.seconds
        self.prev_light = -1
        if duration <= 30:
            self.cd_anim = (Animation(
                    cd_lights=int(App.get_running_app().get_led_count())-1,
                    duration=duration))
        else:
            self.cd_anim = (Animation(duration=duration-30) + Animation(
                    cd_lights=int(App.get_running_app().get_led_count())-1,
                    duration=30))
        self.cd_anim.start(self)
        
    def on_cd_lights(self, instance, value):
        if self.prev_light == -1:
            self.prev_light = floor(value)
            App.get_running_app().arena.led_n_fill(*MATCH_COUNT_DOWN_RED,
                0, self.prev_light + 1)

        elif self.prev_light != floor(value):
            self.prev_light = int(floor(value))
            App.get_running_app().arena.set_led(self.prev_light,
                *MATCH_COUNT_DOWN_RED)

    def on_max_score_reached(self):
        pass

    def on_team_one_scored(self, instance, value):
        if self.pause_play_button_text == RunSoccerScreen.PauseGameStr:
            self.ids.countDownClock.pause()

        if int(value) == int(self.smData.points):
            self.dispatch("on_max_score_reached")

    def on_team_two_scored(self, instance, value):
        if self.pause_play_button_text == RunSoccerScreen.PauseGameStr:
            self.ids.countDownClock.pause()
        if int(value) == int(self.smData.points):
            self.dispatch("on_max_score_reached")

    def get_winning_team_name(self):
        if self.data.team_one_score == self.data.team_two_score:
            App.get_running_app().lights_soccer_match_tie()
            return "NO BODY"
        if self.data.team_one_score > self.data.team_two_score:
            App.get_running_app().lights_soccer_team_1_wins()
            return self.smData.get_team_one_name()
        else:
            App.get_running_app().lights_soccer_team_2_wins()
            return self.smData.get_team_two_name()

class RunSoccerSubScreenSelector(ScreenManager):
    pass

class DMDecisionScreen(Screen):
    pass


class WaitForPlayers(Screen):
    next_screen_after_ready = StringProperty()
    player_or_team = StringProperty("Player")
    previous_screen = StringProperty()
    count_down_word = StringProperty()
    player_1_ready = BooleanProperty(False)
    player_2_ready = BooleanProperty(False)

    is_active = BooleanProperty(False)

    def __init__(self, **kwargs): 
        self.register_event_type("on_everyone_ready")
        super(WaitForPlayers, self).__init__(**kwargs)
        App.get_running_app().arena.player_1.bind(
            ready_button=self.on_player_1_pressed_ready_button)
        App.get_running_app().arena.player_2.bind(
            ready_button=self.on_player_2_pressed_ready_button)

    def on_player_1_pressed_ready_button(self, instance, value):
        if self.is_active:
            self.player_1_ready = True

    def on_player_2_pressed_ready_button(self, instance, value):
        if self.is_active:
            self.player_2_ready = True

    def reset_screen(self, nextScreen, POrT, previousScreen, word):
        self.next_screen_after_ready = nextScreen
        self.player_or_team = POrT
        self.previous_screen = previousScreen
        self.count_down_word = word
        self.player_1_ready = False
        self.player_2_ready = False

    def checkForReadyState(self):
        if (self.player_1_ready and self.player_2_ready):
            self.dispatch("on_everyone_ready")

    def on_pre_enter(self):
        self.player_1_ready = App.get_running_app().arena.player_1.ready_button
        self.player_2_ready = App.get_running_app().arena.player_2.ready_button

    def on_next_screen_after_ready(self, instance, value):
        pass

    def on_everyone_ready(self):
        pass

    def on_count_down_word(self, instance, value):
        pass

    def on_player_1_ready(self, instance, value):
        if value:
            App.get_running_app().lights_player_1_ready()
        self.checkForReadyState()

    def on_player_2_ready(self, instance, value):
        if value:
            App.get_running_app().lights_player_2_ready()
        self.checkForReadyState()

class BGDoorLabel(Label):
    bg_color = ListProperty([0,0,0,0])

RedBGColorList = [1, 0, 0, 1]
GreenBGColorList = [0, 1, 0, 1]

class WaitForPlayersAndDoors(Screen):
    next_screen_after_ready = StringProperty()
    player_or_team = StringProperty("Player")
    previous_screen = StringProperty()
    count_down_word = StringProperty()
    player_1_ready = BooleanProperty(False)
    player_2_ready = BooleanProperty(False)
    player_1_door_closed = BooleanProperty(False)
    player_2_door_closed = BooleanProperty(False)
    is_active = BooleanProperty(False)

    def __init__(self, **kwargs): 
        self.register_event_type("on_everyone_ready")
        super(WaitForPlayersAndDoors, self).__init__(**kwargs)
        App.get_running_app().arena.player_1.bind(
            ready_button=self.on_player_1_pressed_ready_button,
            door_button=self.on_player_1_closed_door)
        App.get_running_app().arena.player_2.bind(
            ready_button=self.on_player_2_pressed_ready_button,
            door_button=self.on_player_2_closed_door)

    def on_leave(self):
        Animation.cancel_all(self.ids.player_1_door_label)
        Animation.cancel_all(self.ids.player_2_door_label)
        
    def on_player_1_pressed_ready_button(self, instance, value):
        if self.is_active and self.player_1_door_closed:
            self.player_1_ready_button_pressed()

    def on_player_2_pressed_ready_button(self, instance, value):
        if self.is_active and self.player_2_door_closed:
            self.player_2_ready_button_pressed()

    def on_player_1_closed_door(self, instance, value):
        if self.is_active:
            self.player_1_door_closed = value
            if self.player_1_door_closed:
                App.get_running_app().close_player_1_door(1)
            else:
                App.get_running_app().open_player_1_door(1)

    def on_player_2_closed_door(self, instance, value):
        if self.is_active:
            self.player_2_door_closed = value
            if self.player_2_door_closed:
                App.get_running_app().close_player_2_door(1)
            else:
                App.get_running_app().open_player_2_door(1)

    def reset_screen(self, nextScreen, POrT, previousScreen, word):
        self.next_screen_after_ready = nextScreen
        self.player_or_team = POrT
        self.previous_screen = previousScreen
        self.count_down_word = word
        self.player_1_ready = False
        self.player_2_ready = False
        self.player_1_door_closed = False
        self.player_2_door_closed = False

    def on_enter(self):
        self.player_1_ready = App.get_running_app().arena.player_1.ready_button
        self.player_2_ready = App.get_running_app().arena.player_2.ready_button
        self.player_1_door_closed = App.get_running_app().arena.player_1.door_button
        self.player_2_door_closed = App.get_running_app().arena.player_2.door_button
        self.on_player_1_door_closed(None, self.player_1_door_closed)
        self.on_player_2_door_closed(None, self.player_2_door_closed)
        if self.player_1_door_closed:
            App.get_running_app().close_player_1_door(1)

        if self.player_2_door_closed:
            App.get_running_app().close_player_2_door(1)

    def TriggerLateScreenChange(self, Key, *largs):
        self.dispatch("on_everyone_ready")

    def checkForReadyState(self):
        if (self.player_1_ready and self.player_2_ready
                and self.player_2_door_closed and self.player_2_door_closed):
            Clock.schedule_once(self.TriggerLateScreenChange, 0.5 )
            

    def on_next_screen_after_ready(self, instance, value):
        pass

    def on_everyone_ready(self):
        pass

    def on_count_down_word(self, instance, value):
        pass

    def player_1_ready_button_pressed(self):
        if self.player_1_door_closed:
            self.player_1_ready = True

    def player_2_ready_button_pressed(self):
        if self.player_2_door_closed:
            self.player_2_ready = True

    def on_player_1_ready(self, instance, value):
        if value:
            if not self.player_1_door_closed:
                App.get_running_app().lights_player_1_needs_to_close_door(self.ids.player_1_door_label)
                self.player_1_ready = False
                return
            Animation.cancel_all(self.ids.player_1_door_label)
            App.get_running_app().lights_player_1_ready()
            self.checkForReadyState()
        self.checkForReadyState()

    def on_player_2_ready(self, instance, value):
        if value:
            if not self.player_2_door_closed:
                App.get_running_app().lights_player_2_needs_to_close_door(self.ids.player_2_door_label)
                self.player_2_ready = False
                return
            Animation.cancel_all(self.ids.player_2_door_label)
            App.get_running_app().lights_player_2_ready()
            self.checkForReadyState()
        else:
            return

    def on_player_1_door_closed(self, instance, value):
        if value:
            self.ids.player_1_door_label.bg_color = GreenBGColorList
            App.get_running_app().lights_player_1_door_closed()
        else:
            self.ids.player_1_door_label.bg_color = RedBGColorList
            self.player_1_ready = False
            App.get_running_app().lights_player_1_door_opened()
            

    def on_player_2_door_closed(self, instance, value):
        if value:
            self.ids.player_2_door_label.bg_color = GreenBGColorList
            App.get_running_app().lights_player_2_door_closed()
        else:
            self.ids.player_2_door_label.bg_color = RedBGColorList
            self.player_2_ready = False
            App.get_running_app().lights_player_2_door_opened()


class ScreenManagement(ScreenManager):
    pass

class CustomDropDown(DropDown): 
    pass

class CountDownClockLabel(Label):
    Timer_idle = 0
    Timer_running = 1
    Timer_paused = 2
    Timer_cancelled = 3
    Timer_time_expired = 4
    seconds = NumericProperty(1)
    def __init__(self, **kwargs):
        self.register_event_type("on_timer_idle")
        self.register_event_type("on_start")
        self.register_event_type("on_pause")
        self.register_event_type("on_resume")
        self.register_event_type("on_cancelled")
        self.register_event_type("on_time_expired")
        self.state = CountDownClockLabel.Timer_idle
        super(CountDownClockLabel, self).__init__(**kwargs)
        self.parallel_animation_cb = None

    def finish_callback(self, animation, incr_crude_clock):
        self.color = [1, 1, 1, 0]
        incr_crude_clock.text = "FINISHED"
        self.dispatch("on_time_expired")

    def start(self, execTime, ParallelAnimationCB = None):
        Animation.cancel_all(self)  # stop any current animations
        self.color = [1,1,1,1]
        self.seconds = execTime
        self.on_seconds(None, None)
        self.anim = Animation(seconds=0, duration=self.seconds)
        self.anim.bind(on_complete=self.finish_callback)
        if self.parallel_animation_cb is not None:
            self.parallel_animation_cb = ParallelAnimationCB
            self.anim &= ParallelAnimationCB(self, self.seconds)
        self._change_state(CountDownClockLabel.Timer_running)
        self.anim.start(self)
    
    def pause(self):
        self._change_state(CountDownClockLabel.Timer_paused)
        Animation.cancel_all(self)
        self.color = [1,1,1,0]
        self.anim = Animation(color=[1,1,1,0], duration=0.1) + Animation(color=[1,1,1,0], duration=0.5)
        self.anim += Animation(color=[1,1,1,1], duration=0.1) + Animation(color=[1,1,1,1], duration=0.5)
        self.anim.repeat = True
        self.anim.start(self)

    def resume(self):
        self._change_state(CountDownClockLabel.Timer_running)
        Animation.cancel_all(self)
        self.color = [1,1,1,1]
        self.on_seconds(None, None)
        self.anim = Animation(seconds=0, duration=self.seconds)
        self.anim.bind(on_complete=self.finish_callback)
        if self.parallel_animation_cb is not None:
            self.parallel_animation_cb = ParallelAnimationCB
            self.anim &= ParallelAnimationCB(self, self.seconds)
        self._change_state(CountDownClockLabel.Timer_running)
        self.anim.start(self)
    
    def cancel(self):
        self._change_state(CountDownClockLabel.Timer_cancelled)
        Animation.cancel_all(self)
        self.seconds = 0

    def on_seconds(self, instance, value):
        self.text = str(round(self.seconds, 1))

    def _change_state(self, nextState):
        if self.state == CountDownClockLabel.Timer_idle:
            if nextState == CountDownClockLabel.Timer_idle:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_running:
                self.state = nextState
                self.dispatch("on_start")
            elif nextState == CountDownClockLabel.Timer_paused:
                self.state = nextState
                self.dispatch("on_start")
                self.dispatch("on_pause")
            elif nextState == CountDownClockLabel.Timer_cancelled:
                self.state = nextState
                self.dispatch("on_start")
                self.dispatch("on_cancelled")
            elif nextState == CountDownClockLabel.Timer_time_expired:
                self.state = nextState
                self.dispatch("on_start")
                self.dispatch("on_time_expired")
            else:
                raise Exception("Invalid State from idle -> {0}".format(nextState))
        elif self.state == CountDownClockLabel.Timer_running:
            if nextState == CountDownClockLabel.Timer_idle:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_running:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_paused:
                self.state = nextState
                self.dispatch("on_pause")
            elif nextState == CountDownClockLabel.Timer_cancelled:
                self.state = nextState
                self.dispatch("on_cancelled")
            elif nextState == CountDownClockLabel.Timer_time_expired:
                self.state = nextState
                self.dispatch("on_time_expired")
            else:
                raise Exception("Invalid State from running -> {0}".format(nextState))
            pass
        elif self.state == CountDownClockLabel.Timer_paused:
            if nextState == CountDownClockLabel.Timer_idle:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_running:
                self.state = nextState
                self.dispatch("on_resume")
            elif nextState == CountDownClockLabel.Timer_paused:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_cancelled:
                self.state = nextState
                self.dispatch("on_cancelled")
            elif nextState == CountDownClockLabel.Timer_time_expired:
                self.state = nextState
                self.dispatch("on_time_expired")
            else:
                raise Exception("Invalid State from paused -> {0}".format(nextState))
            pass
        elif self.state == CountDownClockLabel.Timer_cancelled:

            if nextState == CountDownClockLabel.Timer_idle:
                self.state = nextState
                self.dispatch("on_timer_idle")
            elif nextState == CountDownClockLabel.Timer_running:
                raise Exception ("Invalid cancelled -> running")
            elif nextState == CountDownClockLabel.Timer_paused:
                raise Exception ("Invalid cancelled -> paused")
            elif nextState == CountDownClockLabel.Timer_cancelled:
                self.state = nextState
            elif nextState == CountDownClockLabel.Timer_time_expired:
                raise Exception ("Invalid cancelled -> expired")
            else:
                raise Exception("Invalid State from cancelled -> {0}".format(nextState))
            pass
        elif self.state == CountDownClockLabel.Timer_time_expired:
            if nextState == CountDownClockLabel.Timer_idle:
                self.state = nextState
                self.dispatch("on_timer_idle")
            elif nextState == CountDownClockLabel.Timer_running:
                raise Exception ("Invalid expired -> running")
            elif nextState == CountDownClockLabel.Timer_paused:
                raise Exception ("Invalid expired -> paused")
            elif nextState == CountDownClockLabel.Timer_cancelled:
                raise Exception ("Invalid expired -> cancelled")
            elif nextState == CountDownClockLabel.Timer_time_expired:
                self.state = nextState
            else:
                raise Exception("Invalid State from time expired -> {0}".format(nextState))
            pass
        else:
            raise Exception("Invalid current state = {0}".fomrat(self.state))

    def on_timer_idle(self):
        pass
    
    def on_start(self):
        pass
    
    def on_pause(self):
        pass
    
    def on_resume(self):
        pass

    def on_cancelled(self):
        self._change_state(CountDownClockLabel.Timer_idle)

    def on_time_expired(self):
        self._change_state(CountDownClockLabel.Timer_idle)

class VictoryScreen(Screen):
    victor_text = StringProperty()
    next_screen = StringProperty()

    def reset_screen(self, VictoryText, NextScreen):
        self.victor_text = VictoryText
        self.next_screen = NextScreen

    def on_enter(self):
        pass



class FadeTicker(Label):
    seconds = NumericProperty(3)
    final_word = StringProperty("FIGHT!!!")

    led_brightness = NumericProperty(10)

    def __init__(self, **kwargs): 
        self.register_event_type("on_ready")
        super(FadeTicker, self).__init__(**kwargs)
    def on_led_brightness(self, instance, value):
        App.get_running_app().arena.led_brightness(floor(value))

    # FIXME: Color order is wrong.
    def finish_callback_3(self, animation, Ticker):
        App.get_running_app().arena.led_brightness_and_fill(10, *STOP_LIGHT_ORANGE)
        self._do_animation(2, self.finish_callback_2)

    def finish_callback_2(self, animation, Ticker):
        App.get_running_app().arena.led_brightness_and_fill(10, *STOP_LIGHT_YELLOW)
        self._do_animation(1, self.finish_callback_1)

    def finish_callback_1(self, animation, Ticker):
        App.get_running_app().arena.led_brightness_and_fill(10, *STOP_LIGHT_GREEN)
        self.led_brightness = 10
        Ticker.text = self.final_word
        self.color = [1,1,1,1]
        self.anim = Animation(color=[1,1,1,1], duration=0.3)
        self.anim &= Animation(led_brightness=255, s=BrightnessPerMillis)
        self.anim.bind(on_complete=self.complete_count_down)
        self.anim.start(self)

    def complete_count_down(self, animation, Ticker):
        self.dispatch("on_ready")

    def _do_animation(self, nextValue, nextCB):
        self.led_brightness = 10
        self.seconds = nextValue
        self.color = [1,1,1,0]
        self.anim = Animation(color=[1,1,1,0.7], duration=1.0)
        self.anim &= Animation(led_brightness=255, s=BrightnessPerMillis)
        self.on_seconds(None, None)
        self.anim.bind(on_complete=nextCB)
        self.anim.start(self)

    def start(self):
        Animation.cancel_all(self)
        App.get_running_app().arena.led_brightness_and_fill(10, *STOP_LIGHT_RED)
        self._do_animation(3, self.finish_callback_3)

    def on_seconds(self, instance, value):
        self.text = str(int(self.seconds))

    def cancel(self):
        Animation.cancel_all(self)
        App.get_running_app().arena.led_brightness(255)
        
    def on_ready(self):
        pass

class CountDownScreen(Screen):
    next = StringProperty()
    previous = StringProperty()
    final_word = StringProperty()

    def reset_screen(self, nextScreen, previousScreen, finalWord):
        self.next = nextScreen
        self.previous = previousScreen
        self.final_word = finalWord

    def on_next(self, instance, value):
        pass

    def on_previous(self, instance, value):
        pass

    def on_final_word(self, instance, value):
        pass

class DropdownDemo(GridLayout): 
    select = StringProperty("Door Drop Mode")
    def do_update_main_button(self, x):
        setattr(self.mainbutton, 'text', x)
        self.select = x
    def __init__(self, **kwargs): 
        super(DropdownDemo, self).__init__(**kwargs) 
        self.labelDispalay = Label(text='Door Drop Mode', font_size=30)
        self.add_widget(self.labelDispalay) 
        self.dropdown = CustomDropDown()
        self.mainbutton = Button(text ='Drop Both')

        self.add_widget(self.mainbutton) 
        self.mainbutton.bind(on_release = self.dropdown.open) 

        def update_main_button(instance, x):
            setattr(self.mainbutton, 'text', x)
            self.select = x
        self.dropdown.bind(on_select = update_main_button)

    def on_select(self, instance, x):
        pass



HWProp = HardwareInterface
if platform.system() != 'Windows':
    from arena.physicalarena import Arena
    HWProp = Arena

# def exit_media_app(app):
#     app.stop()

class MainApp(App):
    data = BBViewModelProp()
    arena = HWProp()

    def parse_int_or_zero(self, str_val):
        try:
            return int(str_val)
        except:
            return 0

    def __init__(self, **kwargs): 
        # self.media_q = mp.Queue()
        # self.logging_q = mp.Queue()
        # self.media_p = mp.Process(target=run_media_subprocess, args=(self.media_q, self.logging_q))
        # self.media_p.start()
        self.media_process = subp.Popen("python3 app.py", cwd="mediadisplay/", shell=True)
        
        self.whiteLight = (255, 255, 255)
        super(MainApp, self).__init__(**kwargs)
        self.arena.init()

    def on_stop(self):
        self.arena.shutdown_connection()
        self.media_process.kill()
        # self.send_media_function(exit_media_app)
        # self.media_p.join()

    def send_media_function(self, func):
        self.media_q.put_nowait(pickle.dumps(func))

    def build(self):
        root_widget = ScreenManagement()
        return root_widget

    #
    def lights_off(self):
        self.arena.led_brightness_and_fill(0, 0, 0, 0)

    #
    def lights_waiting_for_players(self):
        self.arena.led_brightness_and_fill(255, *YELLOW)

    #
    def lights_player_1_ready(self):
        self.arena.led_player_1_lights(*PLAYER_1_COLOR)

    #
    def lights_player_2_ready(self):
        self.arena.led_player_2_lights(*PLAYER_2_COLOR)

    #
    def lights_player_1_door_closed(self):
        self.arena.led_player_1_lights(*PINK)

    #
    def lights_player_1_door_opened(self):
        self.arena.led_player_1_lights(*YELLOW)

    #
    def lights_player_2_door_closed(self):
        self.arena.led_player_2_lights(*PURPLE)

    #
    def lights_player_2_door_opened(self):
        self.arena.led_player_2_lights(*YELLOW)

    #
    def lights_player_1_needs_to_close_door(self, WidgetToAnimate):
        pass

    #
    def lights_player_2_needs_to_close_door(self, WidgetToAnimate):
        pass

    #
    def lights_soccer_team_1_scored(self):
        pass

    #
    def lights_soccer_team_2_scored(self):
        pass

    #
    def lights_soccer_team_1_wins(self):
        self.arena.led_brightness_and_fill(255, *PLAYER_1_COLOR)

    #
    def lights_soccer_team_2_wins(self):
        self.arena.led_brightness_and_fill(255, *PLAYER_2_COLOR)

    #
    def lights_dm_player_1_wins(self):
        self.arena.led_brightness_and_fill(255, *PLAYER_1_COLOR)

    #
    def lights_dm_player_2_wins(self):
        self.arena.led_brightness_and_fill(255, *PLAYER_2_COLOR)

    #
    def lights_soccer_match_tie(self):
        self.arena.led_brightness_and_fill(255, *ORANGE)

    #
    def lights_death_match(self):
        pass

    #
    def lights_soccer_match(self):
        pass   

    #
    def get_led_count(self):
        return self.arena.get_led_count()

    def close_player_1_door(self):
        self.arena.close_player_1_door()
        Clock.schedule_once(self.door_stopper_p1, 1)

    def close_player_2_door(self):
        self.arena.close_player_2_door()
        Clock.schedule_once(self.door_stopper_p2, 1)

    def open_player_1_door(self, duration):
        self.arena.open_player_1_door()
        Clock.schedule_once(self.door_stopper_p1, duration)

    def open_player_2_door(self, duration):
        self.arena.open_player_2_door()
        Clock.schedule_once(self.door_stopper_p2, duration)

    def close_player_1_door(self, duration):
        self.arena.close_player_1_door()
        Clock.schedule_once(self.door_stopper_p1, duration)

    def close_player_2_door(self, duration):
        self.arena.close_player_2_door()
        Clock.schedule_once(self.door_stopper_p2, duration)

    def door_stopper_p1(self, val):
        self.arena.stop_player_1_door()

    def door_stopper_p2(self, val):
        self.arena.stop_player_2_door()
    #
    def do_door_drop(self):
        if self.data.death_match.door_drop == 'Drop Both':
            self.open_player_1_door(1)
            self.open_player_2_door(1)
        elif self.data.death_match.door_drop == 'Never drop doors':
            pass
        elif self.data.death_match.door_drop == 'Doors Always Open':
            pass
        elif self.data.death_match.door_drop == 'Drop Player 1 Door Only':
            self.open_player_1_door(1)
        elif self.data.death_match.door_drop == 'Drop Player 2 Door Only':
            self.open_player_2_door(1)
        elif self.data.death_match.door_drop == 'Drop Random Door':
            if (random.randint() % 2) == 1:
                self.open_player_1_door(1)
            else:
                self.open_player_2_door(1)



if __name__ == '__main__':
    MainApp().run()