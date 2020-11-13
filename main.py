from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BoundedNumericProperty
from BattleBox.data import BBViewModelProp

class MainScreen(Screen):
    pass

class DeathmatchScreen(Screen):
    pass

class SoccerScreen(Screen):
    pass

class RunSoccerScreen(Screen):
    pass

class RunDeathmatchScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
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


#presentation = Builder.load_file("main.kv")


class MainApp(App):
    data = BBViewModelProp()
    def on_change_current(self, instance, value):
        print("Derp")

    def on_switch_to_main(self):
        self.data.current = None

    def __init__(self, **kwargs): 
        super(MainApp, self).__init__(**kwargs)
        self.data.bind(current = self.on_change_current)
        


    def build(self):
        root_widget = ScreenManagement()
        return root_widget

if __name__ == '__main__':
    MainApp().run() 