import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics','show_cursor','1')
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingItem
from kivy.uix.button import Button
import os
import json
from table import *








class Root(BoxLayout):
    sm=None
    upperbound=1
    lowerbound=0
    def __init__(self, **kwargs):
        super(Root,self).__init__(**kwargs)


    def changeScreen(self, buttonTxt):
        # print(Root.upperbound)
        if buttonTxt == "next":
            Root.upperbound+=100
            next(Root.upperbound,0)
            Grid()
            Clock.tick()
            self.ids.screen_manager.current="table_screen"
        elif buttonTxt=="prevous":
            Root.upperbound-=100
            prevous(Root.upperbound,0)
            Grid()
            self.ids.screen_manager.do_layout()
            self.ids.screen_manager.current="table_screen"
        Root.sm=self.ids.screen_manager


class MainApp(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
        return Root()


Factory.register('Root', cls=Root)


if __name__ == '__main__':
    MainApp().run()