from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty

class BBDeathMatchProp(EventDispatcher):
    duration = StringProperty("180")
    player_one_name  = StringProperty("", allownone=False)
    player_two_name = StringProperty("", allownone=False)
    door_drop = StringProperty("Drop Both", allownone=False)
    door_drop_duration = StringProperty("180")

    def on_duration(self, instance, value):
        pass

    def on_player_one_name(self, instance, value):
        pass

    def on_player_two_name(self, instance, value):
        pass

    def on_door_drop(self, instance, value):
        pass

    def on_door_drop_duration(self, instance, value):
        pass

class BBSoccerMatchProp(EventDispatcher):
    duration = StringProperty("300")
    team_one_name  = StringProperty("", allownone=False)
    team_two_name = StringProperty("", allownone=False)
    points = StringProperty("5")

    def on_duration(self, instance, value):
        pass
    
    def on_team_one_name(self, instance, value):
        pass

    def on_team_two_name(self, instance, value):
        pass

    def on_points(self, instance, value):
        pass

class BBRunSoccerProp(EventDispatcher):
    """"
    Special events associated with this data model
    """
    __events__ = (
        'on_team_one_scored',
        'on_team_two_scored',
        'on_team_one_wins',
        'on_team_two_wins',
        'on_team_one_wins',
        'on_tie_game',
        'on_match_reconfigured',
        'on_match_scrubbed',
        'on_match_paused',
        'on_match_start',
        'on_match_ended'
    )

    data = ObjectProperty(None, allownone=True)
    def on_data(self, instance, value):
        pass

    def on_team_one_scored(self):
        pass

    def on_team_two_scored(self):
        pass

    def on_team_one_wins(self):
        pass

    def on_team_two_wins(self):
        pass

    def on_team_one_wins(self):
        pass

    def on_tie_game(self):
        pass

    def on_match_reconfigured(self):
        pass

    def on_match_scrubbed(self):
        pass

    def on_match_paused(self):
        pass

    def on_match_start(self):
        pass

    def on_match_ended(self):
        pass

class BBRunDeathMatchProp(EventDispatcher):
    """"
    Special events associated with this data model
    """
    __events__ = (
        'on_player_one_wins',
        'on_player_two_wins',
        'on_match_scrubbed',
        'on_match_start',
        'on_match_ended'
    )
    data = ObjectProperty(None, allownone=True)
    def on_data(self, instance, value):
        pass

    def on_player_one_wins(self):
        pass

    def on_player_two_wins(self):
        pass

    def on_match_scrubbed(self):
        pass
    
    def on_match_start(self):
        pass

    def on_match_ended(self):
        pass

class BBViewModelProp(EventDispatcher):
    """"
    Special events associated with this data model
    """
    __events__ = (
        'on_clear',
        'on_match_complete',
        'on_start_match',
        'on_finish_match'
    )

    current = ObjectProperty(None, allownone=True)
    death_match = BBDeathMatchProp()
    soccer_match = BBSoccerMatchProp()
    run_death_match = BBRunDeathMatchProp()
    run_soccer_match = BBRunSoccerProp()

    # Default handlers for properties.
    def on_current(self, instance, value):
        pass

    def on_death_match(self, instance, value):
        pass

    def on_soccer_match(self, instance, value):
        pass

    def on_run_death_match(self, instance, value):
        pass

    def on_run_soccer_match(self, instance, value):
        pass

    def on_clear(self):
        pass

    def on_match_complete(self):
        pass

    def on_start_match(self):
        pass

    def on_finish_match(self):
        pass