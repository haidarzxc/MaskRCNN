
# python libraries
import pandas as pd
import botocore
import datetime
import os

# project modules
from NCDC_stormevents_data_loader import load_CSV_file
from utils.time import to_UTC_time, date_range_intersection_test

class GoesIntersectionTest:
    def __init__(self,session,track,storms,local, **kwargs):
        self.session=session
        self.track=track
        self.storms=load_CSV_file("./NCDC_stormevents/"+storms)
        self.local=local
        self.output_dir="NCDC_stormevents/GOES_datetime_filtered_intersections.csv"
        self.output_dir_txt="NCDC_stormevents/TXT_GOES_datetime_filtered_intersections.csv"
        # create Log File
        self.track.createLogFile("./logs/goes_intersections_test.txt")


        self.storms = self.storms.assign(BEGIN_TIME_UTC=pd.Series())
        self.storms = self.storms.assign(END_TIME_UTC=pd.Series())

        self.track.info("Running Filter")
        self.storms=self.storms.apply(lambda x: self.filter_stormevents_goes(x,self.session), axis=1)

        # df goes_intersections
        header=["KEY","FOREIGN_KEY", "SIZE", "IS_TIME_INTERSECTING", "BEGIN_TIME_UTC", "END_TIME_UTC", "bucket_begin_time", "bucket_end_time"]
        goes_intersections=load_CSV_file(self.output_dir_txt,header)
        goes_intersections=goes_intersections.drop_duplicates(['KEY'])
        goes_intersections.to_csv(self.output_dir)

        os.remove(self.output_dir_txt)


    def filter_stormevents_goes(self,row,session):
        # time conversion to UTC
        to_UTC_time(row)

        self.bucket_goes(row,session)
        self.track.info("filter_stormevents_goes Testing Intersection "+str(row.name))
        return row





    def bucket_goes(self,row,session):
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

                    with open(self.output_dir_txt, "a") as myfile:
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
                self.track.info(str(object.key)+", "+str(object.size)+", "+str(time_intersection)+", "+str(x)+", "+str(row.name))
                x+=1



        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                Track.warn("The object does not exist.")
            else:
                raise
                Track.warn("Error.")

