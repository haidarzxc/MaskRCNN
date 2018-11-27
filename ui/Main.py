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
from datetime import datetime
from datetime import timedelta


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

    def iterate(self,nexrad_row,goes_objects):
        # print(goes_objects['bucket_begin_time'].values)
        # print("---")
        # print(nexrad_row['bucket_begin_time'])
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')
        if len(goes_objects)>0:

            # goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])
            #
            # goes_30min_window=goes_objects['bucket_begin_time'].between_time(
            #         str(nexrad_datetime.time()),
            #         str((nexrad_datetime + timedelta(minutes=30)).time()))
            # print(goes_30min_window)

            nearest_object=min(goes_objects['bucket_begin_time'],
                key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime))
            print(nearest_object)
        else:
            print("No Goes objects")

    def clip(self,nexrad_objects,goes_objects):
        # print(len(nexrad_objects),len(goes_objects))
        nexrad_objects.head(1).apply(lambda x: self.iterate(x,goes_objects),axis=1)

    def view(self):
        if self.row:
            nexrad_Objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == int(self.row))]
            goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == int(self.row))]
            output_dir="ui_objects"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            nexrad_Objects=nexrad_Objects.sort_values(by=['bucket_begin_time'])
            goes_objects=goes_objects.sort_values(by=['bucket_begin_time'])
            self.clip(nexrad_Objects,goes_objects)
            # graph(nexrad_Objects,goes_objects)

class MainApp(App):
    def build(self):
        return Root()


Factory.register('Root', cls=Root)


if __name__ == '__main__':
    MainApp().run()