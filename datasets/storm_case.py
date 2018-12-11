# import os, sys, inspect
# import pandas as pd
# import numpy as np
# from pathlib import Path
# parent_directory = os.path.dirname(\
#                     os.path.dirname(\
#                     os.path.abspath(inspect.getfile(inspect.currentframe()))))
# sys.path.insert(0,parent_directory)
# from datasets.NCDC_stormevents_data_loader import load_CSV_file
# from GOES_clipping import Frame
#
# from datasets.boto import create_session, \
#                             iterate_nexrad_intersections, \
#                             iterate_goes_intersections
# from datetime import datetime
# from datetime import timedelta
#
# def main():
#     # loading CSVs storms, nexrad intersections, and goes intersections
#     storms=load_CSV_file('NCDC_stormevents/area_filtered_stormevents.csv')
#     nexrad=load_CSV_file('NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv')
#     goes=load_CSV_file('goes_intersections/GOES_datetime_filtered_intersections.csv')
#
#
#     # storm case with max area id=7227
#     max_area_storm=storms.iloc[7227]
#     # filtering nexrads and goess with respect to id 7227
#     storm_nexrads=nexrad.loc[(nexrad['FOREIGN_KEY'] == max_area_storm.name)]
#     storm_goes=goes.loc[(goes['FOREIGN_KEY'] == max_area_storm.name)]
#
#
#     # if objects not found, download them (if any!)
#     for index, goes_object in storm_goes.iterrows():
#         goes_dir='goes_intersections/2017-12-01_2017-12-31/'
#         if not Path(goes_dir+goes_object['KEY'].replace('/',"_")).is_file():
#             iterate_goes_intersections(goes_object,goes_dir)
#
#     for index, nexrad_object in storm_nexrads.iterrows():
#         if not Path('nexrad_intersections/'+nexrad_object['KEY']).is_file():
#             current_working_dir=os.getcwd()
#             iterate_nexrad_intersections(nexrad_object,'nexrad_intersections')
#             os.chdir(current_working_dir)
#
#
#
#     for nexrad_index, nexrad_object in storm_nexrads.iterrows():
#         for goes_index, goes_object in storm_goes.iterrows():
#             nexrad_datetime=datetime.strptime(nexrad_object['bucket_begin_time'],'%Y-%m-%d %X')
#             goes_object.index = pd.to_datetime(goes_object['bucket_begin_time'])
#
#             goes_30min_window=goes_object['bucket_begin_time'].between_time(
#                     str(nexrad_datetime.time()),
#                     str((nexrad_datetime + timedelta(minutes=30)).time()))
#
#
#             nearest_object_index=goes_object['bucket_begin_time'].tolist().index(min(goes['bucket_begin_time'],
#                 key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))
#         break
#
#             # clip_Goes_object(goes_objects.iloc[nearest_object_index],nexrad_row,storm_row)
#
#
#
#
# # main
# if __name__ == '__main__':
#     main()