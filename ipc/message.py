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
    def __init__(self, scrn):
        super().__init__()
        self.screen = scrn

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
    def __init__(self, msg):
        super().__init__()
        self.victory_msg = msg

    def do_action(self, app, root):
        temp = app.root.get_screen('VictoryScreen')
        temp.reset_screen(self.victory_msg)
        root.current = 'VictoryScreen'
        root.transition.direction = 'left'

class CountDown(IPCMessage):
    def __init__(self, finalText):
        super().__init__()
        self.final_text = finalText

    def do_action(self, app, root):
        cds = app.root.get_screen('CountDownScreen')
        cds.do_countdown(self.ts, self.final_text)

class MatchStartsAt(IPCMessage):
    def __init__(self, startingTS, Duration):
        super().__init__()
        self.start_time_stamp = startingTS
        self.duration_seconds = Duration

    def do_action(self, app, root):
        # cds = app.root.get_screen('CountDownScreen')
        # cds.do_countdown(self.ts, self.final_text)
        # Make this work for both run deathmatch AND run soccer
        pass

class ClockSync(IPCMessage):
    """Used for synchronizing clocks between main and media applications.
    This is used for associating a match time with current computer timestamp, then
    figuring out how to compensate for not 100% synchronous times."""
    def __init__(self, matchTime):
        self.match_time = matchTime
        # self.time_stamp = CurTS

    def do_action(self, app, root):
        # cds = app.root.get_screen('CountDownScreen')
        # cds.do_countdown(self.ts, self.final_text)
        # Make this work for both run deathmatch AND run soccer
        pass
# This may only be useful if we 100% need to make sure that time is
# synchronized
# class MatchClockTick(IPCMessage):
#     def __init__(self, matchTime):
#         self.current_time = matchTime

#     def do_action(self, app, root):
#         # cds = app.root.get_screen('CountDownScreen')
#         # cds.do_countdown(self.ts, self.final_text)
#         pass

MessageTypes = [ScreenChange, CountDown, DeclareWinner, MatchStartsAt]
TypesToCreate = { x.__name__: x for x in MessageTypes }

class IPCMessageEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, (*MessageTypes,)):
            return vars(obj)

        return json.JSONEncoder.default(self, obj)


def decode_from_json(jsonStr):
    s = json.loads(jsonStr)
    if s["kind"] not in TypesToCreate:
        Logger.warning(f"decode_from_json: Received invalid message ={jsonStr}")
        kindStr = s["kind"]
        raise Exception(f"Invalid message kind {kindStr}")

    cmdObj = None
    if ScreenChange.__name__ == s["kind"]:
        Logger.info("decode_from_json: Received screen change")
        cmdObj = ScreenChange(s["screen"])

    elif CountDown.__name__ == s["kind"]:
        Logger.info("decode_from_json: Received countdown")
        cmdObj = CountDown(s["final_text"])

    elif DeclareWinner.__name__ == s["kind"]:
        Logger.info("decode_from_json: Received DeclareWinner")
        cmdObj = DeclareWinner(s["victory_msg"])

    Logger.info("decode_from_json: Completed translation")
    cmdObj.ts = s["ts"]
    Logger.info("decode_from_json: Exiting function")
    return cmdObj