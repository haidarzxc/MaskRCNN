# links
'''
storms CSVs details/locations link
    ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/
nexrad radar objets link
    https://s3.amazonaws.com/noaa-nexrad-level2/index.html
goes-16 objects link
    http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_AWS_download.cgi?DATASET=noaa-goes16&BUCKET=ABI-L2-MCMIPF
radars locations link
    http://apollo.lsc.vsc.edu/classes/remote/lecture_notes/radar/88d/88D_locations.html
'''

# base

# shift units
HORIZONTAL_SHIFT=2
VERTICAL_SHIFT=2

# bounding box area threshold
bounding_box_area_threshold=6.25E-06

# stormevents excel sheet time margin shift
STORM_BEGIN_TIME_MIN_SHIFT=1
STORM_END_TIME_MIN_SHIFT=1

# AMAZON S3 end time wether meta_data shift 310 seconds
META_DATA_END_TIME_SEC_SHIFT=310

# goes object margins
goes_margin_left=-50
goes_margin_right=50
goes_margin_top=-50
goes_margin_bottom=50

# radar 88D_locations URL
WSR_88D_LOCATIONS='http://apollo.lsc.vsc.edu/classes/remote/lecture_notes/radar/88d/88D_locations.html'

# ncdc stormevents URL
NCDC_STORMEVENTS='ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/'


# download directories
GOES_DIR='goes_intersections/objects/'
NEXRAD_DIR='nexrad_intersections/'