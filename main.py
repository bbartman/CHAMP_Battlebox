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
    def __init__(self, **kwargs): 
        self.register_event_type("on_max_score_reached", )
        #self.register_event_type("on_team_one_scored")
        #self.register_event_type("on_team_two_scored")
        super(RunSoccerScreen, self).__init__(**kwargs)

    def on_data(self, instance, value):
        self.data.bind(team_one_score=self.on_team_one_scored,
                       team_two_score=self.on_team_one_scored)

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

class DMDecisionScreen(Screen):
    pass


class PlayersReadyScreen(Screen):
    players_ready = NumericProperty()
    next_screen_after_ready = StringProperty()
    player_or_team = StringProperty("Player")
    previous_screen = StringProperty()
    def __init__(self, **kwargs): 
        self.register_event_type("on_everyone_ready")
        super(PlayersReadyScreen, self).__init__(**kwargs)

    def reset_screen(self, nextScreen, POrT, previousScreen):
        self.players_ready = 0
        self.next_screen_after_ready = nextScreen
        self.player_or_team = POrT
        self.previous_screen = previousScreen

    def on_players_ready(self, instance, value):
        if value == 2:
            self.dispatch("on_everyone_ready")

    def on_next_screen_after_ready(self, instance, value):
        pass

    def on_everyone_ready(self):
        pass


class ScreenManagement(ScreenManager):
    pass

class CustomDropDown(DropDown): 
    pass



class CountDownClockLabel(Label):

    Timer_idle = 0
    Timer_running = 1
    Timer_paused = 2
    Timer_canceled = 3
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

    def start(self, execTime):
        Animation.cancel_all(self)  # stop any current animations
        self.seconds = execTime
        self.on_seconds(None, None)
        self.anim = Animation(seconds=0, duration=self.seconds)
        def finish_callback(animation, incr_crude_clock):
            incr_crude_clock.text = "FINISHED"
        self.anim.bind(on_complete=finish_callback)
        self.anim.start(self)

    def stop(self):
        print("Did we stop?")
        Animation.cancel_all(self)
        print("Current value of seconds = ", self.seconds)

    def on_seconds(self, instance, value):
        self.text = str(round(self.seconds, 1))

    def _change_state(self, nextState):
        if self.state == Timer_idle:
            if nextState == Timer_idle:
                pass
            elif nextState == Timer_running:
                pass
            elif self.state == Timer_paused:
                pass
            elif self.state == Timer_canceled:
                pass
            elif self.state == Timer_time_expired:
                pass
            else:
                raise Exception("Invalid State")
        elif self.state == Timer_running:
            #self.dispatch("on_start")
            pass
        elif self.state == Timer_paused:
            #self.dispatch("on_start")
            #self.dispatch("on_pause")
            pass
        elif self.state == Timer_canceled:
            #self.dispatch("on_start")
            #self.dispatch("on_cancelled")
            pass
        elif self.state == Timer_time_expired:
            #self.dispatch("on_start")
            #self.dispatch("on_time_expired")
            pass
        else:
            raise Exception("Invalid State")
        #if nextState == Timer_idle:
            
        #elif nextState == Timer_running:
        #    if self.state == Timer_idle:
        #        pass
        #    elif self.state == Timer_running:
        #        pass
        #    elif self.state == Timer_paused:
        #        pass
        #    elif self.state == Timer_canceled:
        #        pass
        #    elif self.state == Timer_time_expired:
        #        pass
        #    else:
        #        raise Exception("Invalid State")
        #elif nextState == Timer_paused:
        #    if self.state == Timer_idle:
        #        pass
        #    elif self.state == Timer_running:
        #        pass
        #    elif self.state == Timer_paused:
        #        pass
        #    elif self.state == Timer_canceled:
        #        pass
        #    elif self.state == Timer_time_expired:
        #        pass
        #    else:
        #        raise Exception("Invalid State")
        #elif nextState == Timer_canceled:
        #    if self.state == Timer_idle:
        #        pass
        #    elif self.state == Timer_running:
        #        pass
        #    elif self.state == Timer_paused:
        #        pass
        #    elif self.state == Timer_canceled:
        #        pass
        #    elif self.state == Timer_time_expired:
        #        pass
        #    else:
        #        raise Exception("Invalid State")
        #elif nextState == Timer_time_expired:
        #    if self.state == Timer_idle:
        #        pass
        #    elif self.state == Timer_running:
        #        pass
        #    elif self.state == Timer_paused:
        #        pass
        #    elif self.state == Timer_canceled:
        #        pass
        #    elif self.state == Timer_time_expired:
        #        pass
        #    else:
        #        raise Exception("Invalid State")
        #else:
        #    raise Exception("Invalid State")
    def on_timer_idle(self):
        pass
    
    def on_start(self):
        pass
    
    def on_pause(self):
        pass
    
    def on_resume(self):
        pass
    
    def on_scrubbed(self):
        pass

    def on_cancelled(self):
        pass

    def on_time_expired(self):
        pass

class VictoryScreen(Screen):
    victor_text = StringProperty()
    next_screen = StringProperty()

    def reset_screen(self, VictoryText, NextScreen):
        self.victor_text = VictoryText
        self.next_screen = NextScreen

    def on_enter(self):
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


class MainApp(App):
    data = BBViewModelProp()

    def __init__(self, **kwargs): 
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        root_widget = ScreenManagement()
        return root_widget

if __name__ == '__main__':
    MainApp().run() 