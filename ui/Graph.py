import matplotlib.pyplot as plt
import pyart
import settings.local as local
import boto3
import os
import math
import netCDF4

import pylab as pl


import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from pathlib import Path

def create_session():
    session = boto3.Session(
        aws_access_key_id=local.AWSAccessKeyId,
        aws_secret_access_key=local.AWSSecretKey,
    )
    return session.resource('s3')


def get_aws_object(bucket,key,output_dir):
    session=create_session()
    bucket=session.Bucket(bucket)
    bucket.download_file(key,output_dir)


class ScrollableWindow(QtGui.QMainWindow):
    def __init__(self,nexrad,goes):
        self.qapp = QtGui.QApplication([])
        self.output_dir="ui_objects/"
        self.nexrad=nexrad
        self.goes=goes
        self.counter=-1
        self.nexrad_length=len(nexrad)
        self.goes_length=len(goes)

        QtGui.QMainWindow.__init__(self)
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtGui.QVBoxLayout())
        self.widget.layout().setContentsMargins(5,5,5,5)
        self.widget.layout().setSpacing(5)

        self.prev = QtGui.QPushButton('prev', self)
        self.prev.clicked.connect(self.handlePrev)

        self.next = QtGui.QPushButton('next', self)
        self.next.clicked.connect(self.handleNext)

        self.export = QtGui.QPushButton('Export Instances', self)
        self.export.clicked.connect(self.handleExport)

        self.nexrad_label = QtGui.QLabel()
        self.nexrad_label.setText("Nexrad| total: "+str(self.nexrad_length))

        self.goes_label = QtGui.QLabel()
        self.goes_label.setText("Goes| total: "+str(self.goes_length))

        self.fig = plt.Figure()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtGui.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)


        self.bar = QtGui.QWidget()
        self.bar.setLayout(QtGui.QHBoxLayout())

        self.bar.layout().addWidget(self.prev)
        self.bar.layout().addWidget(self.next)
        self.bar.layout().addWidget(self.export)
        self.bar.layout().addWidget(self.nexrad_label)
        self.bar.layout().addWidget(self.goes_label)

        self.bar.layout().addStretch()
        self.bar.layout().addStretch()

        self.widget.layout().addWidget(self.bar)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)



        self.show()
        exit(self.qapp.exec_())

    def download_file(self,key,bucket):
        object_name=key.values[0].split('/')[4]
        file = Path(self.output_dir+"/"+object_name)
        if not file.is_file():
            print("DOWNLOADING",object_name)
            if bucket=="nexrad":
                get_aws_object("noaa-nexrad-level2",key.values[0],self.output_dir+"/"+object_name)
            elif bucket=="goes":
                get_aws_object("noaa-goes16",key.values[0],self.output_dir+"/"+object_name)
        else:
            print(object_name, 'EXISTS!')




    def render(self,title,path,export=None,fileName=None):
        ax = self.fig.add_subplot(111)
        ax.clear()
        radar = pyart.io.read_nexrad_archive(path)
        display = pyart.graph.RadarDisplay(radar)
        display.plot('reflectivity', 0, title=title,ax=ax,colorbar_flag=False)

        if export:
            self.canvas.draw()
            self.fig.savefig(fileName, dpi=100)
        else:
            self.canvas.draw()

    def handleNext(self):
        if self.counter<self.nexrad_length-1:
            self.counter+=1
            object=self.nexrad.iloc[[self.counter]]
            self.download_file(object['KEY'],"nexrad")
            path=self.output_dir+object['KEY'].values[0].split('/')[4]
            self.render(str(self.counter+1)+"-"+object['KEY'].values[0].split('/')[4],path)
            self.nexrad_label.setText("NEXRAD| "+str(self.counter+1)+" out of "+str(self.nexrad_length))
            print('NEXT EVENT DONE',self.counter)

    def handlePrev(self):
        if self.counter>=1:
            self.counter-=1
            object=self.nexrad.iloc[[self.counter]]
            path=self.output_dir+object['KEY'].values[0].split('/')[4]
            self.render(str(self.counter+1)+"-"+object['KEY'].values[0].split('/')[4],path)
            self.nexrad_label.setText("NEXRAD| "+str(self.counter+1)+" out of "+str(self.nexrad_length))
            print('PREV EVENT DONE',self.counter)

    def handleExport(self):
        storm_foreign_key=self.nexrad.iloc[[0]]['FOREIGN_KEY'].values[0]

        img_dir=self.output_dir+str(storm_foreign_key)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        for inst in range(self.nexrad_length):
            object=self.nexrad.iloc[[inst]]
            self.download_file(object['KEY'],"nexrad")
            path=self.output_dir+object['KEY'].values[0].split('/')[4]
            self.render(str(inst+1)+"-"+object['KEY'].values[0].split('/')[4],path,
                    True,img_dir+"/"+str(inst+1)+"-"+object['KEY'].values[0].split('/')[4]+'.png')
            print("SAVING "+str(inst))
        print("DONE!")



def graph(nexrad,goes):
    ScrollableWindow(nexrad,goes)

