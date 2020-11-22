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
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty, NumericProperty
from BattleBox.data import BBViewModelProp, BBDeathMatchProp, BBSoccerMatchProp, BBRunDeathMatchProp
from BattleBox.arena import Arena
from kivy.config import Config
import platform, re


Config.read("BattleBox.ini")

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

        temp = app.root.get_screen('WaitForPlayers')
        temp.reset_screen("RunDeathmatch", "Player", self.name, "FIGHT!!!")
        app.root.current = 'WaitForPlayers'
        root.manager.transition.direction = 'left'

class RunDeathmatchScreen(Screen):
    data = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs): 
        super(RunDeathmatchScreen, self).__init__(**kwargs)

    def on_data(self, instance, value):
        '''This is called once we have initialzied all of the other widgets 
        and we are setting data for the first and only time'''
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
            self.ids.countDownClock.pause()
        else:
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
            return "NO BODY"
        if self.data.team_one_score > self.data.team_two_score:
            return self.smData.get_team_one_name()
        else:
            return self.smData.get_team_two_name()

class RunSoccerSubScreenSelector(ScreenManager):
    pass

class DMDecisionScreen(Screen):
    pass


class PlayersReadyScreen(Screen):
    players_ready = NumericProperty()
    next_screen_after_ready = StringProperty()
    player_or_team = StringProperty("Player")
    previous_screen = StringProperty()
    count_down_word = StringProperty()

    def __init__(self, **kwargs): 
        self.register_event_type("on_everyone_ready")
        super(PlayersReadyScreen, self).__init__(**kwargs)

    def reset_screen(self, nextScreen, POrT, previousScreen, word):
        self.players_ready = 0
        self.next_screen_after_ready = nextScreen
        self.player_or_team = POrT
        self.previous_screen = previousScreen
        self.count_down_word = word

    def on_players_ready(self, instance, value):
        if value == 2:
            self.dispatch("on_everyone_ready")

    def on_next_screen_after_ready(self, instance, value):
        pass

    def on_everyone_ready(self):
        pass

    def on_count_down_word(self, instance, value):
        pass


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
        #self.state = nextState

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
        self._do_animation(2, self.finish_callback_2)

    def finish_callback_2(self, animation, Ticker):
        self._do_animation(1, self.finish_callback_3)

    def finish_callback_3(self, animation, Ticker):
        Ticker.text = self.final_word
        self.color = [1,1,1,1]
        self.anim = Animation(color=[1,1,1,1], duration=0.3)
        self.anim.bind(on_complete=self.complete_count_down)
        self.anim.start(self)

    def complete_count_down(self, animation, Ticker):
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
        self._do_animation(3, self.finish_callback_1)

    def on_seconds(self, instance, value):
        self.text = str(int(self.seconds))

    def cancel(self):
        Animation.cancel_all(self)
        
    def on_ready(self):
        pass


class MainApp(App):
    data = BBViewModelProp()
    def parse_int_or_zero(self, stringValue):
        try:
            return int(stringValue)
        except:
            return 0
    def __init__(self, **kwargs): 
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        root_widget = ScreenManagement()
        return root_widget

if __name__ == '__main__':
    MainApp().run()