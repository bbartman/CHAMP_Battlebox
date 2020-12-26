import json, time
from kivy.logger import Logger

ScreenMap = {
    "main":"main",
    "DeathMatchDecision":"MatchOver"
}

class IPCMessage:
    def __init__(self):
        super(IPCMessage, self).__init__()
        self.kind = type(self).__name__

    def do_action(self, app, root):
        raise NotImplementedError("No default implementation for IPCMessage.do_action")

    def to_json(self):
        self.ts = int(round(time.time() * 1000))
        return json.dumps(self, cls=IPCMessageEncoder)

class ScreenChange(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.screen = ""
        if len(args):
            self.screen = args[0]
            return
        if "screen" in kwargs:
            self.screen = kwargs["screen"]

    def do_action(self, app, root):
        # We ignore this because we will have another message that will
        # contian additional information about the current winner that we
        # will need to display.
        if self.screen == "VictoryScreen":
            return
        if self.screen not in ScreenMap:
            root.current = self.screen
        else:
            root.current = ScreenMap[self.screen]
        root.transition.direction = 'left'

class DeclareWinner(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.victory_msg = ""
        if len(args):
            self.victory_msg = args[0]
            return
        if "victory_msg" in kwargs:
            self.victory_msg = kwargs["victory_msg"]

    def do_action(self, app, root):
        temp = app.root.get_screen('VictoryScreen')
        temp.reset_screen(self.victory_msg)
        root.current = 'VictoryScreen'
        root.transition.direction = 'left'

class CountDown(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.final_text = ""
        if len(args):
            self.final_text = args[0]
            return
        if "final_text" in kwargs:
            self.final_text = kwargs["final_text"]

    def do_action(self, app, root):
        cds = app.root.get_screen('CountDownScreen')
        cds.do_countdown(self.ts, self.final_text)

class RunDeathMatchMsg(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.start_time_stamp = 0
        self.duration = 0

        if len(args) != 0:
            if len(args) != 5:
                raise ValueError("Incorrect number of argument.")
            self.start_time_stamp = args[0]
            self.duration = args[1]
            self.will_drop_doors = args[2]
            self.dd_count_down_start_time = args[3]
            self.dd_end_time = args[4]
            return

        if "start_time_stamp" in kwargs:
            self.start_time_stamp = kwargs["start_time_stamp"]

        if "duration" in kwargs:
            self.duration = kwargs["duration"]

        if "will_drop_doors" in kwargs:
            self.will_drop_doors = kwargs["will_drop_doors"]

        if "dd_count_down_start_time" in kwargs:
            self.dd_count_down_start_time = kwargs["dd_count_down_start_time"]

        if "dd_end_time" in kwargs:
            self.dd_end_time = kwargs["dd_end_time"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunDeathmatch')
        rdms.configure_screen(self.start_time_stamp, self.duration, self.will_drop_doors,
            self.dd_count_down_start_time, self.dd_end_time)


class RunSoccerMsg(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.start_time_stamp = 0
        self.duration = 0
        self.red_team_name = ""
        self.blue_team_name = ""

        if len(args) != 0:
            if len(args) != 4:
                raise ValueError("Incorrect number of argument.")
            self.start_time_stamp = args[0]
            self.duration = args[1]
            self.red_team_name = args[2]
            self.blue_team_name = args[3]
            return

        if "start_time_stamp" in kwargs:
            self.start_time_stamp = kwargs["start_time_stamp"]

        if "duration" in kwargs:
            self.duration = kwargs["duration"]

        if "red_team_name" in kwargs:
            self.red_team_name = kwargs["red_team_name"]

        if "blue_team_name" in kwargs:
            self.blue_team_name = kwargs["blue_team_name"]

    def do_action(self, app, root):
        rss = app.root.get_screen('RunSoccer')
        rss.configure_screen(self.start_time_stamp, self.duration, self.red_team_name,
            self.blue_team_name)

class UpdateSoccerScore(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.red_score = ""
        self.blue_score = ""

        if len(args) != 0:
            if len(args) != 2:
                raise ValueError("Incorrect number of argument.")
            self.red_score = args[0]
            self.blue_score = args[1]
            return

        if "red_score" in kwargs:
            self.red_score = kwargs["red_score"]

        if "blue_score" in kwargs:
            self.blue_score = kwargs["blue_score"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunSoccer')
        rdms.update_score(self.red_score, self.blue_score)

class RedScoredGoal(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.match_time = 0
        self.red_score = 0

        if len(args) != 0:
            if len(args) != 2:
                raise ValueError("Incorrect number of argument.")
            self.red_score = args[0]
            self.match_time = args[1]
            return

        if "red_score" in kwargs:
            self.red_score = kwargs["red_score"]

        if "match_time" in kwargs:
            self.match_time = kwargs["match_time"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunSoccer')
        rdms.red_scored(self.red_score, self.match_time)

class BlueScoredGoal(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.match_time = 0
        self.blue_score = 0

        if len(args) != 0:
            if len(args) != 2:
                raise ValueError("Incorrect number of argument.")
            self.blue_score = args[0]
            self.match_time = args[1]
            return

        if "blue_score" in kwargs:
            self.blue_score = kwargs["blue_score"]

        if "match_time" in kwargs:
            self.match_time = kwargs["match_time"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunSoccer')
        rdms.blue_scored(self.blue_score, self.match_time)


class ResumeSoccer(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.start_time_stamp = 0
        self.duration = 0

        if len(args) != 0:
            if len(args) != 2:
                raise ValueError("Incorrect number of argument.")
            self.start_time_stamp = args[0]
            self.duration = args[1]
            return

        if "start_time_stamp" in kwargs:
            self.start_time_stamp = kwargs["start_time_stamp"]

        if "duration" in kwargs:
            self.duration = kwargs["duration"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunSoccer')
        rdms.resume_time(self.start_time_stamp, self.duration)

class PauseSoccer(IPCMessage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.duration = 0

        if len(args) != 0:
            if len(args) != 1:
                raise ValueError("Incorrect number of argument.")
            self.stop_time = args[0]
            return

        if "stop_time" in kwargs:
            self.stop_time = kwargs["stop_time"]

    def do_action(self, app, root):
        rdms = app.root.get_screen('RunSoccer')
        rdms.pause_time(self.stop_time)
        


MessageTypes = [ScreenChange, CountDown, DeclareWinner, RunDeathMatchMsg, RunSoccerMsg,
                UpdateSoccerScore, RedScoredGoal, BlueScoredGoal, ResumeSoccer,
                PauseSoccer]
TypesToCreate = { x.__name__: x for x in MessageTypes }

class IPCMessageEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, (*MessageTypes,)):
            return vars(obj)

        return json.JSONEncoder.default(self, obj)


def decode_from_json(jsonStr):
    s = json.loads(jsonStr)
    kindStr = s["kind"]
    if s["kind"] not in TypesToCreate:
        Logger.warning(f"decode_from_json: Received invalid message ={jsonStr}")
        raise ValueError(f"Invalid message kind {kindStr}")

    cmdObj = None
    ty = TypesToCreate.get(kindStr, None)
    if ty is None:
        raise ValueError(f"Invalid type to create {kindStr}")

    if not isinstance(s, dict):
        raise ValueError(f"Invalid message format {jsonStr}")

    cmdObj = ty(**s)

    Logger.info("decode_from_json: Completed translation")
    cmdObj.ts = s["ts"]
    Logger.info("decode_from_json: Exiting function")
    return cmdObj