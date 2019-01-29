# python libraries
import unittest
import pandas as pd


# project modules
from utils.time import to_UTC_time,date_range_intersection_test
import settings.local as local

class TestTime(unittest.TestCase):

    def iterate_to_UTC_time(self,row):
        self.assertEqual(row['BEGIN_TIME_UTC'],row['BEGIN_CORRECT'])
        self.assertEqual(row['END_TIME_UTC'],row['END_CORRECT'])

    def test_to_UTC_time(self):
        test_df=pd.DataFrame()
        test_df['BEGIN_DATE_TIME']=pd.Series(
                                    ['20-JAN-19 22:00:00',
                                    '20-JAN-19 15:50:00',
                                    '20-JAN-19 12:15:00',
                                    '20-JAN-19 09:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    ])

        test_df['END_DATE_TIME']=pd.Series(
                                    ['20-JAN-19 13:30:00',
                                    '20-JAN-19 13:15:00',
                                    '20-JAN-19 5:15:00',
                                    '20-JAN-19 21:24:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    '20-JAN-19 20:04:00',
                                    ])

        test_df['CZ_TIMEZONE']=pd.Series(
                                    ['EST-5',
                                    'CST-6',
                                    'MST-7',
                                    'PST-8',
                                    'AST-4',
                                    'AKST-9',
                                    'HST-10',
                                    'GST10',
                                    'SST-11',
                                    'unknown-zone'])
        test_df['BEGIN_TIME_UTC']=pd.Series()
        test_df['END_TIME_UTC']=pd.Series()
        test_df['BEGIN_CORRECT']=pd.Series(
                                    [pd.to_datetime('21-JAN-19 03:00:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 21:50:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 19:15:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 17:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 00:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 05:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 06:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 10:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 07:04:00')-pd.Timedelta(minutes=local.STORM_BEGIN_TIME_MIN_SHIFT),
                                    None
                                    ])

        test_df['END_CORRECT']=pd.Series(
                                    [pd.to_datetime('20-JAN-19 18:30:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 19:15:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 12:15:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 05:24:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 00:04:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 05:04:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 06:04:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('20-JAN-19 10:04:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    pd.to_datetime('21-JAN-19 07:04:00')+pd.Timedelta(minutes=local.STORM_END_TIME_MIN_SHIFT),
                                    None
                                    ])

        test_df=test_df.apply(lambda x:to_UTC_time(x),axis=1)

        test_df.apply(self.iterate_to_UTC_time,axis=1)

    def test_date_range_intersection_test(self):
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

        # test cases
        for case in cases:
            self.assertEqual(cases[case]['result'],cases[case]['correct_result'])
