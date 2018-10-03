
import boto3
import botocore
import os, sys, inspect
import pandas as pd
import numpy as np
from time import sleep
pd.options.mode.chained_assignment = None
import re

# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

import settings.local as local
from NCDC_stormevents_data_loader import load_CSV_file, get_NCDC_data,\
                                    retrieve_WSR_88D_RDA_locations
import utils.track as tr
from datasets.intersect import *

Track=tr.Track()


'''
RADAR CENTER LOCATION

                    HORIZONTAL_SHIFT
                    .-----------. (END_LON+HORIZONTAL_SHIFT,END_LAT+VERTICAL_SHIFT)
                    |           |
  VERTICAL_SHIFT    |     .<----|--center (x,y)
                    |           |
                    .-----------.
    (BEGIN_LON-HORIZONTAL_SHIFT,BEGIN_LAT-VERTICAL_SHIFT)


'''


def create_session():
    session = boto3.Session(
        aws_access_key_id=local.AWSAccessKeyId,
        aws_secret_access_key=local.AWSSecretKey,
    )
    return session.resource('s3')

def return_bucket(session):

    try:
        bucket=session.Bucket("noaa-nexrad-level2")
        # print(bucket.Object("1991/12/26/KTLX/KTLX19911226_025749.gz"))
        x=0
        for object in bucket.objects.all():
            object_dict=dict()

            # NOTE: KTLX19910605_162126.gz
            # format <SSSS><YYYY><MONTH><DAY>_<HOUR><MINUTE><SECOND>
            meta_data=object.key.split("/")[4].split('_')

            meta_data_time=meta_data[1].replace(".gz","")
            meta_data_date=meta_data[0]

            # time params
            object_dict["HOUR"]=meta_data_time[:2]
            object_dict["MIN"]=meta_data_time[2:4]
            object_dict["SEC"]=meta_data_time[4:6]

            # date params
            object_dict["DAY"]=meta_data_date[-2:]
            object_dict["MONTH"]=meta_data_date[-4:-2]
            object_dict["YEAR"]=meta_data_date[-8:-4]
            # station id
            object_dict["STD"]=meta_data_date[:-8]

            print(object_dict)
            if x==4:
                break
            x+=1

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

'''
intersction_test method
    arguments -> location: one row of radar locations
                            (ex: 0 KABR 452721 / 0982447  44.455833  97.413056  46.455833  99.413056)
                 storm: one row of storm event
                            (ex:0 39.6600 -75.0800 39.6600 -75.0800 NaN NaN)
    function -> create 4 points (x,y)
                1. location_begin_point
                2. location_end_point
                3. storm_begin_point
                4. storm_end_point
             -> create 2 boxes
                1.location_box
                2.storm_box
             -> calls function is_intersecting() to find if boxes intersect
                ->function returns boolean value
             -> returns row
'''

def intersction_test(location,storm):

    location_begin_point=Point(location['BEGIN_LON'],location['BEGIN_LAT'])
    location_end_point=Point(location['END_LON'],location['END_LAT'])

    storm_begin_point=Point(storm['BEGIN_LON'], storm['BEGIN_LAT'])
    storm_end_point=Point(storm['END_LON'],storm['END_LAT'])

    location_box=Box(location_begin_point,location_end_point)
    storm_box=Box(storm_begin_point, storm_end_point)

    intersection=is_intersecting(location_box,storm_box)

    if intersection:
        storm['STATIONID']=location['STATIONID']
        storm['IS_INTERSECTING']=True




    return storm

'''
filter_stormevents method
    arguments -> row      : one storm event row
                            (ex:0 39.6600 -75.0800 39.6600 -75.0800 NaN NaN)
              -> locations: pandas data frame contains all radar locations

    function -> for each row, function iterates accross locations
             -> returns row
'''

def filter_stormevents(row,locations):
    st=locations.apply(lambda x: intersction_test(x,row),axis=1)
    # sleep(3)
    Track.info("Testing "+str(row.name)+", "+str(row["IS_INTERSECTING"]))
    return row

def locations_lon_lat(row):
    # Decimal Degrees = degrees + (minutes/60) + (seconds/3600)
    # DD = d + (min/60) + (sec/3600)
    deg=row['LATN/LONGW(deg,min,sec)'].split('/')

    lon=deg[1].strip()
    lat=deg[0].strip()
    lon=re.sub('[^0-9]','', lon)
    lat=re.sub('[^0-9]','', lat)
    # sec [-2:] | min [-4:-2] | deg [:-4]
    try:

        lon_float=float(lon[:-4]) + (float(lon[-4:-2])/60) + (float(lon[-2:])/3600)
        lat_float=float(lat[:-4]) + (float(lat[-4:-2])/60) + (float(lat[-2:])/3600)

        row['BEGIN_LON']=lon_float-local.HORIZONTAL_SHIFT
        row['BEGIN_LAT']=lat_float-local.VERTICAL_SHIFT
        row['END_LON']=lon_float+local.HORIZONTAL_SHIFT
        row['END_LAT']=lat_float+local.VERTICAL_SHIFT
    except:
        Track.warn("Exception: Float Parsing ")


    return row

def get_data():
    session=create_session()
    Track.info("Session Created.")

    stormevents_csv_file=load_CSV_file("NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv")
    locations_csv_file=load_CSV_file("NCDC_stormevents/88D_locations.csv")

    locations_df=locations_csv_file[['STATIONID','LATN/LONGW(deg,min,sec)']]
    locations_df['BEGIN_LAT']=pd.Series()
    locations_df['BEGIN_LON']=pd.Series()
    locations_df['END_LAT']=pd.Series()
    locations_df['END_LON']=pd.Series()
    locations_df=locations_df.apply(locations_lon_lat, axis=1)

    stormevents_df=stormevents_csv_file[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON']]
    # stormevents_df dropping NaN rows
    stormevents_df=stormevents_df.dropna(thresh=2)
    stormevents_df['IS_INTERSECTING']=pd.Series()
    stormevents_df['STATIONID']=pd.Series()

    Track.info("Intersection Test")
    # stormevents_df=stormevents_df.apply(lambda x: filter_stormevents(x,locations_df), axis=1)
    # print("\n")
    print(locations_df.head(1))

    # print("\n")
    # print(stormevents_df.head(1))
    # print("\n")
    # return_bucket(session)








get_data()

# get_NCDC_data("NCDC_stormevents",2017)
# retrieve_WSR_88D_RDA_locations(local.WSR_88D_LOCATIONS,'NCDC_stormevents/88D_locations.csv')


