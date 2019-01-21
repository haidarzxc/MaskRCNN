
# NOTE: switch python PATH to look at parent_directory
import os, sys, inspect
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)

# python libraries
import argparse

# project modules
from datasets.Area_filter import bounding_box_area_filter
# from datasets.intersect import *
# from utils.time import to_UTC_time,date_range_intersection_test
# from NCDC_stormevents_data_loader import load_CSV_file, get_NCDC_data,\
#                                     retrieve_WSR_88D_RDA_locations
import utils.track as tr
import settings.local as local
from datasets.time_intersection_test import GoesIntersectionTest
from utils.boto import create_session

Track=tr.Track()

'''
RADAR CENTER LOCATION

                    HORIZONTAL_SHIFT
                    .-----------. (END_LON+HORIZONTAL_SHIFT,END_LAT+VERTICAL_SHIFT)
                    |           |
  VERTICAL_SHIFT    |     .<----|--center (x,y)
                    |           |
                    .-----------.
    (BEGIN_LON-HORIZONTAL_SHIFT,BEGIN_LAT-VERTICAL_SHIFT)
'''

def parse_args():
    parser = argparse.ArgumentParser(description='zxc Desc')
    parser.add_argument(
        '--intersectionTest',
        dest='intersectionTest',
        help='pass GOES or NEXRAD',
        default=None,
        type=str
    )

    parser.add_argument(
        '--storms',
        dest='stormsFile',
        help='pass stormsFile',
        default=None,
        type=str
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def main(args):
    if args.intersectionTest is not None:
        if args.stormsFile is None:
            Track.warn("Pass a storms file")
            return
        session=create_session(local)
        if args.intersectionTest=="GOES":
            Track.info("Starting GOES intersection Test")
            GoesIntersectionTest(session,Track,args.stormsFile,local)
        elif args.intersectionTest=="NEXRAD":
            pass







if __name__ == '__main__':
    args = parse_args()
    main(args)

