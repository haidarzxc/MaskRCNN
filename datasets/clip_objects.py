import os, sys, inspect
import pandas as pd
import numpy as np
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datasets.NCDC_stormevents_data_loader import load_CSV_file

from utils.boto import create_session
from datasets.download_intersections import iterate_nexrad_intersections, \
                                            iterate_goes_intersections
from datasets.Frame import Frame
import settings.local as local
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import boto3
import botocore
from netCDF4 import Dataset
import pyart


from mpl_toolkits.basemap import Basemap, cm
import math





class Clip():
    # load CSVs storms, nexrad, and goes
    storms=load_CSV_file('NCDC_stormevents/area_filtered_stormevents.csv')
    nexrad=load_CSV_file('NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv')
    goes=load_CSV_file('goes_intersections/GOES_datetime_filtered_intersections.csv')

    # constructor
    def __init__(self,storm_id=None, **kwargs):
        super(Clip,self).__init__(**kwargs)
        self.nexrad=self.nexrad.sort_values(by=['bucket_begin_time'])
        self.goes=self.goes.sort_values(by=['bucket_begin_time'])

        # filters storms for month december 2017
        self.iterate_storms(begin_start_date='01-DEC-17',
                            begin_end_date='31-DEC-17',
                            storm_id=storm_id)


    def clip_goes(self,goes_netCdf,storm_row):
        data=goes_netCdf['Rad']

        g_w=2500
        g_h=1500

        g_x0=-152.109282
        g_y0=14.571340
        g_x1=-52.946879
        g_y1=56.761450

        s_x0=storm_row['BEGIN_LON']
        s_y0=storm_row['BEGIN_LAT']
        s_x1=storm_row['END_LON']
        s_y1=storm_row['END_LAT']

        '''
                        2500
                .----------|----------.(g_x1,g_y1)
                |          |          |
        1500 ---|----------|----------|---
                |          |          |
    (g_x0,g_y0) .----------|----------.
                           |
        '''
        s_x=(g_x1-g_x0)/g_w
        s_y=(g_y1-g_y0)/g_h
        # print("s_x",s_x,"s_y",s_y)

        c0=(s_x0-g_x0)/s_x
        c1=(s_x1-g_x0)/s_x
        r0=(s_y0-g_y0)/s_y
        r1=(s_y1-g_y0)/s_y

        # print(c0,c1,r0,r1)

        c0_int=abs(math.floor(c0))
        c1_int=abs(math.ceil(c1))
        r0_int=abs(math.floor(r0))
        r1_int=abs(math.ceil(r1))
        # print("r0_int",r0_int,
        #       "r1_int",r1_int,
        #       "c0_int",c0_int,
        #       "c1_int",c1_int)
        # [r0..r1,c0..c1]
        clipped=data[
        r0_int+local.goes_margin_left:r1_int+local.goes_margin_right,
        c0_int+local.goes_margin_top:c1_int+local.goes_margin_bottom]
        # print(clipped)
        return clipped

    def clip_nexrad(self, nexrad_object, storm_row):
        radar = pyart.io.read_nexrad_archive('nexrad_intersections/'+nexrad_object['KEY'])
        refl_grid = radar.get_field(0, 'reflectivity')

        # read_grid=pyart.io.read('nexrad_intersections/'+nexrad_object['KEY'])
        # nexrad_netCdf= Dataset('nexrad_intersections/'+nexrad_object['KEY'],"r")
        # read_grid=radar.get_field(1, 'metadata')
        # print("read_grid ",read_grid)

        s_x0=storm_row['BEGIN_LON']
        s_y0=storm_row['BEGIN_LAT']
        s_x1=storm_row['END_LON']
        s_y1=storm_row['END_LAT']


        print("nexrad object refl_grid", refl_grid)
        print("nexrad object rows", len(refl_grid))
        print("nexrad object columns", len(refl_grid[0]))
        clipped=refl_grid[
            :720,
            :1832]
        # print(clipped)
        return clipped


    def clip_object(self,goes_object,nexrad_object,storm_row):
        # download nexrad or goes objects of not found on disk
        goes_dir='goes_intersections/2017-12-01_2017-12-31/'
        if not Path(goes_dir+goes_object['KEY'].replace('/',"_")).is_file():
            iterate_goes_intersections(goes_object,goes_dir)
        if not Path('nexrad_intersections/'+nexrad_object['KEY']).is_file():
            current_working_dir=os.getcwd()
            iterate_nexrad_intersections(nexrad_object,'nexrad_intersections')
            os.chdir(current_working_dir)

        # read goes object
        goes_netCdf= Dataset(goes_dir+goes_object['KEY'].replace('/',"_"),"r")

        # print(goes_netCdf.variables)

        # clip goes and nexrad
        clip_goes=self.clip_goes(goes_netCdf,storm_row)
        clip_nexrad=self.clip_nexrad(nexrad_object,storm_row)
        # print(storm_row)
        # graph and export
        Frame(clip_goes,clip_nexrad,nexrad_object,goes_object)

        # goes_netCdf.close()


    def iterate_goes(self,nexrad_row,goes_objects,storm_row):
        # format nexrad object bucket_begin_time
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')

        # check if goes objects exists
        if len(goes_objects)>0:
            # set goes dataframe index to bucket_begin_time instead of integers
            goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])

            # find goes objects between nexrad bucket_begin_time and next 30 minutes
            goes_30min_window=goes_objects['bucket_begin_time'].between_time(
                    str(nexrad_datetime.time()),
                    str((nexrad_datetime + timedelta(minutes=30)).time()))


            # find nearest goes object index
            nearest_object_index=goes_objects['bucket_begin_time'].tolist().index(min(goes_objects['bucket_begin_time'],
                key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))

            # clip nearest goes object
            self.clip_object(goes_objects.iloc[nearest_object_index],nexrad_row,storm_row)
            # print("nearest_object",nearest_object_index,goes_objects.iloc[nearest_object_index],nexrad_datetime)

        else:
            print("No Goes objects")

    def get_intersected_objects(self,storm_row):
        # get NEXRAD AND GOES objects given storm row
        nexrad_objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == storm_row.name)]
        goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == storm_row.name)]
        print("nexrad_objects",len(nexrad_objects),"goes_objects",len(goes_objects),"------------------------")
        # ------REMOVE head(1)
        # for each nexrad object, iterate intersected goes objects.
        nexrad_objects.head(1).apply(lambda x: self.iterate_goes(x,goes_objects,storm_row),axis=1)


    def iterate_storms(self,begin_start_date=None,begin_end_date=None, storm_id=None):

        # change storm BEGIN_DATE_TIME to Timestamp type
        self.storms['BEGIN_DATE_TIME']=self.storms['BEGIN_DATE_TIME'].apply(lambda x: pd.Timestamp(x))

        # filter by given BEGIN start_date and end_date
        if begin_start_date and begin_end_date:
            begin_start_date=pd.Timestamp(begin_start_date)
            begin_end_date=pd.Timestamp(begin_end_date)
            self.storms=self.storms.loc[(self.storms['BEGIN_DATE_TIME'] > begin_start_date) &
                                (self.storms['BEGIN_DATE_TIME'] < begin_end_date)]

        self.storms=self.storms.reset_index(drop=True)
        # filter by given storm ID
        if not storm_id is None:
            print("ID:",storm_id)
            print(self.storms.iloc[storm_id])
            self.get_intersected_objects(self.storms.iloc[storm_id])
            return

        # get intersections
        self.storms.apply(self.get_intersected_objects,axis=1)



Clip(1)