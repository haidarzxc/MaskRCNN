import pandas as pd
import numpy as np
import os, sys, inspect
# NOTE: switch python PATH to look at parent_directory
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

from datasets.boto import to_UTC_time,date_range_intersection_test,calculate_area
from datasets.intersect import *
import math


# # testing intersect module
# # Example 1
# p1=Point(0,10)
# p2=Point(10,0)
# p3=Point(5,5)
# p4=Point(15,0)
# r1=Box(p1,p2)
# r2=Box(p3,p4)
# res=is_intersecting(r1,r2)
# print(res)
#
# # Example 2
# p1A=Point(3,7)
# p2A=Point(12,-10)
# p3A=Point(8,4)
# p4A=Point(20,7)
# r1A=Box(p1A,p2A)
# r2A=Box(p3A,p4A)
# resA=is_intersecting(r1A,r2A)
# print(resA)
#
# # Example 3
# p1B=Point(-1,-1)
# p2B=Point(1,1)
# p3B=Point(0,0)
# p4B=Point(2,2)
# r1B=Box(p1B,p2B)
# r2B=Box(p3B,p4B)
# resB=is_intersecting(r1B,r2B)
# print(resB)
#
# # Example 4
# p1C=Point(-1,-1)
# p2C=Point(1,1)
# p3C=Point(2,2)
# p4C=Point(3,3)
# r1C=Box(p1C,p2C)
# r2C=Box(p3C,p4C)
# resC=is_intersecting(r1C,r2C)
# print(resC)


# testing filter_stormevents
loc=pd.DataFrame()
stm=pd.DataFrame()

loc['BEGIN_LON']=pd.Series([-1,0])
loc['BEGIN_LAT']=pd.Series([-1,0])
loc['END_LON']=pd.Series([1,1])
loc['END_LAT']=pd.Series([1,1])
loc['STATIONID']=pd.Series(["xxxx3"])

stm['BEGIN_LON']=pd.Series([0,2])
stm['BEGIN_LAT']=pd.Series([0,2])
stm['END_LON']=pd.Series([2,3])
stm['END_LAT']=pd.Series([2,3])
stm['STATIONID']=pd.Series()
stm['IS_INTERSECTING']=pd.Series()

# stm=stm.apply(lambda x: filter_stormevents(x,loc),axis=1)
# print(loc)
# print(stm)

def export_boxes_to_csv(output_dir):

    df=pd.DataFrame()
    # location
    loc_beg_x=[]
    loc_beg_y=[]
    loc_end_x=[]
    loc_end_y=[]

    # storm
    stm_beg_x=[]
    stm_beg_y=[]
    stm_end_x=[]
    stm_end_y=[]
    intersection=[]

    for loc_beg,loc_end,stm_beg,stm_end in zip(boxes['location_begin_point'],
                                            boxes['location_end_point'],
                                            boxes['storm_begin_point'],
                                            boxes['storm_end_point']):
        # check intersection
        loc_beg_point=Point(loc_beg.x,loc_beg.y)
        loc_end_point=Point(loc_end.x,loc_end.y)
        stm_beg_point=Point(stm_beg.x,stm_beg.y)
        stm_end_point=Point(stm_end.x,stm_end.y)
        loc_box=Box(loc_beg_point,loc_end_point)
        stm_box=Box(stm_beg_point,stm_end_point)
        res=is_intersecting(loc_box,stm_box)
        intersection.append(is_intersecting(loc_box,stm_box))

        # location
        loc_beg_x.append(loc_beg.x)
        loc_beg_y.append(loc_beg.y)
        loc_end_x.append(loc_end.x)
        loc_end_y.append(loc_end.y)

        # storm
        stm_beg_x.append(stm_beg.x)
        stm_beg_y.append(stm_beg.y)
        stm_end_x.append(stm_end.x)
        stm_end_y.append(stm_end.y)

    df['loc_beg_x']=pd.Series(loc_beg_x)
    df['loc_beg_y']=pd.Series(loc_beg_y)
    df['loc_end_x']=pd.Series(loc_end_x)
    df['loc_end_y']=pd.Series(loc_end_y)

    df['stm_beg_x']=pd.Series(stm_beg_x)
    df['stm_beg_y']=pd.Series(stm_beg_y)
    df['stm_end_x']=pd.Series(stm_end_x)
    df['stm_end_y']=pd.Series(stm_end_y)
    df['intersection']=pd.Series(intersection)

    df=df.drop_duplicates()
    df.to_csv(output_dir)
    # print(df)

def test_To_UTC_time(output_dir):
    test_df=pd.DataFrame()
    test_df['BEGIN_DATE_TIME']=pd.Series(['06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','11-MAR-17 21:00:00'])
    test_df['END_DATE_TIME']=pd.Series(['06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00','06-APR-17 15:09:00' ,'12-MAR-17 2:00:00'])
    test_df['CZ_TIMEZONE']=pd.Series(['EST-5','CST-6','MST-7','PST-8','AST-4','AKST-9','HST-10','GST10','SST-11','CST-6'])
    test_df['BEGIN_TIME_UTC']=pd.Series()
    test_df['END_TIME_UTC']=pd.Series()

    test_df=test_df.apply(lambda x:to_UTC_time(x),axis=1)
    test_df.to_csv(output_dir)
    print(test_df)


def test_date_range_intersection_test():
    '''
    format
        yyyy-mm-dd hh:mm:ss

    date_range_intersection_test() method arguments
        1.bucket_begin_time
        2.bucket_end_time
        3.BEGIN_TIME_UTC
        4.END_TIME_UTC
    '''
    result=None

    cases={
        # overlapping day
        "caseA":dict(
            date1A='2017-01-01 00:00:00',
            date1B='2017-01-02 00:00:00',
            date2A='2017-01-02 00:00:00',
            date2B='2017-01-03 00:00:00',
            result="",
            correct_result=True
        ),
        # NOT overlapping day
        "caseB":dict(
            date1A='2017-01-01 00:00:00',
            date1B='2017-01-02 00:00:00',
            date2A='2017-01-03 00:00:00',
            date2B='2017-01-04 00:00:00',
            result="",
            correct_result=False
        ),
        # overlapping month
        "caseC":dict(
            date1A='2017-01-01 00:00:00',
            date1B='2017-02-01 00:00:00',
            date2A='2017-02-01 00:00:00',
            date2B='2017-03-01 00:00:00',
            result="",
            correct_result=True
        ),
        # NOT overlapping month
        "caseD":dict(
            date1A='2017-01-01 00:00:00',
            date1B='2017-02-01 00:00:00',
            date2A='2017-03-01 00:00:00',
            date2B='2017-04-01 00:00:00',
            result="",
            correct_result=False
        ),
        # overlapping year
        "caseE":dict(
            date1A='2015-01-01 00:00:00',
            date1B='2016-01-01 00:00:00',
            date2A='2015-01-01 00:00:00',
            date2B='2017-01-01 00:00:00',
            result="",
            correct_result=True
        ),
        # NOT overlapping year
        "caseF":dict(
            date1A='2015-01-01 00:00:00',
            date1B='2016-01-01 00:00:00',
            date2A='2017-01-01 00:00:00',
            date2B='2018-01-01 00:00:00',
            result="",
            correct_result=False
        ),
        # overlapping hour
        "caseG":dict(
            date1A='2017-01-01 10:00:00',
            date1B='2017-01-01 11:00:00',
            date2A='2017-01-01 10:00:00',
            date2B='2017-01-01 12:00:00',
            result="",
            correct_result=True
        ),
        # NOT overlapping hour
        "caseH":dict(
            date1A='2017-01-01 10:00:00',
            date1B='2017-01-01 11:00:00',
            date2A='2017-01-01 12:00:00',
            date2B='2017-01-01 13:00:00',
            result="",
            correct_result=False
        ),
        # overlapping minutes
        "caseI":dict(
            date1A='2017-01-01 10:01:00',
            date1B='2017-01-01 10:10:00',
            date2A='2017-01-01 10:05:00',
            date2B='2017-01-01 10:20:00',
            result="",
            correct_result=True
        ),
        # NOT overlapping minutes
        "caseJ":dict(
            date1A='2017-01-01 10:01:00',
            date1B='2017-01-01 10:10:00',
            date2A='2017-01-01 10:15:00',
            date2B='2017-01-01 10:20:00',
            result="",
            correct_result=False
        ),
        # overlapping Seconds
        "caseK":dict(
            date1A='2017-01-01 10:01:01',
            date1B='2017-01-01 10:01:05',
            date2A='2017-01-01 10:01:02',
            date2B='2017-01-01 10:01:10',
            result="",
            correct_result=True
        ),
        # NOT overlapping Seconds
        "caseL":dict(
            date1A='2017-01-01 10:01:01',
            date1B='2017-01-01 10:01:05',
            date2A='2017-01-01 10:01:06',
            date2B='2017-01-01 10:01:10',
            result="",
            correct_result=False
        ),


    }

    # run cases
    for case in cases:
        result=date_range_intersection_test(cases[case]['date1A'],
                                            cases[case]['date1B'],
                                            cases[case]['date2A'],
                                            cases[case]['date2B'])
        cases[case]['result']=result

    # test cases (assert testunit will be integrated later on...)
    for case in cases:
        case_test=cases[case]['result'] is cases[case]['correct_result']
        if not case_test:
            print("failing case...")
            break;
        print(case,case_test)


def test_Area():
    test_df=pd.DataFrame()
    test_df['BEGIN_LON']=pd.Series([-118.4535,-2])
    test_df['BEGIN_LAT']=pd.Series([46.0757,0])
    test_df['END_LON']=pd.Series([-118.9053,2])
    test_df['END_LAT']=pd.Series([46.078,4])
    test_df['AREA']=pd.Series([])

    test_df=test_df.apply(lambda x: calculate_area(x), axis=1)
    test_df=test_df.sort_values(by=['AREA'],ascending=False)
    print(test_df)


test_Area()
# test_date_range_intersection_test()
# test_To_UTC_time("NCDC_stormevents\\test_To_UTC_time.csv")
# export_boxes_to_csv("frontend\\src\\static\\boxes.csv")