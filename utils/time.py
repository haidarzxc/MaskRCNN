import pandas as pd
from datetime import timedelta

import settings.local as local
import utils.track as tr
Track=tr.Track()
# http://strftime.org/
# https://www.timeanddate.com/worldclock/converter.html?iso=20190121T070400&p1=1440&p2=tz_sst

def date_range_intersection_test(bucket_begin_time,
                                    bucket_end_time,
                                    BEGIN_TIME_UTC,
                                    END_TIME_UTC
                                ):
    # (StartA <= EndB) and (EndA >= StartB)
    if (bucket_begin_time <= END_TIME_UTC) and (bucket_end_time >= BEGIN_TIME_UTC):
        return True;
    return False

def convert_time(time,zone,format='%Y-%m-%d %X'):
    time_str=time.strftime(format)
    return pd.to_datetime(time_str)+timedelta(hours=zone)


def to_UTC_time(row):
    # CZ_TIMEZONE
    # EST-5, CST-6, MST-7, PST-8, AST-4, AKST-9, HST-10, GST10, SST-11

    # converting string date time to pd timestamp
    format = '%d-%b-%y %X'
    storm_begin_datetime=pd.to_datetime(row['BEGIN_DATE_TIME'], format=format)
    storm_end_datetime=pd.to_datetime(row['END_DATE_TIME'], format=format)

    # add shift values
    shift_begin_date_time=storm_begin_datetime-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT)
    shift_end_date_time=storm_end_datetime+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT)

    try:
        if(row['CZ_TIMEZONE']=='EST-5'):
            # EST + 5 to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,5)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,5)
        elif(row['CZ_TIMEZONE']=='CST-6'):
            # CST + 6hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,6)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,6)
        elif(row['CZ_TIMEZONE']=='MST-7'):
            # mst + 7hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,7)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,7)
        elif(row['CZ_TIMEZONE']=='PST-8'):
            # PST + 8hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,8)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,8)
        elif(row['CZ_TIMEZONE']=='AST-4'):
            # AST + 4hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,4)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,4)
        elif(row['CZ_TIMEZONE']=='AKST-9'):
            # akst + 9hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,9)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,9)
        elif(row['CZ_TIMEZONE']=='HST-10'):
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,10)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,10)
        elif(row['CZ_TIMEZONE']=='GST10'):
            # Guam - 10 hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,-10)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,-10)
        elif(row['CZ_TIMEZONE']=='SST-11'):
            # SST + 11 hours to utc
            row['BEGIN_TIME_UTC']=convert_time(shift_begin_date_time,11)
            row['END_TIME_UTC']=convert_time(shift_end_date_time,11)
        else:
            Track.warn("Exception: time_zone not tracked "+row['CZ_TIMEZONE'])
            return None

    except:
        Track.warn("Exception: Error")
        pass
    return row