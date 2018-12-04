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
import math

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class Frame(QtGui.QMainWindow):
    def __init__(self,data,lon,lat,nexrad_object):
        self.qapp = QtGui.QApplication([])
        self.nexrad_object=nexrad_object
        self.data=data
        self.lon=lon
        self.lat=lat

        QtGui.QMainWindow.__init__(self)
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtGui.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(5)

        self.fig = plt.Figure(figsize=(16,15))
        self.fig.subplots_adjust(hspace=.1)
        self.canvas = FigureCanvas(self.fig)



        ax0 = self.fig.add_subplot(2, 1, 2)

        bbox = [np.min(lon),np.min(lat),np.max(lon),np.max(lat)]
        n_add = 0
        m = Basemap(llcrnrlon=bbox[0]-n_add,llcrnrlat=bbox[1]-n_add,
                    urcrnrlon=bbox[2]+n_add,urcrnrlat=bbox[3]+n_add,
                    resolution='i',
                    projection='cyl',ax=ax0)
        m.drawcoastlines(linewidth=0.5)
        m.drawcountries(linewidth=0.25)

        m.pcolormesh(lon.data, lat.data, data, latlon=True)
        parallels = np.linspace(np.min(lat),np.max(lat),5.)
        m.drawparallels(parallels,labels=[True,False,False,False])
        meridians = np.linspace(np.min(lon),np.max(lon),5.)
        m.drawmeridians(meridians,labels=[False,False,False,True])



        ax1 = self.fig.add_subplot(2, 1, 1)
        radar = pyart.io.read_nexrad_archive('nexrad_intersections/'+nexrad_object['KEY'])
        display = pyart.graph.RadarDisplay(radar)
        display.plot('reflectivity', 0, title="title",ax=ax1,colorbar_flag=False)



        self.canvas.draw()
        self.scroll = QtGui.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)


        # self.fig.savefig("MaskRCNN", dpi=100)
        self.show()
        exit(self.qapp.exec_())

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

    def render_objects(self,goes_netCdf,lon,lat,nexrad_object):
        Frame(goes_netCdf,lon,lat,nexrad_object)

    def clip_goes(self,goes_netCdf,storm_row):
        data=goes_netCdf['Rad']

        g_w=2500
        g_h=1500

        g_x0=-152.109282
        g_y0=14.571340
        g_x1=-52.946879
        g_y1=56.761450

        s_x0=storm_row['END_LON']
        s_y0=storm_row['BEGIN_LAT']
        s_x1=storm_row['BEGIN_LON']
        s_y1=storm_row['END_LAT']

        '''
                        2500
                .----------|----------.(g_x1,g_y1)
                |          |          |
        1500 ---|----------|----------|---
                |          |          |
    (g_x0,g_y0) .----------|----------.
                           |
        '''
        s_x=(g_x1-g_x0)/g_w
        s_y=(g_y1-g_y0)/g_h
        print(s_x,s_y)

        c0=(s_x0-g_x0)/s_x
        c1=(s_x1-g_x1)/s_x
        r0=(s_y0-g_y0)/s_y
        r1=(s_y1-g_y1)/s_y

        print(c0,c1,r0,r1)

        c0_int=abs(math.floor(c0))
        c1_int=abs(math.ceil(c1))
        r0_int=abs(math.floor(r0))
        r1_int=abs(math.ceil(r1))
        print("r0_int",r0_int,
              "r1_int",r1_int,
              "c0_int",c0_int,
              "c1_int",c1_int)
        # [r0..r1,c0..c1]
        clipped=data[r0_int:r1_int, c0_int:c1_int]
        return clipped,r0_int, r1_int, c0_int, c1_int

    def geo_coordinates(self, goes_netCdf,nexrad_object,storm_row):
        proj_info = goes_netCdf.variables['goes_imager_projection']
        lon_origin = proj_info.longitude_of_projection_origin
        H = proj_info.perspective_point_height+proj_info.semi_major_axis
        r_eq = proj_info.semi_major_axis
        r_pol = proj_info.semi_minor_axis

        clipped, r0_int, r1_int, c0_int, c1_int=self.clip_goes(goes_netCdf,storm_row)


        lat_rad_1d = goes_netCdf.variables['x'][c0_int:c1_int]
        lon_rad_1d = goes_netCdf.variables['y'][r0_int:r1_int]


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

        # self.draw_goes(goes_netCdf.variables['Rad'][0:499,0:499],lon,lat)
        print("lat_rad_1d shape",np.shape(lat_rad_1d))
        print("lat_rad_1d shape",np.shape(lon_rad_1d))
        print("clipped shape",np.shape(clipped))
        print(storm_row)
        self.render_objects(clipped,lon,lat,nexrad_object)



    def clip_Goes_object(self,goes_object,nexrad_object,storm_row):
        goes_dir='goes_intersections/2017-12-01_2017-12-31/'
        if not Path(goes_dir+goes_object['KEY'].replace('/',"_")).is_file():
            iterate_goes_intersections(goes_object,goes_dir)
        if not Path('nexrad_intersections/'+nexrad_object['KEY']).is_file():
            current_working_dir=os.getcwd()
            iterate_nexrad_intersections(nexrad_object,'nexrad_intersections')
            os.chdir(current_working_dir)

        goes_netCdf= Dataset(goes_dir+goes_object['KEY'].replace('/',"_"),"r")

        # print(goes_netCdf.variables)
        self.geo_coordinates(goes_netCdf,nexrad_object,storm_row)
        # goes_netCdf.close()


    def iterate_goes(self,nexrad_row,goes_objects,storm_row):
        nexrad_datetime=datetime.strptime(nexrad_row['bucket_begin_time'],'%Y-%m-%d %X')

        if len(goes_objects)>0:

            goes_objects.index = pd.to_datetime(goes_objects['bucket_begin_time'])

            goes_30min_window=goes_objects['bucket_begin_time'].between_time(
                    str(nexrad_datetime.time()),
                    str((nexrad_datetime + timedelta(minutes=30)).time()))


            nearest_object_index=goes_objects['bucket_begin_time'].tolist().index(min(goes_objects['bucket_begin_time'],
                key=lambda x: abs((datetime.strptime(x,'%Y-%m-%d %X')) - nexrad_datetime)))


            self.clip_Goes_object(goes_objects.iloc[nearest_object_index],nexrad_row,storm_row)
            # print("nearest_object",nearest_object_index,goes_objects.iloc[nearest_object_index],nexrad_datetime)

        else:
            print("No Goes objects")

    def get_intersected_objects(self,storm_row):
        nexrad_objects=self.nexrad.loc[(self.nexrad['FOREIGN_KEY'] == storm_row.name)]
        goes_objects=self.goes.loc[(self.goes['FOREIGN_KEY'] == storm_row.name)]
        # print("before iterate_goes",storm_row.name)
        nexrad_objects.head(1).apply(lambda x: self.iterate_goes(x,goes_objects,storm_row),axis=1)


    def iterate_storms(self,begin_start_date=None,begin_end_date=None):
        storms=self.storms.sort_values(by=['AREA'],ascending=False)

        storms['BEGIN_DATE_TIME']=storms['BEGIN_DATE_TIME'].apply(lambda x: pd.Timestamp(x))
        if begin_start_date and begin_end_date:

            begin_start_date=pd.Timestamp(begin_start_date)
            begin_end_date=pd.Timestamp(begin_end_date)
            storms=storms.loc[(storms['BEGIN_DATE_TIME'] > begin_start_date) &
                                (storms['BEGIN_DATE_TIME'] < begin_end_date)]
        print(storms)
        # storms.head(4).apply(self.get_intersected_objects,axis=1)



Clip()