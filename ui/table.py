from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

import os, sys, inspect
import pandas as pd
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

from datasets.NCDC_stormevents_data_loader import load_CSV_file

class TableHeader(Label):
    pass


class Record(Label):
    pass


upperbound=1
lowerbound=0

def next(x,y):
    global upperbound
    upperbound=x
    lowerbound=y

def prevous(x,y):
    global upperbound
    upperbound=x
    lowerbound=y

class Grid(GridLayout):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.cols = 4
        self.size_hint_y= None
        self.bind(minimum_height=self.setter('height'))
        self.spacing= '1dp'
        self.fetchData()
        self.renderData()

    def fetchData(self):
        storm_cols=['BEGIN_DATE_TIME','END_DATE_TIME','BEGIN_LON','BEGIN_LAT']
        storms=load_CSV_file('NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv')
        storms_header=pd.DataFrame([storm_cols],columns=storm_cols)

        storms_filtered=storms[storm_cols]
        storms_header=storms_header.append(storms_filtered, ignore_index=True)
        print(storms_header[0:upperbound])
        storms_header=storms_header.head(10).to_dict('records')

        # storms_header=storms_header[0:upperbound].to_dict('records')
        self.data=storms_header


    def renderData(self):
        self.clear_widgets()
        for i in range(len(self.data)):
            if i < 1:
                row = self.createHeader(i)
            else:
                row = self.createRecord(i)
            for item in row:
                self.add_widget(item)


    def createHeader(self, i):
        x=[]
        for k in self.data[i]:
            column = TableHeader(text=str(self.data[i][k]))
            x.append(column)
        return x

    def createRecord(self, i):
        x=[]
        for k in self.data[i]:
            column = Record(text=str(self.data[i][k]))
            x.append(column)
        return x