

# python libraries
import pandas as pd
import botocore
import re
import datetime
import os


# project modules
from datasets.NCDC_stormevents_data_loader import load_CSV_file
from utils.intersect import *
from utils.time import to_UTC_time
# from utils.general import verify_lon_lat
import settings.local as local
from utils.time import date_range_intersection_test

class NexradIntersectionTest():
    def __init__(self,session,track,storms,locations,local, **kwargs):

        if  session is None or \
            track is None or \
            storms is None or \
            locations is None or \
            local is None:
            return



        self.session=session
        self.track=track

        # create Log File
        self.track.createLogFile("./logs/nexrad_intersections_test.txt")

        self.storms=load_CSV_file("./NCDC_stormevents/"+storms)
        self.local=local
        self.output_dir="NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv"
        self.output_dir_txt="NCDC_stormevents/TXT_NEXRAD_bounding_box_datetime_filtered_intersections.csv"
        self.locations=load_CSV_file("./NCDC_stormevents/"+locations)


        # add columns to locations DataFrame
        locations_df=self.locations[['STATIONID','LATN/LONGW(deg,min,sec)']]
        locations_df = locations_df.assign(BEGIN_LAT=pd.Series())
        locations_df = locations_df.assign(BEGIN_LON=pd.Series())
        locations_df = locations_df.assign(END_LAT=pd.Series())
        locations_df = locations_df.assign(END_LON=pd.Series())
        locations_df=locations_df.apply(self.locations_lon_lat, axis=1)


        # add columns to stormevents DataFrame
        stormevents_df = stormevents_df.assign(IS_INTERSECTING=pd.Series())
        stormevents_df = stormevents_df.assign(STATIONID=pd.Series())
        stormevents_df = stormevents_df.assign(BEGIN_TIME_UTC=pd.Series())
        stormevents_df = stormevents_df.assign(END_TIME_UTC=pd.Series())


        # run space and datetime test
        self.track.info("Running Filter")
        stormevents_df=stormevents_df.apply(lambda x: self.filter_stormevents_nexrad(x,locations_df,session), axis=1)


        # read df nexrad_intersections -re format csv file
        header=["KEY","FOREIGN_KEY", "SIZE", "IS_INTERSECTING", "IS_TIME_INTERSECTING","BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "STATIONID", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"]
        nexrad_intersections=load_CSV_file(self.output_dir_txt,header)
        nexrad_intersections=nexrad_intersections.drop_duplicates(['KEY'])
        nexrad_intersections.to_csv(self.output_dir)

        os.remove(self.output_dir_txt)
        # stormevents_filtered_df=stormevents_df.loc[stormevents_df['IS_INTERSECTING'] == True]
        # stormevents_filtered_df.to_csv(self.output_dir)


    def locations_lon_lat(self,row):
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

            # verify lons and lats
            # method signiture BEGIN_LON,END_LON, BEGIN_LAT,END_LAT,track=None
            result=verify_lon_lat(
                lon_float-self.local.HORIZONTAL_SHIFT,
                lon_float+self.local.HORIZONTAL_SHIFT,
                lat_float-self.local.VERTICAL_SHIFT,
                lat_float+self.local.VERTICAL_SHIFT,
                self.track
            )

            row['BEGIN_LON']=result['BEGIN_LON']
            row['BEGIN_LAT']=result['BEGIN_LAT']
            row['END_LON']=result['END_LON']
            row['END_LAT']=result['END_LAT']

        except:
            self.track.warn("Exception: Float Parsing ")

        return row



    def filter_stormevents_nexrad(self,row,locations,session):

        # space interestion test
        st=locations.apply(lambda x: self.intersction_test(x,row),axis=1)

        # time conversion to UTC
        to_UTC_time(row)


        # time range intersection test
        if row['IS_INTERSECTING'] == True:
            self.bucket_nexrad(row,session)



        self.track.info("Nexrad filter test "+str(row.name))
        return row



    def intersction_test(self,location,storm):

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


    def bucket_nexrad(self,row,session):
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
                    with open(self.output_dir_txt, "a") as myfile:
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
                self.track.warn("Exception: The object does not exist.")
            else:
                raise
                self.track.warn("Exception: Error.")






