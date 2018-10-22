
import boto3
import botocore
import os, sys, inspect
import pandas as pd
import numpy as np
from time import sleep
pd.options.mode.chained_assignment = None
import re

import pytz
import datetime

# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

import settings.local as local
from NCDC_stormevents_data_loader import load_CSV_file, get_NCDC_data,\
                                    retrieve_WSR_88D_RDA_locations
import utils.track as tr
from utils.time import to_UTC_time,date_range_intersection_test
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



counter=0
total_size=0
intersections=pd.DataFrame()
intersections['KEY']=pd.Series()
intersections['SIZE']=pd.Series()
intersections['IS_BOX_INTERSECTING']=pd.Series()
intersections['IS_TIME_INTERSECTING']=pd.Series()
intersections['BEGIN_LAT']=pd.Series()
intersections['BEGIN_LON']=pd.Series()
intersections['END_LAT']=pd.Series()
intersections['END_LON']=pd.Series()
intersections['STATIONID']=pd.Series()
intersections['BEGIN_TIME_UTC']=pd.Series()
intersections['END_TIME_UTC']=pd.Series()
intersections['bucket_begin_time']=pd.Series()
intersections['bucket_end_time']=pd.Series()

def bucket_nexrad(row,session):
    global counter
    global total_size
    try:
        bucket=session.Bucket("noaa-nexrad-level2")

        # print(bucket.Object("1991/12/26/KTLX/KTLX19911226_025749.gz"))
        x=0

        # using row BEGIN_TIME_UTC and STATIONID
        # to construct prefix for bucket objects filter
        prefrix_datetime=row['BEGIN_TIME_UTC'].strftime("%Y/%m/%d")+"/"+row['STATIONID']

        for object in bucket.objects.filter(Prefix=prefrix_datetime):
            object_dict=dict()

            # NOTE: KTLX19910605_162126.gz
            # format <SSSS><YYYY><MONTH><DAY>_<HOUR><MINUTE><SECOND>
            meta_data=object.key.split("/")[4].split('_')
            # if not object.key.endswith(".gz"):
            #     continue
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

            # if not int(object_dict["YEAR"])==2017:
            #     print(object_dict["YEAR"],end='\r')
            #     continue

            # construct timestamp
            bucket_begin_time=datetime.datetime(int(object_dict["YEAR"]),
                                                int(object_dict["MONTH"]),
                                                int(object_dict["DAY"]),
                                                int(object_dict["HOUR"]),
                                                int(object_dict["MIN"]),
                                                int(object_dict["SEC"]))

            bucket_end_time=bucket_begin_time+pd.Timedelta(seconds=local.META_DATA_END_TIME_SEC_SHIFT)

            time_intersection=date_range_intersection_test(bucket_begin_time
                                        ,bucket_end_time,
                                        row['BEGIN_TIME_UTC'],
                                        row['END_TIME_UTC']
                                        )
            print(object.key,object.size,object_dict,time_intersection,x,row.name)

            # adding row to intersections
            if time_intersection:
                intersections.loc[counter]=[
                                        object.key,
                                        object.size*0.000001,
                                        row['IS_INTERSECTING'],
                                        time_intersection,
                                        row['BEGIN_LAT'],
                                        row['BEGIN_LON'],
                                        row['END_LAT'],
                                        row['END_LON'],
                                        row['STATIONID'],
                                        row['BEGIN_TIME_UTC'],
                                        row['END_TIME_UTC'],
                                        bucket_begin_time,
                                        bucket_end_time
                    ]
                counter+=1
                total_size+=object.size*0.000001
            # if x==4:
            #     break
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
# NOTE: for frontend csv
boxes={}
boxes['location_begin_point']=[]
boxes['location_end_point']=[]
boxes['storm_begin_point']=[]
boxes['storm_end_point']=[]

def intersction_test(location,storm):

    location_begin_point=Point(location['BEGIN_LON'],location['BEGIN_LAT'])
    location_end_point=Point(location['END_LON'],location['END_LAT'])

    storm_begin_point=Point(storm['BEGIN_LON'], storm['BEGIN_LAT'])
    storm_end_point=Point(storm['END_LON'],storm['END_LAT'])

    location_box=Box(location_begin_point,location_end_point)
    storm_box=Box(storm_begin_point, storm_end_point)

    # NOTE: for frontend csv
    boxes['location_begin_point'].append(location_begin_point)
    boxes['location_end_point'].append(location_end_point)
    boxes['storm_begin_point'].append(storm_begin_point)
    boxes['storm_end_point'].append(storm_end_point)

    intersection=is_intersecting(location_box,storm_box)

    if intersection:
        storm['STATIONID']=location['STATIONID']
        storm['IS_INTERSECTING']=True




    return storm




'''
filter_stormevents_nexrad method
    arguments -> row      : one storm event row
                            (ex:0 39.6600 -75.0800 39.6600 -75.0800 NaN NaN)
              -> locations: pandas data frame contains all radar locations

    function -> for each row, function iterates accross locations
             -> returns row
'''

def filter_stormevents_nexrad(row,locations,session):
    # space interestion test
    st=locations.apply(lambda x: intersction_test(x,row),axis=1)

    # time conversion to UTC
    to_UTC_time(row)

    # time range intersection test
    if row['IS_INTERSECTING'] == True:
        bucket_nexrad(row,session)



    Track.info("filter_stormevents_nexrad Testing Intersection "+str(row.name))
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

        # NOTE: all lon (longtudes) are negative
        lon_float=(float(lon[:-4]) + (float(lon[-4:-2])/60) + (float(lon[-2:])/3600))*-1
        lat_float=float(lat[:-4]) + (float(lat[-4:-2])/60) + (float(lat[-2:])/3600)

        row['BEGIN_LON']=lon_float-local.HORIZONTAL_SHIFT
        row['BEGIN_LAT']=lat_float-local.VERTICAL_SHIFT
        row['END_LON']=lon_float+local.HORIZONTAL_SHIFT
        row['END_LAT']=lat_float+local.VERTICAL_SHIFT
    except:
        Track.warn("Exception: Float Parsing ")


    return row

def iterate_intersections(row):

    try:
        session=create_session()
        bucket=session.Bucket("noaa-nexrad-level2")

        obj=bucket.Object(row['KEY'])
        print(obj.key,row.name)
        path="Radar_intersections/"+obj.key.replace("/","-")
        bucket.download_file(obj.key,path)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")


def download_intersections(output_dir):
    file=load_CSV_file(output_dir)
    file.apply(iterate_intersections,axis=1)

def get_data_size(output_dir,year="2017"):
    counter=0
    size_df=pd.DataFrame()
    size_df['KEY']=pd.Series()
    size_df['SIZE']=pd.Series()
    try:
        session=create_session()
        bucket=session.Bucket("noaa-nexrad-level2")
        objects=bucket.objects.filter(Prefix=year)
        for object in objects:
            print(object.key,object.size,counter)
            size_df.loc[counter]=[object.key,object.size*0.000001]
            counter+=1
        size_df.to_csv(output_dir)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

def get_data(output_dir_stormevents, output_dir_intersections, data_type):
    global intersections
    session=create_session()
    Track.info("Session Created.")

    stormevents_csv_file=load_CSV_file("NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv")

    if(data_type=="NEXRAD"):
        locations_csv_file=load_CSV_file("NCDC_stormevents/88D_locations.csv")

        locations_df=locations_csv_file[['STATIONID','LATN/LONGW(deg,min,sec)']]
        locations_df['BEGIN_LAT']=pd.Series()
        locations_df['BEGIN_LON']=pd.Series()
        locations_df['END_LAT']=pd.Series()
        locations_df['END_LON']=pd.Series()
        locations_df=locations_df.apply(locations_lon_lat, axis=1)

        stormevents_df=stormevents_csv_file[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON','BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]
        # stormevents_df dropping NaN rows
        stormevents_df=stormevents_df.dropna(thresh=2)
        stormevents_df['IS_INTERSECTING']=pd.Series()
        stormevents_df['STATIONID']=pd.Series()
        stormevents_df['BEGIN_TIME_UTC']=pd.Series()
        stormevents_df['END_TIME_UTC']=pd.Series()

        Track.info("Intersection Test")
        stormevents_df=stormevents_df.apply(lambda x: filter_stormevents_nexrad(x,locations_df,session), axis=1)


        # global df intersections "NCDC_stormevents/bounding_box_datetime_filtered_intersections.csv"
        intersections=intersections.drop_duplicates()
        intersections.to_csv(output_dir_intersections)


        stormevents_filtered_df=stormevents_df.loc[stormevents_df['IS_INTERSECTING'] == True]
        stormevents_filtered_df.to_csv(output_dir_stormevents)

    elif(data_type=="GOES"):
        print("GOES")
        stormevents_df=stormevents_csv_file[['BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]

        # stormevents_df dropping NaN rows
        stormevents_df=stormevents_df.dropna(thresh=2)
        stormevents_df['BEGIN_TIME_UTC']=pd.Series()
        stormevents_df['END_TIME_UTC']=pd.Series()



if __name__ == '__main__':
    Track.start_timer()
    # get_data("NCDC_stormevents/intersections.csv",
    #         "NCDC_stormevents/bounding_box_datetime_filtered_intersections.csv",
    #         "NEXRAD")

    # get_data("NCDC_stormevents/GOES_datetime_filtered_intersections.csv",
    #         "GOES")

    # download_intersections("NCDC_stormevents/bounding_box_datetime_filtered_intersections.csv")
    # get_data_size('NCDC_stormevents/size_2017.csv')


    # get_NCDC_data("NCDC_stormevents",2017)
    # retrieve_WSR_88D_RDA_locations(local.WSR_88D_LOCATIONS,'NCDC_stormevents/88D_locations.csv')
    Track.stop_timer()
    Track.get_exection_time()

