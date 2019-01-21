

# python libraries
import pandas as pd
import math

# project modules
from datasets.NCDC_stormevents_data_loader import load_CSV_file
from utils.intersect import *



'''
    top,Left            .----------.    storm_end_point
                        |          |    top,Right
                        |          |
                        |          |
    storm_begin_point   .----------.   bottom,Right
    bottom,left
'''

class AreaFilter():
    def __init__(self,track,storms,output_dir,local, **kwargs):
        self.track=track
        self.storms=storms
        self.output_dir=output_dir
        self.local=local

        self.bounding_box_area_filter()



    def calculate_distance(self,x1,x2,y1,y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def calculate_area(self,row):
        storm_begin_point=Point(row['BEGIN_LON'], row['BEGIN_LAT'])
        storm_end_point=Point(row['END_LON'],row['END_LAT'])
        # print((row['END_LON']-row['END_LAT'])*(row['BEGIN_LON']-row['BEGIN_LAT']))
        storm_box=Box(storm_begin_point, storm_end_point)
        width=self.calculate_distance(storm_box.bottom,
                                storm_box.bottom,
                                storm_box.left,
                                storm_box.right)

        height=self.calculate_distance(storm_box.bottom,
                                    storm_box.top,
                                    storm_box.left,
                                    storm_box.left)

        area=width*height
        # print(width,height,area)
        row['AREA']=area

        return row

    def bounding_box_area_filter(self):
        stormevents_csv_file=load_CSV_file("NCDC_stormevents/"+self.storms)

        stormevents_df=stormevents_csv_file[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON','BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]
        # stormevents_df dropping NaN rows
        stormevents_df=stormevents_df.dropna(thresh=2)
        stormevents_df['AREA']=pd.Series()

        self.track.info("AREA Calculation")
        stormevents_df=stormevents_df.apply(lambda x: self.calculate_area(x), axis=1)


        stormevents_df_sorted=stormevents_df.sort_values(by=['AREA'])
        stormevents_df_threshold=stormevents_df_sorted.loc[stormevents_df['AREA'] >= self.local.bounding_box_area_threshold]
        print(stormevents_df_threshold)

        stormevents_df_threshold.to_csv("NCDC_stormevents/"+self.output_dir)