from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty, NumericProperty
from BattleBox.data import BBViewModelProp, BBDeathMatchProp, BBSoccerMatchProp, BBRunDeathMatchProp

class MainScreen(Screen):
    pass

class DeathmatchScreen(Screen):
    def reset_screen(self, app):
        app.data.death_match.reset()
        self.ids.dm_door_drop.do_update_main_button(app.data.death_match.door_drop)

    def __init__(self, **kwargs): 
        super(DeathmatchScreen, self).__init__(**kwargs)

    def drop_down_changed(self, instance, x):
        if x == 'Drop Both':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Doors Always Open':
            self.ids.dm_door_drop_duration.disabled = True
        elif x == 'Drop Red Player Door Only':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Drop Blue Player Door Only':
            self.ids.dm_door_drop_duration.disabled = False
        elif x == 'Drop Random Door':
            self.ids.dm_door_drop_duration.disabled = False

class RunDeathmatchScreen(Screen):
    events = [
        'on_not_running',
        'on_starting_match',
        'on_running_match',
        'on_match_paused',
        'on_door_drop',
        'on_player_one_wins',
        'on_player_two_wins',
        'on_match_scrubbed',
        'on_pending_decision',
        'on_match_complete'
    ]

    data = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs): 
        for eventName in RunDeathmatchScreen.events:
            self.register_event_type(eventName)
        super(RunDeathmatchScreen, self).__init__(**kwargs)

    def on_data(self, instance, value):
        '''This is called once we have initialzied all of the other widgets 
        and we are setting data for the first and only time'''
        self.data.bind(state = self.on_state)

    def on_state(self, instance, value):
        if value == BBRunDeathMatchProp.STATE_not_running:
            self.dispatch("on_not_running")
        elif value == BBRunDeathMatchProp.STATE_starting_match:
            self.dispatch("on_starting_match")
        elif value == BBRunDeathMatchProp.STATE_running_match:
            self.dispatch("on_running_match")
        elif value == BBRunDeathMatchProp.STATE_paused:
            self.dispatch("on_match_paused")
        elif value == BBRunDeathMatchProp.STATE_doors_drop:
            self.dispatch("on_door_drop")
        elif value == BBRunDeathMatchProp.STATE_player_one_wins:
            self.dispatch("on_player_one_wins")
        elif value == BBRunDeathMatchProp.STATE_player_two_wins:
            self.dispatch("on_player_two_wins")
        elif value == BBRunDeathMatchProp.STATE_match_canceled:
            self.dispatch("on_match_scrubbed")
        elif value == BBRunDeathMatchProp.STATE_pending_decision:
            self.dispatch("on_pending_decision")
        elif value == BBRunDeathMatchProp.STATE_match_complete:
            self.dispatch("on_match_complete")
        else:
            raise Exception("Invalid state")

    def on_not_running(self):
        pass

    def on_starting_match(self):
        pass

    def on_running_match(self):
        pass

    def on_match_paused(self):
        pass

    def on_door_drop(self):
        pass

    def on_player_one_wins(self):
        pass

    def on_player_two_wins(self):
        pass

    def on_match_scrubbed(self):
        pass

    def on_pending_decision(self):
        pass

    def on_match_reconfigured(self):
        self.data.state = BBRunDeathMatchProp.STATE_not_running

    def on_match_complete(self):
        pass

    def on_pre_enter(self):
        pass

    def on_leave(self):
        pass

class SoccerScreen(Screen):
    def reset_screen(self, app):
        app.data.soccer_match.reset()


class ManualSoccerScoreAdjustmentScreen(Screen):
    pass

class RunSoccerScreen(Screen):
    data = ObjectProperty(None, allownone=False)
    PauseGameStr = "Pause\nGame"
    ResumeGameStr = "Resume\nGame"
    pause_play_button_text = StringProperty("Pause\nGame")
    def __init__(self, **kwargs): 
        self.register_event_type("on_max_score_reached")
        #self.register_event_type("on_team_one_scored")
        #self.register_event_type("on_team_two_scored")
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
        if int(value) == int(self.smData.points):
            self.dispatch("on_max_score_reached")

    def on_team_two_scored(self, instance, value):
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
        incr_crude_clock.text = "FINISHED"
        self.dispatch("on_time_expired")

    def start(self, execTime):
        Animation.cancel_all(self)  # stop any current animations
        self.seconds = execTime
        self.on_seconds(None, None)
        self.anim = Animation(seconds=0, duration=self.seconds)
        self.anim.bind(on_complete=self.finish_callback)
        self._change_state(CountDownClockLabel.Timer_running)
        self.anim.start(self)
    
    def pause(self):
        self._change_state(CountDownClockLabel.Timer_paused)
        Animation.cancel_all(self)

    def resume(self):
        self._change_state(CountDownClockLabel.Timer_running)
        Animation.cancel_all(self)
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

    def __init__(self, **kwargs): 
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        root_widget = ScreenManagement()
        return root_widget

if __name__ == '__main__':
    MainApp().run() 