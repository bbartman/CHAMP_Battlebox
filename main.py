from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

class MainScreen(Screen):
    pass

class DeathmatchScreen(Screen):
    pass

class DeathmatchScreen(Screen):
    pass

class BattleRoyaleScreen(Screen):
    pass

class SoccerScreen(Screen):
    pass

class TournamentScreen(Screen):
    pass

class RunDeathmatchScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()