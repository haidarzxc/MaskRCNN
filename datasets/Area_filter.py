from NCDC_stormevents_data_loader import load_CSV_file
import pandas as pd
import utils.track as tr
from datasets.intersect import *
import math
import settings.local as local


Track=tr.Track()

def calculate_distance(x1,x2,y1,y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

'''
    top,Left            .----------.    storm_end_point
                        |          |    top,Right
                        |          |
                        |          |
    storm_begin_point   .----------.   bottom,Right
    bottom,left
'''

def calculate_area(row):
    storm_begin_point=Point(row['BEGIN_LON'], row['BEGIN_LAT'])
    storm_end_point=Point(row['END_LON'],row['END_LAT'])
    # print((row['END_LON']-row['END_LAT'])*(row['BEGIN_LON']-row['BEGIN_LAT']))
    storm_box=Box(storm_begin_point, storm_end_point)
    width=calculate_distance(storm_box.bottom,
                            storm_box.bottom,
                            storm_box.left,
                            storm_box.right)

    height=calculate_distance(storm_box.bottom,
                                storm_box.top,
                                storm_box.left,
                                storm_box.left)

    area=width*height
    # print(width,height,area)
    row['AREA']=area

    return row



def bounding_box_area_filter(output_dir):
    stormevents_csv_file=load_CSV_file("NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv")

    stormevents_df=stormevents_csv_file[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON','BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]
    # stormevents_df dropping NaN rows
    stormevents_df=stormevents_df.dropna(thresh=2)
    stormevents_df['AREA']=pd.Series()

    Track.info("AREA Calculation")
    stormevents_df=stormevents_df.apply(lambda x: calculate_area(x), axis=1)


    stormevents_df_sorted=stormevents_df.sort_values(by=['AREA'])
    stormevents_df_threshold=stormevents_df_sorted.loc[stormevents_df['AREA'] >= local.bounding_box_area_threshold]
    print(stormevents_df_threshold)

    stormevents_df_threshold.to_csv(output_dir)