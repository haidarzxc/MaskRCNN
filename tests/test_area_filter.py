# python libraries
import unittest
import pandas as pd


# project modules
from datasets.area_filter import AreaFilter
# import utils.track as tr
# import settings.local as local
# Track=tr.Track()

class TestAreaFilter(unittest.TestCase):

    def test_calculate_distance(self):
        instance1=AreaFilter()
        #method signiture x1,x2,y1,y2
        # example (-1, 1) and (3, 4)
        result=instance1.calculate_distance(-1,3,1,4)
        self.assertEqual(result,5)
        self.assertNotEqual(result,75)

        result1=instance1.calculate_distance(-1,33,1,11)
        self.assertEqual(result1,35.4400902933387)
        self.assertNotEqual(result1,732)

    def iterate_calculateArea(self,row):
        self.assertEqual(row['AREA'],row['CORRECT_AREA'])

    def test_calculate_area(self):
        instance1=AreaFilter()
        test_df=pd.DataFrame()
        test_df['BEGIN_LON']=pd.Series([-5,0])
        test_df['BEGIN_LAT']=pd.Series([0,5])
        test_df['END_LON']=pd.Series([10,20])
        test_df['END_LAT']=pd.Series([15,25])
        test_df['AREA']=pd.Series([])
        test_df['CORRECT_AREA']=pd.Series([225,400])

        test_df=test_df.apply(lambda x: instance1.calculate_area(x), axis=1)
        test_df.apply(self.iterate_calculateArea,axis=1)
