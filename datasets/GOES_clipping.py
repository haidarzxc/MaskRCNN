import os, sys, inspect
import pandas as pd
import numpy as np
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
from datasets.NCDC_stormevents_data_loader import load_CSV_file

from datasets.boto import create_session, \
                            iterate_nexrad_intersections, \
                            iterate_goes_intersections
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import boto3
import botocore
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import pyart
from mpl_toolkits.basemap import Basemap, cm

class Clip():
    storms=load_CSV_file('NCDC_stormevents/area_filtered_stormevents.csv')
    nexrad=load_CSV_file('NCDC_stormevents/NEXRAD_bounding_box_datetime_filtered_intersections.csv')
    goes=load_CSV_file('goes_intersections/GOES_datetime_filtered_intersections.csv')

    def __init__(self, **kwargs):
        super(Clip,self).__init__(**kwargs)
        self.nexrad=self.nexrad.sort_values(by=['bucket_begin_time'])
        self.goes=self.goes.sort_values(by=['bucket_begin_time'])
        self.iterate_storms(begin_start_date='01-DEC-17',
                            begin_end_date='31-DEC-17')

    def draw_goes(self,data,lon,lat):
        bbox = [np.min(lon),np.min(lat),np.max(lon),np.max(lat)]
        fig = plt.figure(figsize=(6,3),dpi=200)
        n_add = 0
        m = Basemap(llcrnrlon=bbox[0]-n_add,llcrnrlat=bbox[1]-n_add,
                    urcrnrlon=bbox[2]+n_add,urcrnrlat=bbox[3]+n_add,
                    resolution='i',
                    projection='cyl')
        m.drawcoastlines(linewidth=0.5)
        m.drawcountries(linewidth=0.25)
        m.pcolormesh(lon.data, lat.data, data, latlon=True)
        parallels = np.linspace(np.min(lat),np.max(lat),5.)
        m.drawparallels(parallels,labels=[True,False,False,False])
        meridians = np.linspace(np.min(lon),np.max(lon),5.)
        m.drawmeridians(meridians,labels=[False,False,False,True])
        cb = m.colorbar()

        # plt.savefig('goes_16_demo.png',dpi=200,transparent=True)
        plt.show()

    def geo_coordinates(self, goes_netCdf):
        proj_info = goes_netCdf.variables['goes_imager_projection']
        lon_origin = proj_info.longitude_of_projection_origin
        H = proj_info.perspective_point_height+proj_info.semi_major_axis
        r_eq = proj_info.semi_major_axis
        r_pol = proj_info.semi_minor_axis

        lat_rad_1d = goes_netCdf.variables['x'][:]
        lon_rad_1d = goes_netCdf.variables['y'][:]

        lat_rad,lon_rad = np.meshgrid(lat_rad_1d,lon_rad_1d)

        lambda_0 = (lon_origin*np.pi)/180.0

        a_var = np.power(np.sin(lat_rad),2.0) + \
                (np.power(np.cos(lat_rad),2.0)* \
                (np.power(np.cos(lon_rad),2.0)+ \
                (((r_eq*r_eq)/(r_pol*r_pol))* \
                np.power(np.sin(lon_rad),2.0))))
        b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
        c_var = (H**2.0)-(r_eq**2.0)

        r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

        s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
        s_y = - r_s*np.sin(lat_rad)
        s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

        lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))* \
                ((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
        lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)

        # print('{} N, {} W'.format(lat[318,1849],abs(lon[318,1849])))

        self.draw_goes(goes_netCdf.variables['Rad'][:],lon,lat)



    def clip_Goes_object(self,goes_object,nexrad_object):
        goes_dir='goes_intersections/2017-12-01_2017-12-31/'
        if not Path(goes_dir+goes_object['KEY'].replace('/',"_")).is_file():
            iterate_goes_intersections(goes_object,goes_dir)
        if not Path('nexrad_intersections/'+nexrad_object['KEY']).is_file():
            current_working_dir=os.getcwd()
            iterate_nexrad_intersections(nexrad_object,'nexrad_intersections')
            os.chdir(current_working_dir)

        goes_netCdf= Dataset(goes_dir+goes_object['KEY'].replace('/',"_"),"r")

        # print(goes_netCdf.variables)
        self.geo_coordinates(goes_netCdf)
        # goes_netCdf.close()


    def iterate_goes(self,nexrad_row,goes_objects):
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')
        if len(goes_objects)>0:

            goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])

            goes_30min_window=goes_objects['bucket_begin_time'].between_time(
                    str(nexrad_datetime.time()),
                    str((nexrad_datetime + timedelta(minutes=30)).time()))


            nearest_object_index=goes_objects['bucket_begin_time'].tolist().index(min(goes_objects['bucket_begin_time'],
                key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))

            self.clip_Goes_object(goes_objects.iloc[nearest_object_index],nexrad_row)
            # print("nearest_object",nearest_object_index,goes_objects.iloc[nearest_object_index],nexrad_datetime)

        else:
            print("No Goes objects")

    def get_intersected_objects(self,storm_row):
        nexrad_objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == storm_row.name)]
        goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == storm_row.name)]

        nexrad_objects.head(1).apply(lambda x: self.iterate_goes(x,goes_objects),axis=1)


    def iterate_storms(self,begin_start_date=None,begin_end_date=None):
        storms=self.storms
        storms['BEGIN_DATE_TIME']=storms['BEGIN_DATE_TIME'].apply(lambda x: pd.Timestamp(x))
        if begin_start_date and begin_end_date:

            begin_start_date=pd.Timestamp(begin_start_date)
            begin_end_date=pd.Timestamp(begin_end_date)
            storms=storms.loc[(storms['BEGIN_DATE_TIME'] > begin_start_date) &
                                (storms['BEGIN_DATE_TIME'] < begin_end_date)]


        storms.head(1).apply(self.get_intersected_objects,axis=1)



Clip()