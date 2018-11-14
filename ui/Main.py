import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics','show_cursor','1')
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
import os
from Table import *

class Toolbar(BoxLayout):
    pass

class Root(FloatLayout):
    sm=None
    storms_list_view = ObjectProperty()
    def __init__(self, **kwargs):
        super(Root,self).__init__(**kwargs)

    def next(self, *args):
        print("next",self.storms_list_view.adapter.selection)

    def prevous(self):
        print("prevous",self.storms_list_view.adapter.selection)




class MainApp(App):
    def build(self):
        return Root()


Factory.register('Root', cls=Root)


if __name__ == '__main__':
    MainApp().run()