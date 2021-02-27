import os, asyncio, time, json, sys
from kivy.config import Config
Config.read("Media.ini")
import random

random.seed(int(time.time()*1000))

import cffi, kivy, math, traceback
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Quad, Rectangle, Triangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty, NumericProperty, BooleanProperty
from kivy.logger import Logger

import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from functools import partial
from soundboard import SoundBoard

# This makes sure we get the interprocess communication stuff
# imported correctly.
sys.path.append("..")
from ipc.message import IPCMessage, decode_from_json
from ipc.communicator import connect_to_main_server

class MediaScreenManager(ScreenManager):
    pass

class CDLabel(Label):
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        self.finalWord = ""

    def start_animation(self, finalWord):
        self.finalWord = finalWord
        self.final_text = ""

    def on_start_3(self, animation, widget):
        self.color = [1,1,1,0]
        self.text = "3"

    def on_start_2(self, animation, widget):
        self.text = "2"

    def on_start_1(self, animation, widget):
        self.text = "1"

    def on_start_final(self, animation, widget):
        self.text = self.final_text
        if "GO" in self.final_text:
            App.get_running_app().soundboard.aplay(App.get_running_app().soundboard.cd_go)
        else:
            App.get_running_app().soundboard.aplay(App.get_running_app().soundboard.cd_fight)

    def play_sound(self, sound, anim, w):
        App.get_running_app().soundboard.aplay(sound)

    def _build_sound_anim(self, skewTime, sound):
        sound_offset = skewTime - sound.length
        S1 = Animation(duration=sound_offset)
        S1.bind(on_complete=partial(self.play_sound, sound))
        return S1

    def start_animation(self, finalText, *args):
        startTimeMs = int(round(time.time() * 1000))
        # Clearing any previous text.
        self.final_text = finalText
        self.text = ""
        self.color = [1, 1, 1, 0]
        # Converting current time into milliseconds offset from current tick.
        
        # Building complicated count down animation.
        A1 = Animation(color=[1,1,1,0.7], duration=1.0) + Animation(color=[1,1,1,0], duration=0)
        A1.bind(on_start=self.on_start_3)
        A1 &= self._build_sound_anim(1.0, App.get_running_app().soundboard.cd_three)

        A2 = Animation(color=[1,1,1,0.7], duration=1.0)+ Animation(color=[1,1,1,0], duration=0)
        A2.bind(on_start=self.on_start_2)
        A2 &= self._build_sound_anim(1.0, App.get_running_app().soundboard.cd_two)
        
        A3 = Animation(color=[1,1,1,0.7], duration=1.0) + Animation(color=[1,1,1,0], duration=0)
        A3.bind(on_start=self.on_start_1)
        A3 &= self._build_sound_anim(1.0, App.get_running_app().soundboard.cd_one)

        A4 = Animation(color=[1, 1, 1, 0.7], duration=0.3)
        A4.bind(on_start=self.on_start_final)


        self.anim = A1 + A2 + A3 + A4
        self.anim.start(self)
        endTimeMs = int(round(time.time() * 1000))
        Logger.info(f"MediaApp->CountDown: time to build animation {endTimeMs - startTimeMs}")

    def cancel_animation(self):
        self.anim.cancel(self)

class CountDownScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_leave(self):
        self.stop_count_down()

    def do_countdown(self, startTime, finalText):
        clockStartTimeInMs = (startTime - int(round(time.time() * 1000)))
        self.ids.counter.text = ""
        Logger.info(f"MediaApp->CountDownScreen: Starting countdown in {clockStartTimeInMs/1000.0}")
        Clock.schedule_once(
            partial(self.ids.counter.start_animation, finalText),
            clockStartTimeInMs/1000.0)
        # skew = 1.0 - ((int(round(time.time() * 1000)) - tsSent)/1000.0)
        # (tsSent, finalText)

    def stop_count_down(self):
        self.ids.counter.cancel_animation()

class PymunkDemo(RelativeLayout):
    def cannon(self, space, startingPosition = (0, 20), xDirModifier=1):
        mass = 10
        moment = pymunk.moment_for_box(mass, (20, 20))
        b = pymunk.Body(mass, moment)
        s = pymunk.Poly.create_box(b, (20, 20))
        s.friction = 3
        b.position = startingPosition
        s.color = random.randint(10, 255)/255.0, random.randint(10, 255)/255.0, random.randint(10, 255)/255.0
        space.add(b, s)
        magnatude = random.randint(10000, 15000)
        angleRadians = math.radians(random.randint(3000, 7000)/100.0)
        impulse = Vec2d( (math.cos(angleRadians) * magnatude) * xDirModifier,
                        math.sin(angleRadians) * magnatude)
        b.apply_impulse_at_local_point((impulse))
        with self.canvas:
            Color(*s.color)
            s.ky = Quad(points=self.points_from_poly(s))

    # def create_logo(self, lines, space):
    #     for line in lines:
    #         for i in range(len(line) - 1):
    #             shape = pymunk.Segment(space.static_body, line[i], line[i + 1], 1)
    #             shape.friction = 0.5
    #             space.add(shape)

    def init(self):
        self.run = True
        self.step = 1 / 60.0
        self.start()

    def start(self):
        self.run = True
        self.space = space = pymunk.Space()
        space.gravity = 0, -900
        space.sleep_time_threshold = 0.3
        space.steps = 0
        floor = pymunk.Segment(space.static_body, (0, 0), (1280, 0), 5)
        floor.friction = 1.0
        space.add(floor)
        with self.canvas:
            Color(0.2, 0.2, 0.2)
            floor.ky = Line(points=[0, 0, 1280, 0], width=5)

        # # we use our own event scheduling to make sure a event happens exactly
        # # after X amount of simulation steps
        self.events = []
        def fire_both_sides(space):
            self.cannon(space, startingPosition = (30, 30), xDirModifier=1)
            self.cannon(space, startingPosition = (1250, 30), xDirModifier=-1)
        for x in range(200):
            self.events.append((1, fire_both_sides))

        self.events.append((500, self.reset))
        self.update_event = Clock.schedule_interval(self.update, 1.0 / 20.0)
    def stop(self):
        self.run = False
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()

    def reset(self, *args):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start()

    def update(self, dt):
        stepdelay = 25
        for x in range(6):
            self.space.step(1.0 / 60.0 / 2)
            self.space.step(1.0 / 60.0 / 2)
            self.space.steps += 1
            if (
                len(self.events) > 0
                and self.space.steps - stepdelay > self.events[0][0]
            ):
                _, f = self.events.pop(0)
                f(self.space)

        for shape in self.space.shapes:
            if hasattr(shape, "ky") and not shape.body.is_sleeping:
                if isinstance(shape, pymunk.Circle):
                    body = shape.body
                    shape.ky[0].pos = body.position - (shape.radius, shape.radius)
                    circle_edge = body.position + Vec2d(shape.radius, 0).rotated(
                        body.angle
                    )
                    shape.ky[1].points = [
                        body.position.x,
                        body.position.y,
                        circle_edge.x,
                        circle_edge.y,
                    ]
                if isinstance(shape, pymunk.Segment):
                    body = shape.body
                    p1 = body.position + shape.a.cpvrotate(body.rotation_vector)
                    p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                    shape.ky.points = p1.x, p1.y, p2.x, p2.y
                if isinstance(shape, pymunk.Poly):
                    shape.ky.points = self.points_from_poly(shape)
        return self.run

    def ellipse_from_circle(self, shape):
        pos = shape.body.position - (shape.radius, shape.radius)
        e = Ellipse(pos=pos, size=[shape.radius * 2, shape.radius * 2])
        circle_edge = shape.body.position + Vec2d(shape.radius, 0).rotated(
            shape.body.angle
        )
        Color(0.17, 0.24, 0.31)
        l = Line(
            points=[
                shape.body.position.x,
                shape.body.position.y,
                circle_edge.x,
                circle_edge.y,
            ]
        )
        return e, l

    def points_from_poly(self, shape):
        body = shape.body
        ps = [p.rotated(body.angle) + body.position for p in shape.get_vertices()]
        vs = []
        for p in ps:
            vs += [p.x, p.y]
        return vs

class VictoryScreen(Screen):
    def __init__(self, **kwargs):
        super(VictoryScreen, self).__init__(**kwargs)
    
    def reset_screen(self, VictoryText):
        self.ids.victoryText .text = VictoryText

# class MatchScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
 

class RunDeathmatchScreen(Screen):
    dd_prog_value = NumericProperty(0)
    seconds = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation = None
        self.say_halt = False

    def on_leave(self):
        if self.animation is not None:
            Animation.cancel_all(self)
            self.animation = None

    def switch_dd_screen(self, name, *args):
        self.ids.ddDisplay.current = name
        self.ids.ddDisplay.transition.direction = "left"

    def run_animation(self, duration, will_dd, dd_startTime, dd_endTime, timeDelta):
        self.seconds = duration
        self.animation = Animation(seconds=0, duration=duration)
        if will_dd:
            assert dd_startTime > dd_endTime, "This ends before it starts"
            Logger.info("MediaApp->MatchScreen->runAnimation: animating dd")
            self.dd_prog_value = 0
            # Late message start colaboration.
            if duration < dd_startTime:
                raise Exception("Possible issue with late starting deathmatch timer.")
            delayedStart = Animation(duration=duration - dd_startTime) 
            ddAnimation = Animation(dd_prog_value=self.ids.pb.max, duration=dd_startTime - dd_endTime)
            ddAnimation.bind(on_start=partial(self.switch_dd_screen, "dd"),
                             on_complete=partial(self.switch_dd_screen, "postdd"))
            combinedAnimations = delayedStart + ddAnimation
            self.animation &= combinedAnimations
        self.animation.start(self)
        return False

    def configure_screen(self, startTime, duration, will_dd, dd_startTime, dd_endTime):
        clockStartTimeInMs = startTime - int(round(time.time() * 1000))
        if clockStartTimeInMs <= 0:
            Logger.info("MediaApp->RunDeathmatchScreen: Starting timer late or now")
            reducedTime = duration + (clockStartTimeInMs/1000.0)
            self.run_animation(reducedTime, will_dd, dd_startTime, dd_endTime, 0)
        else:
            Logger.info(f"MediaApp->RunDeathmatchScreen: Setting timer for later {clockStartTimeInMs/1000.0}")
            Clock.schedule_once(
                partial(self.run_animation, duration, will_dd, dd_startTime, dd_endTime),
                clockStartTimeInMs/1000.0)

    def on_seconds(self, instance, value):
        try:
            if (float(self.ids.time.text) >= self.seconds):
                self.say_halt = True 
        except:
            pass
        self.ids.time.text = str(round(self.seconds, 1))
        if (float(self.seconds) <= 0.0):
            if self.say_halt: 
                App.get_running_app().soundboard.aplay(App.get_running_app().soundboard.hault)
                self.say_halt = False
        self.ids.time.text = str(round(self.seconds, 1))

class RunSoccerScreen(Screen):
    red_team_name = StringProperty("Red team")
    red_score = NumericProperty(0)
    blue_team_name = StringProperty("Blue team")
    blue_score = NumericProperty(0)
    seconds = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation = None
        self.red_team_goal_anim = None
        self.blue_team_goal_anim = None
        self.say_halt = False

    def on_leave(self):
        Animation.cancel_all(self)
        self.animation = None

    def on_enter(self):
        self.seconds = 0
        

    def on_seconds(self, instance, value):
        try:
            if (float(self.ids.time.text) >= self.seconds):
                self.say_halt = True 
        except:
            pass
        self.ids.time.text = str(round(self.seconds, 1))
        if (float(self.seconds) <= 0.0):
            if self.say_halt: 
                App.get_running_app().soundboard.aplay(App.get_running_app().soundboard.hault)
                self.say_halt = False

    def run_animation(self, duration, deltaTime):
        self.seconds = duration
        self.animation = Animation(seconds=0, duration=duration)
        self.animation.start(self)
        return False
    
    # This does a complete screen reset.
    def configure_screen(self, startTime, duration, redTeamName, blueTeamName):
        self.switch_subscreens("scoreDisplay")
        self.red_score = 0
        self.blue_score = 0
        self.red_team_name = redTeamName
        self.blue_team_name = blueTeamName
        clockStartTimeInMs = startTime - int(round(time.time() * 1000))
        if clockStartTimeInMs <= 0:
            Logger.info("MediaApp->RunSoccerScreen: Starting timer late or now")
            reducedTime = duration + (clockStartTimeInMs/1000.0)
            self.run_animation(reducedTime, 0)
        else:
            Logger.info(f"MediaApp->RunSoccerScreen: Setting timer for later {clockStartTimeInMs/1000.0}")
            Clock.schedule_once(partial(self.run_animation, duration),
                clockStartTimeInMs/1000.0)
    
    # This is for the manual score change screen update.
    # Should not display goals screen.
    def update_score(self, redTeamGoals, blueTeamGoals):
        self.red_score = redTeamGoals
        self.blue_score = blueTeamGoals

    def switch_subscreens(self, screenName, *AniArgs):
        self.ids.sm.current = screenName
        self.ids.sm.transition.direction = "left"

    def red_scored(self, goalCount, timePaused):
        Animation.cancel_all(self)
        self.seconds = timePaused
        self.red_score = goalCount
        self.red_team_goal_anim = Animation(duration=10)
        self.red_team_goal_anim.bind(on_start=partial(self.switch_subscreens, "redGoal"),
                                     on_complete=partial(self.switch_subscreens, "scoreDisplay"))
        self.red_team_goal_anim.start(self)

    def blue_scored(self, goalCount, timePaused):
        Animation.cancel_all(self)
        self.seconds = timePaused
        self.blue_score = goalCount
        self.blue_team_goal_anim = Animation(duration=10)
        self.blue_team_goal_anim.bind(on_start=partial(self.switch_subscreens, "blueGoal"),
                                      on_complete=partial(self.switch_subscreens, "scoreDisplay"))
        self.blue_team_goal_anim.start(self)

    def resume_time(self, startTime, duration):
        clockStartTimeInMs = startTime - int(round(time.time() * 1000))
        if clockStartTimeInMs <= 0:
            Logger.info("MediaApp->resume_time: Starting timer late or now")
            reducedTime = duration + (clockStartTimeInMs/1000.0)
            self.run_animation(reducedTime, 0)
        else:
            Logger.info(f"MediaApp->resume_time: Setting timer for later {clockStartTimeInMs/1000.0}")
            Clock.schedule_once(partial(self.run_animation, duration),
                clockStartTimeInMs/1000.0)


    def pause_time(self, stopTime):
        # In the future I need to put a blink on the text for this.
        Animation.cancel_all(self)
        self.seconds = stopTime

RedBG = [1, 0, 0, 1]
GreenBG = [0, 1, 0, 1]
YellowBG = [1, 1, 0, 1]

class WaitForPlayers(Screen):
    red_status = BooleanProperty(False)
    blue_status = BooleanProperty(False)

    red_bg_color = ListProperty(RedBG)
    blue_bg_color = ListProperty(RedBG)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    def on_red_status(self, instance, value):
        if value:
            self.red_bg_color = GreenBG
        else:
            self.red_bg_color = RedBG

    def on_blue_status(self, instance, value):
        if value:
            self.blue_bg_color = GreenBG
        else:
            self.blue_bg_color = RedBG

class WaitForPlayersAndDoors(Screen):
    red_status = BooleanProperty(False)
    blue_status = BooleanProperty(False)
    red_door = BooleanProperty(False)
    blue_door = BooleanProperty(False)

    red_bg_color = ListProperty(RedBG)
    blue_bg_color = ListProperty(RedBG)
    red_door_bg_color = ListProperty(RedBG)
    blue_door_bg_color = ListProperty(RedBG)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.red_animation = None
        self.blue_animation = None
        
    def switch_red_door_color(self, color, *args):
        self.red_door_bg_color = color

    def switch_blue_door_color(self, color, *args):
        self.blue_door_bg_color = color

    def on_leave(self):
        Animation.cancel_all(self.ids.redDoor)
        Animation.cancel_all(self.ids.blueDoor)

    def red_blink_door(self):
        Logger.info("MainApp->WaitForPlayersAndDoors: Called red blink")
        w = self.ids.redDoor
        Animation.cancel_all(w)
        def getColor(val):
            if (val % 2) == 1:
                return RedBG
            else:
                return YellowBG
        blinkTime = 0.3
        for x in range(6):
            if x == 0:
                self.red_animation = Animation(duration=blinkTime)
                self.red_animation.bind(on_start=partial(self.switch_red_door_color, getColor(x)))
            else:
                anim = Animation(duration=blinkTime)
                anim.bind(on_start=partial(self.switch_red_door_color, getColor(x)))
                self.red_animation += anim
        self.red_animation.bind(on_complete=partial(self.switch_red_door_color, RedBG))
        self.red_animation.start(w)

    def blue_blink_door(self):
        Logger.info("MainApp->WaitForPlayersAndDoors: Called blue blink")
        w = self.ids.blueDoor
        Animation.cancel_all(w)
        def getColor(val):
            if (val % 2) == 1:
                return RedBG
            else:
                return YellowBG
        blinkTime = 0.3
        for x in range(6):
            if self.blue_animation is None:
                self.blue_animation = Animation(duration=blinkTime)
                self.blue_animation.bind(on_start=partial(self.switch_blue_door_color, getColor(x)))
            else:
                anim = Animation(duration=blinkTime)
                anim.bind(on_start=partial(self.switch_blue_door_color, getColor(x)))
                self.blue_animation += anim
        self.blue_animation.bind(on_complete=partial(self.switch_blue_door_color, RedBG))
        self.blue_animation.start(w)

    def on_red_status(self, instance, value):
        if value:
            self.red_bg_color = GreenBG
        else:
            self.red_bg_color = RedBG

    def on_blue_status(self, instance, value):
        if value:
            self.blue_bg_color = GreenBG
        else:
            self.blue_bg_color = RedBG

    def on_red_door(self, instance, value):
        Animation.cancel_all(self.ids.redDoor)
        if value:
            self.red_door_bg_color = GreenBG
        else:
            self.red_door_bg_color = RedBG

    def on_blue_door(self, instance, value):
        Animation.cancel_all(self.ids.blueDoor)
        if value:
            self.blue_door_bg_color = GreenBG
        else:
            self.blue_door_bg_color = RedBG

    
class MediaApp(App):
    def on_start(self):
        self.soundboard = SoundBoard()
        self.task = asyncio.create_task(connect_to_main_server(self.addr, self.on_received_cmd))

    def __init__(self, **kwargs):
        self.addr = Config.get("media", "socket", fallback="/home/pi/.battle_box_helpers/media_socket")
        super(MediaApp, self).__init__(**kwargs)

    def on_received_cmd(self, line):
        try:
            Logger.info(f"MediaApp: Received command {line}")
            cmd = decode_from_json(line)
            cmd.do_action(self, self.root)

        except Exception as E:
            Logger.info(f"MediaApp: Error Message {E}")
            Logger.info(f"MediaApp: {traceback.format_exc()}")


    def on_stop(self):
        tasks = [t for t in asyncio.all_tasks() if t is not
                asyncio.current_task()]
        [task.cancel() for task in tasks]
        Logger.info(f"MediaApp: Cancelling {len(tasks)} outstanding tasks")

    def build(self):
        root_widget = MediaScreenManager()
        return root_widget

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MediaApp().async_run())
    loop.close()