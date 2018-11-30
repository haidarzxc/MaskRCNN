import os, sys, inspect
import pandas as pd
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datasets.NCDC_stormevents_data_loader import load_CSV_file

from datasets.boto import create_session, \
                            iterate_nexrad_intersections, \
                            iterate_goes_intersections
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import boto3
import botocore

class Clip():
    storms=load_CSV_file('NCDC_stormevents/area_filtered_stormevents.csv')
    nexrad=load_CSV_file('NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv')
    goes=load_CSV_file('goes_intersections/GOES_datetime_filtered_intersections.csv')

    def __init__(self, **kwargs):
        super(Clip,self).__init__(**kwargs)
        self.nexrad=self.nexrad.sort_values(by=['bucket_begin_time'])
        self.goes=self.goes.sort_values(by=['bucket_begin_time'])
        self.iterate_storms(begin_start_date='01-DEC-17',
                            begin_end_date='31-DEC-17')


    def clip_Goes_object(self,goes_object,nexrad_object):
        goes_dir='goes_intersections/2017-12-01_2017-12-31/'
        if not Path(goes_dir+goes_object['KEY'].replace('/',"_")).is_file():
            iterate_goes_intersections(goes_object,goes_dir)
        if not Path('nexrad_intersections/'+nexrad_object['KEY']).is_file():
            iterate_nexrad_intersections(nexrad_object,'nexrad_intersections')


    def iterate_goes(self,nexrad_row,goes_objects):
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')
        if len(goes_objects)>0:

            goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])

            goes_30min_window=goes_objects['bucket_begin_time'].between_time(
                    str(nexrad_datetime.time()),
                    str((nexrad_datetime + timedelta(minutes=30)).time()))


            nearest_object_index=goes_objects['bucket_begin_time'].tolist().index(min(goes_objects['bucket_begin_time'],
                key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))

            self.clip_Goes_object(goes_objects.iloc[nearest_object_index],nexrad_row)
            # print("nearest_object",nearest_object_index,goes_objects.iloc[nearest_object_index],nexrad_datetime)

        else:
            print("No Goes objects")

    def get_intersected_objects(self,storm_row):
        nexrad_objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == storm_row.name)]
        goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == storm_row.name)]

        nexrad_objects.head(1).apply(lambda x: self.iterate_goes(x,goes_objects),axis=1)


    def iterate_storms(self,begin_start_date=None,begin_end_date=None):
        storms=self.storms
        storms['BEGIN_DATE_TIME']=storms['BEGIN_DATE_TIME'].apply(lambda x: pd.Timestamp(x))
        if begin_start_date and begin_end_date:

            begin_start_date=pd.Timestamp(begin_start_date)
            begin_end_date=pd.Timestamp(begin_end_date)
            storms=storms.loc[(storms['BEGIN_DATE_TIME'] > begin_start_date) &
                                (storms['BEGIN_DATE_TIME'] < begin_end_date)]


        storms.head(1).apply(self.get_intersected_objects,axis=1)



Clip()