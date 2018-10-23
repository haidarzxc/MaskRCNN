import pandas as pd
import settings.local as local
# http://strftime.org/
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
    time_str=time.tz_localize(zone).tz_convert('UTC').strftime(format)
    return pd.to_datetime(time_str)


def to_UTC_time(row):
    # CZ_TIMEZONE
    # EST-5, CST-6, MST-7, PST-8, AST-4, AKST-9, HST-10, GST10, SST-11

    # converting string date time to pd timestamp
    format = '%d-%b-%y %X'
    storm_begin_datetime=pd.to_datetime(row['BEGIN_DATE_TIME'], format=format)
    storm_end_datetime=pd.to_datetime(row['END_DATE_TIME'], format=format)

    # add shift values
    row['BEGIN_DATE_TIME']=storm_begin_datetime-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT)
    row['END_DATE_TIME']=storm_end_datetime+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT)

    try:
        if(row['CZ_TIMEZONE']=='EST-5'):
            convert_time(row['BEGIN_DATE_TIME'],'US/Eastern')
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Eastern')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Eastern')
        elif(row['CZ_TIMEZONE']=='CST-6'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Central')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Central')
        elif(row['CZ_TIMEZONE']=='MST-7'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Mountain')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Mountain')
        elif(row['CZ_TIMEZONE']=='PST-8'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Pacific')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Pacific')
        elif(row['CZ_TIMEZONE']=='AST-4'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'Canada/Atlantic')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'Canada/Atlantic')
        elif(row['CZ_TIMEZONE']=='AKST-9'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Alaska')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Alaska')
        elif(row['CZ_TIMEZONE']=='HST-10'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Hawaii')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Hawaii')
            # varify time zone GST10
        elif(row['CZ_TIMEZONE']=='GST10'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'Pacific/Guam')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'Pacific/Guam')
        elif(row['CZ_TIMEZONE']=='SST-11'):
            row['BEGIN_TIME_UTC']=convert_time(row['BEGIN_DATE_TIME'],'US/Samoa')
            row['END_TIME_UTC']=convert_time(row['END_DATE_TIME'],'US/Samoa')
        else:
            Track.warn("Exception: time_zone not tracked "+row['CZ_TIMEZONE'])
    except:
        pass



    return row