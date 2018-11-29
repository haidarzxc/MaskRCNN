
import boto3
import botocore
import os, sys, inspect
import pandas as pd
import numpy as np
from time import sleep
pd.options.mode.chained_assignment = None
import re
import math

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



def bucket_nexrad(row,session):
    try:
        bucket=session.Bucket("noaa-nexrad-level2")


        # using row BEGIN_TIME_UTC and STATIONID
        # to construct prefix for bucket objects filter
        prefrix_datetime=row['BEGIN_TIME_UTC'].strftime("%Y/%m/%d")+"/"+row['STATIONID']
        x=0
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
            print(object.key,object.size,time_intersection,x,row.name)

            # adding row to nexrad_intersections
            if time_intersection:
                with open("NCDC_stormevents/TXT_NEXRAD_bounding_box_datetime_filtered_intersections.csv", "a") as myfile:
                    rec=str(object.key)+ \
                    ","+str(row.name)+ \
                    ","+str(object.size*0.000001)+ \
                    ","+str(row['IS_INTERSECTING'])+ \
                    ","+str(time_intersection)+ \
                    ","+str(row['BEGIN_LAT'])+ \
                    ","+str(row['BEGIN_LON'])+ \
                    ","+str(row['END_LAT'])+ \
                    ","+str(row['END_LON'])+ \
                    ","+str(row['STATIONID'])+ \
                    ","+str(row['BEGIN_TIME_UTC'])+ \
                    ","+str(row['END_TIME_UTC'])+ \
                    ","+str(bucket_begin_time)+ \
                    ","+str(bucket_end_time)+ \
                    "\n"
                    myfile.write(rec)

            print(object.key,object.size,time_intersection,x,row.name)
            x+=1

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

def bucket_goes(row,session):
    try:
        bucket=session.Bucket("noaa-goes16")

        # format
        # <Product>/<Year>/<Day of Year>/<Hour>/<Filename>
        #
        # where:
        #
        #     <Product> is the product generated from one of
        #             the sensors aboard the satellite (e.g.)
        #             ABI-L1b-RadF
        #             ABI-L1b-RadC
        #             ABI-L1b-RadM
        #     <Year> is the year the netCDF4 file was created
        #     <Day of Year> is the numerical day of the year (1-365)
        #     <Hour> is the hour the data observation was made
        #     <Filename> is the name of the file containing the data.
        #      These are compressed and encapsulated using the netCDF4
        #      standard.

        # s20171671145342: is start of scan time
        #     4 digit year
        #     3 digit day of year
        #     2 digit hour
        #     2 digit minute
        #     2 digit second
        #     1 digit tenth of second

        prefrix_datetime="ABI-L1b-RadC"+"/"+row['BEGIN_TIME_UTC'].strftime("%Y/%j")
        x=0
        for object in bucket.objects.filter(Prefix=prefrix_datetime):

            meta_data=object.key.split('_')
            # slicing year[1:5] dayOfYear[5:8] hour[8:10] minute[10:12] second[12:14]
            strrr=meta_data[3][12:14]
            bucket_begin_time=datetime.datetime(int(meta_data[3][1:5]),
                                                1,
                                                1,
                                                int(meta_data[3][8:10]),
                                                int(meta_data[3][10:12]),
                                                int(meta_data[3][12:14])
                                                ) + datetime.timedelta(int(meta_data[3][5:8]) - 1)

            bucket_end_time=datetime.datetime(int(meta_data[4][1:5]),
                                                1,
                                                1,
                                                int(meta_data[4][8:10]),
                                                int(meta_data[4][10:12]),
                                                int(meta_data[4][12:14])
                                                ) + datetime.timedelta(int(meta_data[4][5:8]) - 1)

            time_intersection=date_range_intersection_test(bucket_begin_time
                                        ,bucket_end_time,
                                        row['BEGIN_TIME_UTC'],
                                        row['END_TIME_UTC']
                                        )
            if time_intersection:

                with open("NCDC_stormevents/TXT_GOES_datetime_filtered_intersections.csv", "a") as myfile:
                    rec=str(object.key)+ \
                        ","+str(row.name)+ \
                        ","+str(object.size*0.000001)+ \
                        ","+str(time_intersection)+ \
                        ","+str(row['BEGIN_TIME_UTC'])+ \
                        ","+str(row['END_TIME_UTC'])+ \
                        ","+str(bucket_begin_time)+ \
                        ","+str(bucket_end_time)+ \
                        "\n"
                    myfile.write(rec)

            print(object.key,object.size,time_intersection,x,row.name)
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

def filter_stormevents_goes(row,session):
    # time conversion to UTC
    to_UTC_time(row)

    bucket_goes(row,session)
    Track.info("filter_stormevents_goes Testing Intersection "+str(row.name))
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

def iterate_nexrad_intersections(row,output_dir):
    global total
    try:
        session=create_session()
        bucket=session.Bucket("noaa-nexrad-level2")

        os.chdir(os.path.dirname(os.path.realpath(output_dir)).split(output_dir)[0])

        obj=bucket.Object(row['KEY'])

        rep=row['KEY'].rpartition("/")
        path=output_dir+"/"+rep[0]
        if not os.path.exists(path):
            os.makedirs(path)


        os.chdir(path)
        bucket.download_file(obj.key,rep[2])
        total+=(obj.get()['ContentLength']*0.000001)
        Track.info(str(obj.key)+", "+str(row.name)+", "+path+", "+str(total))
        print(obj.key,row.name,path,total)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

def iterate_goes_intersections(row,output_dir):
    global total
    try:
        session=create_session()
        bucket=session.Bucket("noaa-goes16")
        obj=bucket.Object(row['KEY'])
        bucket.download_file(obj.key,output_dir+"/"+obj.key.replace('/',"_"))
        total+=(obj.get()['ContentLength']*0.000001)
        Track.info(str(obj.key)+", "+str(row.name)+", "+output_dir+", "+str(total))
        print(obj.key,row.name,output_dir,total)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

total=0
def download_intersections(bucket,input_dir,output_dir):

    file=load_CSV_file(input_dir)
    file=file.sort_values(by='KEY')
    file=file.drop_duplicates(['KEY'])
    Track.createLogFile(output_dir+"/log.log")
    if bucket=="noaa-goes16":
        file.apply(lambda x:iterate_goes_intersections(x,output_dir),axis=1)
    elif bucket=="noaa-nexrad-level2":
        file.apply(lambda x:iterate_nexrad_intersections(x,output_dir),axis=1)
    Track.info("total volume (mb): "+str(total))

total_volume=0
def iterate_intersections_v1(row):
    global total_volume
    total_volume+=row['SIZE']
    print(row.name,row['SIZE'],total_volume)

def get_file_size(input_dir):
    file=load_CSV_file(input_dir,["KEY", "SIZE", "IS_TIME_INTERSECTING", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"])
    file=file.drop_duplicates(['KEY'])
    file.apply(lambda x:iterate_intersections_v1(x),axis=1)
    print(total_volume)


def get_goes_size(bucket,
                    output_dir=None,
                    product='ABI-L1b-RadC',
                    year="2017",
                    start_date=None,
                    end_date=None,
                    channel=None):
    counter=0
    total_volume=0
    try:
        if not os.path.exists(output_dir):
            file=open(output_dir, 'w+')
            file.close()
        session=create_session()
        bucket=session.Bucket(bucket)
        objects=[]
        if start_date and end_date:
            start=datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
            end=datetime.datetime.strptime(end_date,'%Y-%m-%d').date()
            start_dayOfYear=datetime.datetime.strftime(start,'%j')
            end_dayOfYear=datetime.datetime.strftime(end,'%j')
            dayOfYear=list(range(int(start_dayOfYear), (int(end_dayOfYear)+1)))

            for day in dayOfYear:
                day_object=datetime.datetime.strptime(str(day),'%j').date()
                day_object_dayOfYear=datetime.datetime.strftime(day_object,'%j')
                objects=bucket.objects.filter(Prefix=product+"/"+year+'/'+day_object_dayOfYear)
                print(year,day_object_dayOfYear)
                for object in objects:
                    split_object_key=object.key.split('/')
                    split_object_filename=split_object_key[4].split('_')
                    if channel:
                        object_channel=split_object_filename[1].split('-')[3]
                        if not object_channel[2:]==channel:
                            continue
                    print(object.key,object.size,counter)
                    total_volume+=object.size
                    with open(output_dir, "a") as myfile:
                        rec=str(object.key)+ \
                            ","+str(object.size*0.000001)+ \
                            "\n"
                        myfile.write(rec)
                    counter+=1
            data=load_CSV_file(output_dir,['KEY','SIZE'])
            data.to_csv(output_dir)
            print(total_volume)


    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            Track.warn("The object does not exist.")
        else:
            raise
            Track.warn("Error.")

def get_data(output_dir_intersections, data_type):

    session=create_session()
    Track.info("Session Created.")

    stormevents_csv_file=load_CSV_file("NCDC_stormevents/area_filtered_stormevents.csv")

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

        Track.info("NEXRAD Intersection Test")
        stormevents_df=stormevents_df.apply(lambda x: filter_stormevents_nexrad(x,locations_df,session), axis=1)


        # df nexrad_intersections
        header=["KEY","FOREIGN_KEY", "SIZE", "IS_INTERSECTING", "IS_TIME_INTERSECTING","BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "STATIONID", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"]
        nexrad_intersections=load_CSV_file("NCDC_stormevents/TXT_NEXRAD_bounding_box_datetime_filtered_intersections.csv",header)
        nexrad_intersections=nexrad_intersections.drop_duplicates(['KEY'])
        nexrad_intersections.to_csv(output_dir_intersections)


        stormevents_filtered_df=stormevents_df.loc[stormevents_df['IS_INTERSECTING'] == True]
        stormevents_filtered_df.to_csv(output_dir_stormevents)

    elif(data_type=="GOES"):
        print("GOES")
        stormevents_df=stormevents_csv_file[['BEGIN_DATE_TIME','CZ_TIMEZONE','END_DATE_TIME']]

        # stormevents_df dropping NaN rows
        stormevents_df=stormevents_df.dropna(thresh=2)
        stormevents_df['BEGIN_TIME_UTC']=pd.Series()
        stormevents_df['END_TIME_UTC']=pd.Series()

        Track.info("GOES Intersection Test")
        stormevents_df=stormevents_df.apply(lambda x: filter_stormevents_goes(x,session), axis=1)

        # df goes_intersections

        header=["KEY","FOREIGN_KEY", "SIZE", "IS_TIME_INTERSECTING", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"]
        goes_intersections=load_CSV_file("NCDC_stormevents/TXT_GOES_datetime_filtered_intersections.csv",header)
        goes_intersections=goes_intersections.drop_duplicates(['KEY'])
        goes_intersections.to_csv(output_dir_intersections)



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

    storm_box=Box(storm_begin_point, storm_end_point)

    width=calculate_distance(storm_box.top,
                            storm_box.top,
                            storm_box.left,
                            storm_box.right)

    height=calculate_distance(storm_box.bottom,
                                storm_box.bottom,
                                storm_box.left,
                                storm_box.right)
    # print(width,height)

    area=width*height
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




if __name__ == '__main__':
    Track.start_timer()
    # bounding_box_area_filter("NCDC_stormevents/area_filtered_stormevents.csv")

    # get_data(
    #         "NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv",
    #         "NEXRAD")

    # get_data(
    #         "NCDC_stormevents/GOES_datetime_filtered_intersections.csv",
    #         "GOES")


    # download_intersections("NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv","nexrad_intersections")
    download_intersections("noaa-goes16","NCDC_stormevents/TXT_data_size.csv","goes_intersections/2017-12-01_2017-12-31")



    # get_goes_size("noaa-goes16",
    #                 output_dir='NCDC_stormevents/TXT_data_size.csv',
    #                 product="ABI-L1b-RadC",
    #                 year="2017",
    #                 start_date='2017-12-01',
    #                 end_date='2017-12-31'
    #                 )
    # get_file_size('goes_intersections/TXT_GOES_datetime_filtered_intersections.csv')

    # get_NCDC_data("NCDC_stormevents",2017)
    # retrieve_WSR_88D_RDA_locations(local.WSR_88D_LOCATIONS,'NCDC_stormevents/88D_locations.csv')
    Track.stop_timer()
    Track.get_exection_time()

