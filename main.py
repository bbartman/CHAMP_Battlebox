from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
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

class RunSoccerScreen(Screen):
    pass

class TournamentScreen(Screen):
    pass

class RunDeathmatchScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class DoorDropScreenManager(ScreenManager):
    pass

class DD_NoDropScreen(Screen):
    pass

class DD_AlwaysOpenScreen(Screen):
    pass

class DD_DropAfterTimeScreen(Screen):
    pass

class CustomDropDown(DropDown): 
    pass

class DropdownDemo(GridLayout): 
    def __init__(self, **kwargs): 
        super(DropdownDemo, self).__init__(**kwargs) 
        self.labelDispalay = Label(text='Door Drop Mode', font_size=30)
        self.add_widget(self.labelDispalay) 
        self.dropdown = CustomDropDown() 
        self.mainbutton = Button(text ='Drop Both')

        # Added button to FloatLayout so inherits this class
        self.add_widget(self.mainbutton) 
        self.mainbutton.bind(on_release = self.dropdown.open) 
  
        # root.select on_select called 
        self.dropdown.bind(on_select = lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.dropdown.bind(on_select = self.callback)
   
    def callback(self, instance, x): 
        '''x is self.mainbutton.text refreshed''' 
        print ( "The chosen mode is: {0}" . format ( x ) ) 


presentation = Builder.load_file("main.kv")


class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()