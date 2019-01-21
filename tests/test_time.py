# python libraries
import unittest
import pandas as pd


# project modules
from utils.time import to_UTC_time
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
