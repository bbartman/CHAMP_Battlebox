from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty, NumericProperty

class BBDeathMatchProp(EventDispatcher):
    duration = NumericProperty(180)
    player_one_name = StringProperty("", allownone=False)
    player_two_name = StringProperty("", allownone=False)
    door_drop = StringProperty("Drop Both", allownone=False)
    door_drop_duration = NumericProperty(120)

    def get_player_one_name(self):
        if self.player_one_name == "":
            return "Player 1"
        else:
            return self.player_one_name

    def get_player_two_name(self):
        if self.player_two_name == "":
            return "Player 2"
        else:
            return self.player_two_name

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

    def reset(self):
        self.door_drop = BBDeathMatchProp.door_drop.defaultvalue
        self.duration = BBDeathMatchProp.duration.defaultvalue
        self.player_one_name  = BBDeathMatchProp.player_one_name.defaultvalue
        self.player_two_name= BBDeathMatchProp.player_two_name.defaultvalue
        self.door_drop_duration = BBDeathMatchProp.door_drop_duration.defaultvalue

    def dump(self):
        print("Deathmatch info!")
        print("  Duration = ", self.duration)
        print("  Door drop = ", self.door_drop)
        print("  Door drop duration = ", self.door_drop_duration)
        print("  Player 1 = ", self.player_one_name)
        print("  Player 2 = ", self.player_two_name)



class BBSoccerMatchProp(EventDispatcher):
    duration = NumericProperty(300)
    team_one_name  = StringProperty("", allownone=False)
    team_two_name = StringProperty("", allownone=False)
    points = NumericProperty(5)


    def get_team_one_name(self):
        if self.team_one_name == "":
            return "Team 1"
        else:
            return self.team_one_name 

    def get_team_two_name(self):
        if self.team_two_name == "":
            return "Team 2"
        else:
            return self.team_two_name
    def on_duration(self, instance, value):
        pass
    
    def on_team_one_name(self, instance, value):
        pass

    def on_team_two_name(self, instance, value):
        pass

    def on_points(self, instance, value):
        pass

    def reset(self):
        self.duration = BBSoccerMatchProp.duration.defaultvalue
        self.team_one_name  = BBSoccerMatchProp.team_one_name.defaultvalue
        self.team_two_name = BBSoccerMatchProp.team_two_name.defaultvalue
        self.points = BBSoccerMatchProp.points.defaultvalue


class BBRunSoccerProp(EventDispatcher):
    team_one_score = BoundedNumericProperty(0, min=0, max=1000, errorvalue=0)
    team_two_score = BoundedNumericProperty(0, min=0, max=1000, errorvalue=0)
    def on_team_one_score(self, instance, value):
        pass
    def on_team_two_score(self, instance, value):
        pass

class BBRunDeathMatchProp(EventDispatcher):
    data = ObjectProperty(None, allownone=True)

    def on_data(self, instance, value):
        pass

class BBViewModelProp(EventDispatcher):
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