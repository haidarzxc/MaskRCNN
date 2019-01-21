

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