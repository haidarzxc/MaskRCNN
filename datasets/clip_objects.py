# python libraries
import os, sys, inspect
import pandas as pd
import numpy as np
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from netCDF4 import Dataset
import pyart
# from mpl_toolkits.basemap import Basemap, cm
import math

# project modules
from datasets.NCDC_stormevents_data_loader import load_CSV_file
from utils.boto import create_session
from datasets.download_intersections import iterate_nexrad_intersections, \
                                            iterate_goes_intersections
from datasets.Frame import Frame
import settings.local as local
from datasets.trainingObject import TrainingObject


class Clip():

    # constructor
    def __init__(self,storms_dir,nexrad_dir,goes_dir,
                track,year,output_dir,train_dir,storm_id=None, **kwargs):
        super(Clip,self).__init__(**kwargs)

        self.track=track
        self.year=year
        self.output_dir=output_dir
        self.train_dir='./'+train_dir

        # create Log File
        self.track.createLogFile("./logs/clip.txt")
        self.track.start_timer()
        self.track.info(str(self.track.get_start_time()))


        # load CSVs storms, nexrad, and goes
        self.storms=load_CSV_file("NCDC_stormevents/"+storms_dir)
        self.nexrad=load_CSV_file("NCDC_stormevents/"+nexrad_dir)
        self.goes=load_CSV_file(goes_dir)
        self.track.info("loaded Storms, nexrad and goes csvs")

        self.nexrad=self.nexrad.sort_values(by=['bucket_begin_time'])
        self.goes=self.goes.sort_values(by=['bucket_begin_time'])
        self.track.info("sorted nexrad and goes by bucket_begin_time")


        # training dataset directory
        self.track.info("check if training dataset directory exists")
        if not os.path.exists(self.train_dir):
            os.mkdir(self.train_dir)
            track.info("created directory: "+str(self.train_dir))
        # create instances
        self.instances=TrainingObject(self.track,self.year,self.output_dir)
        self.track.info("created instance of training object")

        # filters storms for month december 2017
        self.track.info("begin iteration")
        self.iterate_storms(begin_start_date='01-OCT-18',
                            begin_end_date='31-OCT-18',
                            storm_id=storm_id)

        self.instances.dump_instances()

        self.track.stop_timer()
        self.track.info(str(self.track.get_end_time()))


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

    def clip_nexrad(self, radar, storm_row):

        refl_grid = radar.get_field(0, 'reflectivity')


        # gatefilter = pyart.filters.GateFilter(radar)
        # gatefilter.exclude_transition()
        # gatefilter.exclude_masked('reflectivity')

        # grid = pyart.map.grid_from_radars(
        #         (radar,),
        #         # gatefilters=(gatefilter, ),
        #         grid_shape=(1, 241, 241),
        #         grid_limits=((2000, 2000),
        #                     (-123000.0, 123000.0),
        #                     (-123000.0, 123000.0)),
        #         fields=['reflectivity'])

        # read_grid=radar.fields['reflectivity']['data']
        # print("read_grid ",read_grid)

        s_x0=storm_row['BEGIN_LON']
        s_y0=storm_row['BEGIN_LAT']
        s_x1=storm_row['END_LON']
        s_y1=storm_row['END_LAT']


        # print("nexrad object refl_grid", refl_grid)
        # print("nexrad object rows", len(refl_grid))
        # print("nexrad object columns", len(refl_grid[0]))
        clipped=refl_grid[
            :700,
            :700]
        # clipped= grid.fields['reflectivity']['data'][0]
        # print(clipped)
        return clipped


    def clip_object(self,goes_object,nexrad_object,storm_row):
        # download nexrad or goes objects of not found on disk
        if not Path(local.GOES_DIR+goes_object['KEY'].replace('/',"_")).is_file():
            iterate_goes_intersections(goes_object,local.GOES_DIR)
        if not Path(local.NEXRAD_DIR+nexrad_object['KEY']).is_file():
            current_working_dir=os.getcwd()
            iterate_nexrad_intersections(nexrad_object,local.NEXRAD_DIR)
            os.chdir(current_working_dir)

        # read goes object ; goes_netCdf.variables
        goes_netCdf= Dataset(local.GOES_DIR+goes_object['KEY'].replace('/',"_"),"r")
        # read nexrad object
        radar = pyart.io.read_nexrad_archive(local.NEXRAD_DIR+nexrad_object['KEY'])
        self.track.info("Loaded GOES and NEXRAD OBJECT")

        # clip goes and nexrad
        self.track.info("Clipping: GOES and NEXRAD objects")
        clip_goes=self.clip_goes(goes_netCdf,storm_row)
        clip_nexrad=self.clip_nexrad(radar,storm_row)

        goes_netCdf.close()

        # add instance
        self.track.info(str(storm_row)+", Nexrad_id: "+str(nexrad_object.name)+", Goes_id: "+str(goes_object.name))
        print("storm_id",storm_row.name,",Nexrad_id:",nexrad_object.name,",Goes_id:",goes_object.name)

        self.instances.current_image_dir=self.train_dir+"/GOES_train_"+str(storm_row.name)+"_"+str(nexrad_object.name)+"_"+str(goes_object.name)+".jpg"
        self.track.info("set image directory: "+self.instances.current_image_dir)
        self.instances.generate_segmentation_image(radar)
        self.track.info("generated image segmentation")
        self.instances.generate_training_images(clip_goes)
        self.track.info("generated training image")
        self.instances.create_training_instance(storm_row,goes_object,len(clip_goes),len(clip_goes[0]))
        self.track.info("created training instance")

        # graph and export
        # Frame(clip_goes,clip_nexrad,nexrad_object,goes_object)


    def iterate_goes(self,nexrad_row,goes_objects,storm_row):

        # format nexrad object bucket_begin_time
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')

        # set goes dataframe index to bucket_begin_time instead of integers
        goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])

        # find goes objects between nexrad bucket_begin_time and next 30 minutes
        goes_30min_window=goes_objects['bucket_begin_time'].between_time(
                str(nexrad_datetime.time()),
                str((nexrad_datetime + timedelta(minutes=30)).time()))

        # reset index back to integers
        goes_objects=goes_objects.reset_index(drop=True)

        # find nearest goes object index
        nearest_object_index=goes_objects['bucket_begin_time'].tolist().index(min(goes_objects['bucket_begin_time'],
            key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))

        # clip nearest goes object
        self.clip_object(goes_objects.iloc[nearest_object_index],nexrad_row,storm_row)
        # print("nearest_object",nearest_object_index,goes_objects.iloc[nearest_object_index],nexrad_datetime)

    def get_intersected_objects(self,storm_row):
        # get NEXRAD AND GOES objects given storm row
        nexrad_objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == storm_row.name)]
        goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == storm_row.name)]
        # print("nexrad_objects",len(nexrad_objects),"goes_objects",len(goes_objects),"------------------------")
        self.track.info("nexrad_objects: "+str(len(nexrad_objects))+",goes_objects: "+str(len(goes_objects)))

        if len(nexrad_objects)==0:
            self.track.info("No NEXRAD objects")
            return
        if len(goes_objects)==0:
            self.track.info("No GOES objects")
            return

        # ------REMOVE head(1)
        # for each nexrad object, iterate intersected goes objects.
        nexrad_objects.apply(lambda x: self.iterate_goes(x,goes_objects,storm_row),axis=1)


    def iterate_storms(self,begin_start_date=None,begin_end_date=None, storm_id=None):

        # change storm BEGIN_DATE_TIME to Timestamp type
        self.storms['BEGIN_DATE_TIME']=self.storms['BEGIN_DATE_TIME'].apply(lambda x: pd.Timestamp(x))

        # filter by given BEGIN start_date and end_date
        if begin_start_date and begin_end_date:
            begin_start_date=pd.Timestamp(begin_start_date)
            begin_end_date=pd.Timestamp(begin_end_date)
            self.storms=self.storms.loc[(self.storms['BEGIN_DATE_TIME'] > begin_start_date) &
                                (self.storms['BEGIN_DATE_TIME'] < begin_end_date)]

        # NO RESET INDEX SINCE STORM ID IS USED TO FOREGIN_KEY
        # self.storms=self.storms.reset_index(drop=True)

        # filter by given storm ID
        if not storm_id is None:
            print("ID:",storm_id)
            print(self.storms.iloc[storm_id])
            self.get_intersected_objects(self.storms.iloc[storm_id])
            return

        # get intersections
        self.storms.apply(self.get_intersected_objects,axis=1)





