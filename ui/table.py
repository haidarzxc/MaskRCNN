from kivy.uix.listview import ListItemButton

import os, sys, inspect
import pandas as pd
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datasets.NCDC_stormevents_data_loader import load_CSV_file

class ListButton(ListItemButton):
    pass

def data():
    storm_cols=['BEGIN_DATE_TIME','END_DATE_TIME','BEGIN_LON','BEGIN_LAT']
    storms=load_CSV_file('NCDC_stormevents/StormEvents_details-ftp_v1.0_d2017_c20180918.csv')
    storms_header=pd.DataFrame([storm_cols],columns=storm_cols)
    storms_filtered=storms[storm_cols]
    storms_header=storms_header.append(storms_filtered, ignore_index=True)
    storms_header=storms_header.to_string(header=False,
                        index=False,
                        index_names=False).split('\n')
    print(storms_header)

    return storms_header

