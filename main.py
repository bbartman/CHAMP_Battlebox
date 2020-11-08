from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
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
    '''The code of the application itself.''' 
    def __init__(self, **kwargs): 
          
        '''The button at the opening of the window is created here, 
        not in kv 
        ''' 
        super(DropdownDemo, self).__init__(**kwargs) 
        self.dropdown = CustomDropDown() 
  
        # Creating a self widget bouton 
        self.mainbutton = Button(text ='Do you in college?', 
                                 size_hint_x = 0.6, size_hint_y = 0.15) 
          
        # Added button to FloatLayout so inherits this class  
        self.add_widget(self.mainbutton) 
  
        # Adding actions  
        # If click  
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