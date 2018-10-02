
import boto3
import botocore
import os, sys, inspect
import pandas as pd
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

Track=tr.Track()


'''
                    HORIZONTAL_SHIFT
             (VX,VY).-----------. (END_LON,END_LAT)
                    |           |
  VERTICAL_SHIFT    |           |
                    |           |
                    .-----------.
    (BEGIN_LON,BEGIN_LAT)       (HX,HY)
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

def addPoints(row,locations):
    # print(locations['LON'])
    # row["VX"]=row["BEGIN_LON"]
    # row["VY"]=row["BEGIN_LAT"]+local.VERTICAL_SHIFT
    # row["HX"]=row["BEGIN_LON"]+local.HORIZONTAL_SHIFT
    # row["HY"]=row["BEGIN_LAT"]
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
        row['LON']=float(lon[:-4]) + (float(lon[-4:-2])/60) + (float(lon[-2:])/3600)
        row['LAT']=float(lat[:-4]) + (float(lat[-4:-2])/60) + (float(lat[-2:])/3600)
        row['END_LON']=float(row['LON'])+local.HORIZONTAL_SHIFT
        row['END_LAT']=float(row['LAT'])+local.VERTICAL_SHIFT
    except:
        Track.warn("Exception: Float Parsing ")


    # NOTE: or keep as it is
    # deg=row['LATN/LONGW(deg,min,sec)'].split('/')
    # row['LON']=deg[1].strip()[:-4]
    # row['LAT']=deg[0].strip()[:-4]
    # row['END_LON']=int(row['LON'])+local.HORIZONTAL_SHIFT
    # row['END_LAT']=int(row['LAT'])+local.VERTICAL_SHIFT

    return row

def get_data():
    session=create_session()
    Track.info("Session Created.")

    stormevents_csv_file=load_CSV_file("NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv")
    locations_csv_file=load_CSV_file("NCDC_stormevents/88D_locations.csv")
    locations_df=locations_csv_file[['STATIONID','LATN/LONGW(deg,min,sec)']]
    locations_df['LAT']=pd.Series()
    locations_df['LON']=pd.Series()
    locations_df['END_LAT']=pd.Series()
    locations_df['END_LON']=pd.Series()
    locations_df=locations_df.apply(locations_lon_lat, axis=1)
    stormevents_df=stormevents_csv_file[['BEGIN_LAT','BEGIN_LON','END_LAT','END_LON']]

    # stormevents_df=stormevents_df.head(1).apply(lambda x: addPoints(x,locations_df), axis=1)
    print("\n")
    print(locations_df.head(1))
    print("\n")
    print(stormevents_df.head(1))
    print("\n")
    # return_bucket(session)







get_data()

# get_NCDC_data("NCDC_stormevents",2017)
# retrieve_WSR_88D_RDA_locations(local.WSR_88D_LOCATIONS,'NCDC_stormevents/88D_locations.csv')


