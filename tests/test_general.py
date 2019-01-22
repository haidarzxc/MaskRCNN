# python libraries
import unittest


# project modules
from utils.general import verify_lon_lat


class TestGeneral(unittest.TestCase):

    def test_verify_lon_lat(self):
        # BEGIN_LON must be less than END_LON
        # BEGIN_LAT must be less than END_LAT

        # case A - pass non lons and lats
        null_values=dict(BEGIN_LON=None,
                        END_LON=None,
                        BEGIN_LAT=None,
                        END_LAT=None
                        )
        # method signiture track=None,BEGIN_LON,END_LON, BEGIN_LAT,END_LAT
        result=verify_lon_lat(null_values['BEGIN_LON'],
                               null_values['END_LON'],
                               null_values['BEGIN_LAT'],
                               null_values['END_LAT']
                        )

        self.assertEqual(result['BEGIN_LON'],null_values['BEGIN_LON'])
        self.assertEqual(result['END_LON'],null_values['END_LON'])
        self.assertEqual(result['BEGIN_LAT'],null_values['BEGIN_LAT'])
        self.assertEqual(result['END_LAT'],null_values['END_LAT'])

        # case B - correct values
        # BEGIN_LAT	BEGIN_LON	END_LAT	END_LON
        # 39.66	-75.08	39.66	-75.08
        correct_values=dict(BEGIN_LON=-75.08,
                        END_LON=-75.08,
                        BEGIN_LAT=39.66,
                        END_LAT=39.66
                        )
        result1=verify_lon_lat(correct_values['BEGIN_LON'],
                               correct_values['END_LON'],
                               correct_values['BEGIN_LAT'],
                               correct_values['END_LAT']
                        )

        self.assertEqual(result1['BEGIN_LON'],correct_values['BEGIN_LON'])
        self.assertEqual(result1['END_LON'],correct_values['END_LON'])
        self.assertEqual(result1['BEGIN_LAT'],correct_values['BEGIN_LAT'])
        self.assertEqual(result1['END_LAT'],correct_values['END_LAT'])

        # case C - wrong values

        correct_values1=dict(BEGIN_LON=-30,
                        END_LON=-15,
                        BEGIN_LAT=20,
                        END_LAT=50
                        )

        incorrect_values=dict(BEGIN_LON=-15,
                        END_LON=-30,
                        BEGIN_LAT=50,
                        END_LAT=20
                        )
        result2=verify_lon_lat(incorrect_values['BEGIN_LON'],
                               incorrect_values['END_LON'],
                               incorrect_values['BEGIN_LAT'],
                               incorrect_values['END_LAT']
                        )
        self.assertEqual(result2['BEGIN_LON'],correct_values1['BEGIN_LON'])
        self.assertEqual(result2['END_LON'],correct_values1['END_LON'])
        self.assertEqual(result2['BEGIN_LAT'],correct_values1['BEGIN_LAT'])
        self.assertEqual(result2['END_LAT'],correct_values1['END_LAT'])

        # case D - none negative lons
        incorrect_values1=dict(BEGIN_LON=15,
                        END_LON=30,
                        BEGIN_LAT=50,
                        END_LAT=20
                        )
        result3=verify_lon_lat(incorrect_values1['BEGIN_LON'],
                               incorrect_values1['END_LON'],
                               incorrect_values1['BEGIN_LAT'],
                               incorrect_values1['END_LAT']
                        )
                        
        self.assertEqual(result3['BEGIN_LON'],correct_values1['BEGIN_LON'])
        self.assertEqual(result3['END_LON'],correct_values1['END_LON'])
        self.assertEqual(result3['BEGIN_LAT'],correct_values1['BEGIN_LAT'])
        self.assertEqual(result3['END_LAT'],correct_values1['END_LAT'])

