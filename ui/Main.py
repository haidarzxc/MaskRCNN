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
from kivy.uix.label import Label
import os
from Table import *
from pathlib import Path

import os, sys, inspect
import pandas as pd
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datasets.NCDC_stormevents_data_loader import load_CSV_file
from utils.time import to_UTC_time
from Graph import graph,get_aws_object

class Toolbar(BoxLayout):
    pass

class Root(BoxLayout):
    sm=None
    items_list = ObjectProperty(None)
    column_headings = ObjectProperty(None)
    rv_data = ListProperty([])
    storms=load_CSV_file('NCDC_stormevents/area_filtered_stormevents.csv')


    nexrad=load_CSV_file('NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv')
    goes=load_CSV_file('goes_intersections/GOES_datetime_filtered_intersections.csv')
    row=None

    def __init__(self, **kwargs):
        super(Root,self).__init__(**kwargs)
        self.get_dataframe()


    def get_dataframe(self):
        storm_cols=['BEGIN_DATE_TIME','END_DATE_TIME','BEGIN_LON','BEGIN_LAT']
        storms_filtered=self.storms[storm_cols]

        # Extract and create column headings
        for heading in storms_filtered.columns:
            self.column_headings.add_widget(Label(text=heading))

        # Extract and create rows
        data = []
        for row in storms_filtered.itertuples():
            for i in range(1, len(row)):
                data.append([row[i], row[0]])
        self.rv_data = [{'text': str(x[0]), 'Index': str(x[1]), 'selectable': True} for x in data]

    def get_row(self, instance):
        self.row=self.rv_data[instance.index]['Index']
        print("get_row:",self.row)


    def view(self):
        if self.row:
            nexrad_Objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == int(self.row))]
            graph(nexrad_Objects)

class MainApp(App):
    def build(self):
        return Root()


Factory.register('Root', cls=Root)


if __name__ == '__main__':
    MainApp().run()