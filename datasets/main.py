
# python libraries
# NOTE: switch python PATH to look at parent_directory
import os, sys, inspect
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
import argparse

# project modules
import utils.track as tr
import settings.local as local
from datasets.time_intersection_test import GoesIntersectionTest
from datasets.space_intersection_test import NexradIntersectionTest
from datasets.area_filter import AreaFilter
from utils.boto import create_session
from datasets.verifyStorms import VerifyStorms

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

    parser.add_argument(
        '--locations',
        dest='locationsFile',
        help='pass locations file',
        default=None,
        type=str
    )

    parser.add_argument(
        '--areaFilter',
        dest='areaFilter',
        help='pass storms file to filter area',
        default=None,
        type=str
    )

    parser.add_argument(
        '--output_dir',
        dest='output',
        help='pass output directory',
        default=None,
        type=str
    )

    parser.add_argument(
        '--verifyStorms',
        dest='verifyStorms',
        help='verify verifyStorms values',
        default=None,
        type=str
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

'''
Terminal Commands
python datasets\main.py --intersectionTest GOES --storms area_filtered_stormevents.csv

python datasets\main.py --intersectionTest NEXRAD --storms area_filtered_stormevents.csv --locations 88D_locations.csv

python datasets\main.py --areaFilter verified_storms.csv --output_dir area_filtered_stormevents.csv

python datasets\main.py --verifyStorms StormEvents_details-ftp_v1.0_d2017_c20180918.csv --output_dir verified_storms.csv

'''


def main(args):

    if args.verifyStorms is not None \
            and args.output is not None:
        Track.warn("Verify Storms")
        VerifyStorms(args.verifyStorms,args.output,Track)

    if args.areaFilter is not None:
        if args.output is None:
            Track.warn("Exception: Pass a output file")
            return
        Track.info("Starting storms Area filter")
        AreaFilter(Track,args.areaFilter,args.output,local)

    if args.intersectionTest is not None:

        if args.stormsFile is None:
            Track.warn("Exception: Pass a storms file")
            return
        session=create_session(local)
        if args.intersectionTest=="GOES":
            Track.info("Starting GOES intersection Test")
            GoesIntersectionTest(session,Track,args.stormsFile,local)

        elif args.intersectionTest=="NEXRAD":
            if args.locationsFile is None:
                Track.warn("Exception: Pass a Locations file")
                return
            Track.info("Starting NEXRAD intersection Test")
            NexradIntersectionTest(session,Track,args.stormsFile,args.locationsFile,local)



if __name__ == '__main__':
    args = parse_args()
    main(args)

