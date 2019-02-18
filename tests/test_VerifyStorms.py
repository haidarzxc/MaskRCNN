# python libraries
import unittest
import pandas as pd


# project modules
from datasets.verifyStorms import VerifyStorms

class TestVerifyStorms(unittest.TestCase):

    def test_storm_null(self):
        storms_df=pd.DataFrame(data={
                            'BEGIN_LAT': [None],
                            'BEGIN_LON': [None],
                            'END_LAT': [None],
                            'END_LON': [None],
                            'BEGIN_DATE_TIME': [None],
                            'CZ_TIMEZONE': [None],
                            'END_DATE_TIME': [54],
                            })

        instance =VerifyStorms(storms_df)

        self.assertEqual(instance.output.empty,True)

    def test_storm_postive_longtudes(self):
        storms_df=pd.DataFrame(data={
                            'BEGIN_LAT': [5],
                            'BEGIN_LON': [5],
                            'END_LAT': [5],
                            'END_LON': [5],
                            'BEGIN_DATE_TIME': [5],
                            'CZ_TIMEZONE': [5],
                            'END_DATE_TIME': [5],
                            })

        instance = VerifyStorms(storms_df)
        self.assertEqual(instance.output.loc[0,'BEGIN_LON'],-5)
        self.assertEqual(instance.output.loc[0,'END_LON'],-5)
        self.assertNotEqual(instance.output.loc[0,'BEGIN_LAT'],-5)
        self.assertNotEqual(instance.output.loc[0,'END_LAT'],-5)

    def test_storm_postive_longtudes(self):
        storms_df=pd.DataFrame(data={
                            'BEGIN_LAT': [5],
                            'BEGIN_LON': [5],
                            'END_LAT': [5],
                            'END_LON': [5],
                            'BEGIN_DATE_TIME': [5],
                            'CZ_TIMEZONE': [5],
                            'END_DATE_TIME': [5],
                            })

        instance = VerifyStorms(storms_df)
        self.assertEqual(instance.output.loc[0,'BEGIN_LON'],-5)
        self.assertEqual(instance.output.loc[0,'END_LON'],-5)
        self.assertNotEqual(instance.output.loc[0,'BEGIN_LAT'],-5)
        self.assertNotEqual(instance.output.loc[0,'END_LAT'],-5)

    def test_storm_lat_greator(self):
        storms_df=pd.DataFrame(data={
                            'BEGIN_LAT': [10.4323223,100],
                            'BEGIN_LON': [5,12],
                            'END_LAT': [10.4323123,50],
                            'END_LON': [5,12],
                            'BEGIN_DATE_TIME': [5,12],
                            'CZ_TIMEZONE': [5,12],
                            'END_DATE_TIME': [5,12],
                            })

        instance = VerifyStorms(storms_df)
        self.assertEqual(instance.output.loc[0,'BEGIN_LAT'],10.4323123)
        self.assertEqual(instance.output.loc[0,'END_LAT'],10.4323223)
        self.assertEqual(instance.output.loc[1,'BEGIN_LAT'],50)
        self.assertEqual(instance.output.loc[1,'END_LAT'],100)

    def test_storm_lon_greator(self):
        storms_df=pd.DataFrame(data={
                            'BEGIN_LAT': [5,1,0],
                            'BEGIN_LON': [-5,10,-140.213],
                            'END_LAT': [5,1,0],
                            'END_LON': [-6,2,-140.223],
                            'BEGIN_DATE_TIME': [5,1,0],
                            'CZ_TIMEZONE': [5,1,0],
                            'END_DATE_TIME': [5,1,0],
                            })

        instance = VerifyStorms(storms_df)
        self.assertEqual(instance.output.loc[0,'BEGIN_LON'],-6)
        self.assertEqual(instance.output.loc[0,'END_LON'],-5)
        self.assertEqual(instance.output.loc[1,'BEGIN_LON'],-10)
        self.assertEqual(instance.output.loc[1,'END_LON'],-2)
        self.assertEqual(instance.output.loc[2,'BEGIN_LON'],-140.223)
        self.assertEqual(instance.output.loc[2,'END_LON'],-140.213)
        self.assertNotEqual(instance.output.loc[1,'BEGIN_LON'],2)
        self.assertNotEqual(instance.output.loc[1,'END_LON'],10)





