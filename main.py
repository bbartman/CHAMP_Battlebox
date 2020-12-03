from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
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

import platform, re


class MainScreen(Screen):
    pass

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

    def __init__(self, **kwargs): 
        super(DeathmatchScreen, self).__init__(**kwargs)

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
    def __init__(self, completionTime, runDuration):
        pass

class RunDeathmatchScreen(Screen):
    data = ObjectProperty(None)
    dmData = ObjectProperty(None)

    # The computed amount of time in seconds
    # until the door should drop.
    # time_stamp_to_drop_doors_at = NumericProperty(30)
    # time_stamp_to_start_count_down_lights = NumericProperty(30)
    # time_stamp_match_over_count_down_start = NumericProperty(30)
    # disable_door_drop_count_down = BooleanProperty(False)

    # Used to track if we will drop the doors during this match
    # will_drop_doors = BooleanProperty(False)

    # Used to trigger the dropping of the doors
    # doors_dropped = BooleanProperty(False)

    # door_drop_count_down_increment = NumericProperty(1)
    # match_over_count_down_increment = NumericProperty(1)

    def __init__(self, **kwargs): 
        self.register_event_type("on_drop_doors")
        super(RunDeathmatchScreen, self).__init__(**kwargs)

    def reset_screen(self, app, root):
        print("Called reset screen!")
        self.time_stamp_to_drop_doors_at = 0
        self.time_stamp_to_start_count_down_lights = 0
        self.time_stamp_match_over_count_down_start = 30
        self.disable_door_drop_count_down = 0
        self.will_drop_doors = False
        self.doors_dropped = False
        self.door_drop_count_down_increment = 1
        self.match_over_count_down_increment = 1
        self.doors_dropped = False
        self.disable_door_drop_count_down = False
        # Calcuating information for count down timer.
        endingTime = self.time_stamp_match_over_count_down_start
        self.time_stamp_match_over_count_down_start = 30
        self.time_stamp_match_over_count_down_start = min([self.dmData.duration,
                                                            self.time_stamp_match_over_count_down_start])
        totalLightTime = self.time_stamp_match_over_count_down_start - endingTime
        self.match_over_count_down_increment = totalLightTime/App.get_running_app().get_led_count()
        print("time_stamp_match_over_count_down_start = ", self.time_stamp_match_over_count_down_start)
        print("Value for door drop = ", self.dmData.door_drop)
        if self.dmData.door_drop == 'Drop Both':
            print("We will drop both?!")
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Never drop doors':
            self.will_drop_doors = False
        elif self.dmData.door_drop == 'Doors Always Open':
            self.will_drop_doors = False
        elif self.dmData.door_drop == 'Drop Player 1 Door Only':
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Drop Player 2 Door Only':
            self.will_drop_doors = True
        elif self.dmData.door_drop == 'Drop Random Door':
            self.will_drop_doors = True
        else:
            print("Value for door drop = ", self.dmData.door_drop)
        if self.will_drop_doors:
            self.time_stamp_to_drop_doors_at = self.dmData.duration - self.dmData.door_drop_duration
            print("self.time_stamp_to_drop_doors_at = ", self.time_stamp_to_drop_doors_at)

            # Checking if the match and door drop timer will overlap.
            # if they do simply ignore things. 
            self.time_stamp_to_start_count_down_lights = self.time_stamp_to_drop_doors_at + 15
            if self.time_stamp_to_start_count_down_lights >= self.time_stamp_match_over_count_down_start:
                Logger.info("We can't show door drop countdown, end of match and door drop overlap")
                self.disable_door_drop_count_down = True
                return

            self.time_stamp_to_start_count_down_lights = min([self.dmData.duration,
                                                              self.time_stamp_to_start_count_down_lights])
            # Handling things as time per light, NOT lights per second.
            totalLightTime = self.time_stamp_to_start_count_down_lights - self.time_stamp_to_drop_doors_at
            self.door_drop_count_down_increment = totalLightTime/App.get_running_app().get_led_count()
            self.lights_count_down_active = False
            print("Will drop doors")


    def on_seconds(self, instance, value):
        self.text = str(round(self.seconds, 1))
        if self.will_drop_doors:
            if not self.lights_count_down_active:
                if self.seconds <= self.time_stamp_to_start_count_down_lights:
                    print("Lights On")
                    self.lights_count_down_active = True
            else:
                if self.seconds <= self.time_stamp_to_drop_doors_at:
                    print("Lights Completed")
                    self.lights_count_down_active = False
            
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
    def __init__(self, **kwargs):
        super(SoccerScreen, self).__init__(**kwargs)
        
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

    
    def __init__(self, **kwargs): 
        self.register_event_type("on_max_score_reached")
        super(RunSoccerScreen, self).__init__(**kwargs)

    def on_data(self, instance, value):
        self.data.bind(team_one_score=self.on_team_one_scored,
                       team_two_score=self.on_team_one_scored)
    
    def on_pause_play_button_text(self, instance, value):
        pass

    def play_pause_pressed(self):
        if self.pause_play_button_text == RunSoccerScreen.PauseGameStr:
            App.get_running_app().lights_game_paused()
            self.ids.countDownClock.pause()
        else:
            App.get_running_app().lights_soccer()
            self.ids.countDownClock.resume()
            self.pause_play_button_text = RunSoccerScreen.PauseGameStr

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

    needs_doors_closed = BooleanProperty(False)
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
    needs_doors_closed = BooleanProperty(False)
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

    def on_player_1_pressed_ready_button(self, instance, value):
        if self.is_active and self.player_1_door_closed:
            self.player_1_ready_button_pressed()

    def on_player_2_pressed_ready_button(self, instance, value):
        if self.is_active and self.player_2_door_closed:
            self.player_2_ready_button_pressed()

    def on_player_1_closed_door(self, instance, value):
        if self.is_active:
            self.player_1_door_closed = value

    def on_player_2_closed_door(self, instance, value):
        if self.is_active:
            self.player_2_door_closed = value

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

    def checkForReadyState(self):
        if (self.player_1_ready and self.player_2_ready
                and self.player_2_door_closed and self.player_2_door_closed):
            self.dispatch("on_everyone_ready")

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
                App.get_running_app().lights_player_1_needs_to_close_door()
                self.player_1_ready = False
                return
            App.get_running_app().lights_player_1_ready()
            self.checkForReadyState()
        self.checkForReadyState()

    def on_player_2_ready(self, instance, value):
        if value:
            if not self.player_2_door_closed:
                App.get_running_app().lights_player_2_needs_to_close_door()
                self.player_2_ready = False
                return
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
            

    def on_player_2_door_closed(self, instance, value):
        if value:
            self.ids.player_2_door_label.bg_color = GreenBGColorList
            App.get_running_app().lights_player_2_door_closed()
        else:
            self.ids.player_2_door_label.bg_color = RedBGColorList
            self.player_2_ready = False


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


    def finish_callback(self, animation, incr_crude_clock):
        self.color = [1,1,1,0]
        incr_crude_clock.text = "FINISHED"
        self.dispatch("on_time_expired")

    def start(self, execTime):
        Animation.cancel_all(self)  # stop any current animations
        self.color = [1,1,1,1]
        self.seconds = execTime
        self.on_seconds(None, None)
        self.anim = Animation(seconds=0, duration=self.seconds)
        self.anim.bind(on_complete=self.finish_callback)
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

class FadeTicker(Label):
    seconds = NumericProperty(3)
    final_word = StringProperty("FIGHT!!!")

    def __init__(self, **kwargs): 
        self.register_event_type("on_ready")
        super(FadeTicker, self).__init__(**kwargs)

    def finish_callback_1(self, animation, Ticker):
        App.get_running_app().lights_count_down_screen_2()
        self._do_animation(2, self.finish_callback_2)

    def finish_callback_2(self, animation, Ticker):
        App.get_running_app().lights_count_down_screen_1()
        self._do_animation(1, self.finish_callback_3)

    def finish_callback_3(self, animation, Ticker):
        Ticker.text = self.final_word
        self.color = [1,1,1,1]
        self.anim = Animation(color=[1,1,1,1], duration=0.3)
        self.anim.bind(on_complete=self.complete_count_down)
        self.anim.start(self)

    def complete_count_down(self, animation, Ticker):
        App.get_running_app().lights_count_down_screen_go()
        self.dispatch("on_ready")

    def _do_animation(self, nextValue, nextCB):
        self.seconds = nextValue
        self.color = [1,1,1,0]
        self.anim = Animation(color=[1,1,1,0.7], duration=1.0)
        self.on_seconds(None, None)
        self.anim.bind(on_complete=nextCB)
        self.anim.start(self)

    def start(self):
        Animation.cancel_all(self)
        App.get_running_app().lights_count_down_screen_3()
        self._do_animation(3, self.finish_callback_1)

    def on_seconds(self, instance, value):
        self.text = str(int(self.seconds))

    def cancel(self):
        Animation.cancel_all(self)
        
    def on_ready(self):
        pass

HWProp = HardwareInterface
if platform.system() != 'Windows':
    from arena.physicalarena import Arena
    HWProp = Arena
    # TODO: Change the type here so that if I'm not in windows
    # I can change behavior
    # pass

class BreathingLights:
    def __init__(self, hw, **kwargs):
        assert hw != None, "Missing hardware"
        self.hardware = hw
        self.running = False
        self.increasing = True
        self.min = kwargs.get("min", 0.3)
        self.max = kwargs.get("max", 0.9)
        self.color = kwargs.get("color", (255, 255, 255))
        assert self.min != self.max, "min and max cannot be the same value."
        assert self.min < self.max, "Min must be less than max."
        assert self.min > 0, "Min must be greater than zero"
        assert self.max <= 1.0, "Max must be less than or equal to 1"
        if "increment" in kwargs:
            self.increment = kwargs.get("increment", 0.1)
        elif "cycle_time" in kwargs:
            # divide by 10 because we have to make sure that we increment every
            # 1 tenth of a second and the cycle time should be in seconds.
            self.increment = ((self.max - self.min)/kwargs["cycle_time"])/10
        else:
            self.increment = 0.1
            
        
    def start(self, color=None):
        self.running = True
        if color == None:
            self.hardware.led_fill(*self.color)
        else:
            self.color = color
            self.hardware.led_fill(*color)
        self.value = self.min
        Clock.schedule_interval(self.breathing_brightness_cb, 0.1)

    def stop(self):
        self.running = False

    def breathing_brightness_cb(self, time_delta):
        if self.running:
            if self.increasing:
                self.value += self.increment
                if self.value >= self.max:
                    self.increasing = False
            else:
                self.value -= self.increment
                if self.value <= self.min:
                    self.increasing = True
            self.hardware.led_brightness(self.value)
        return self.running

class MainApp(App):
    data = BBViewModelProp()
    arena = HWProp()

    def parse_int_or_zero(self, stringValue):
        try:
            return int(stringValue)
        except:
            return 0

    def __init__(self, **kwargs): 
        self.whiteLight = (255, 255, 255)
        super(MainApp, self).__init__(**kwargs)
        self.arena.init()
        self.breathing_light_control = BreathingLights(self.arena,
                                                       color=self.whiteLight,
                                                       cycle_time=3.0)
        self.breathing_light_control.start()


    def build(self):
        root_widget = ScreenManagement()
        return root_widget

    #
    def match_select_enter(self):
        self.breathing_light_control.start()

    #
    def match_select_leave(self):
        self.breathing_light_control.stop()

    #
    def lights_off(self):
        self.arena.led_fill(0, 0, 0)
        self.arena.led_brightness(0)

    #
    def lights_waiting_for_players(self):
        self.arena.led_fill(0, 255, 128)

    #
    def lights_player_1_ready(self):
        pass

    #
    def lights_player_2_ready(self):
        pass

    #
    def lights_player_1_door_closed(self):
        pass

    #
    def lights_player_2_door_closed(self):
        pass

    #
    def lights_player_1_needs_to_close_door(self):
        pass

    #
    def lights_player_2_needs_to_close_door(self):
        pass

    #
    def lights_soccer_team_1_scored(self):
        pass

    #
    def lights_soccer_team_2_scored(self):
        pass

    #
    def lights_soccer_team_1_wins(self):
        pass

    #
    def lights_soccer_team_2_wins(self):
        pass

    #
    def lights_soccer_match_tie(self):
        pass
    
    #
    def lights_death_match_config_enter(self):
        pass
    
    #
    def lights_death_match_config_leave(self):
        pass

    #
    def lights_soccer_config_enter(self):
        pass

    #
    def lights_soccer_config_leave(self):
        pass

    #
    def lights_count_down_screen_go(self):
        pass

    #
    def lights_count_down_screen_1(self):
        pass

    #
    def lights_count_down_screen_2(self):
        pass

    #
    def lights_count_down_screen_3(self):
        pass

    #
    def lights_death_match(self):
        pass

    #
    def lights_soccer_match(self):
        pass   

    #
    def lights_game_paused(self):
        pass

    #
    def lights_door_drop_count_down_lights(self):
        pass

    # I need to make sure that this gets implemented later.
    def get_led_count(self):
        return 42

    def do_door_drop(self):
        pass


if __name__ == '__main__':
    MainApp().run()