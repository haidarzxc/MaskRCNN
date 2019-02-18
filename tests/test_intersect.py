# python libraries
import unittest


# project modules
from utils.intersect import *

'''
        left,top            .----------.    storm_end_point
                            |          |    Right,top
                            |          |
                            |          |
        storm_begin_point   .----------.   Right,bottom
        left,bottom

  example case
  (-5,15).----------------.(10,15)
        |                 |
        |                 |
        |                 |
        |                 |
        |                 |
  (-5,0)|-----------------.(10,0)


              (0,25).---------------------.(20,25)
                    |                     |
                    |                     |
  (-5,15).----------|-----.(10,15)        |
        |           |     |               |
        |           |     |               |
        |      (0,5).-----|---------------.(20,5)
        |                 |
        |                 |
  (-5,0)|-----------------.(10,0)
'''

class TestIntersect(unittest.TestCase):

    def test_point(self):
        p1=Point(0,10)
        self.assertEqual(p1.x, 0)
        self.assertEqual(p1.y, 10)

        self.assertNotEqual(p1.x, 2)
        self.assertNotEqual(p1.y, 120)

    def test_box(self):
        # box one
        p1=Point(-5,0)
        p2=Point(10,15)
        box1=Box(p1,p2)
        self.assertEqual(box1.left, -5)
        self.assertEqual(box1.right, 10)
        self.assertEqual(box1.top, 15)
        self.assertEqual(box1.bottom, 0)

        self.assertNotEqual(box1.left, 0)
        self.assertNotEqual(box1.right, 20)
        self.assertNotEqual(box1.top, 25)
        self.assertNotEqual(box1.bottom, 50)

        # box two
        p3=Point(0,5)
        p4=Point(20,25)
        box2=Box(p3,p4)

        self.assertEqual(box2.left, 0)
        self.assertEqual(box2.right, 20)
        self.assertEqual(box2.top, 25)
        self.assertEqual(box2.bottom, 5)

        self.assertNotEqual(box2.left, -15)
        self.assertNotEqual(box2.right, 24)
        self.assertNotEqual(box2.top, 0)
        self.assertNotEqual(box2.bottom, 20)

    def test_is_intersecting(self):
        # box one
        p1=Point(-5,0)
        p2=Point(10,15)
        box1=Box(p1,p2)

        # box two
        p3=Point(0,5)
        p4=Point(20,25)
        box2=Box(p3,p4)

        # box three
        p5=Point(0,16)
        p6=Point(20,25)
        box3=Box(p5,p6)

        # box four
        p7=Point(11,5)
        p8=Point(20,25)
        box4=Box(p7,p8)

        result_case_intersecting=is_intersecting(box1,box2)
        result_case1_not_intersecting=is_intersecting(box1,box3)
        result_case2_not_intersecting=is_intersecting(box1,box4)

        self.assertTrue(result_case_intersecting)
        self.assertFalse(result_case1_not_intersecting)
        self.assertFalse(result_case2_not_intersecting)







