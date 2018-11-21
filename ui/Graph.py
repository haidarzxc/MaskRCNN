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
    def __init__(self,objects):
        self.qapp = QtGui.QApplication([])

        self.objects=objects
        self.counter=-1
        self.objects_length=len(objects)

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

        self.status_label = QtGui.QLabel()
        self.status_label.setText("total: "+str(self.objects_length))

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
        self.bar.layout().addWidget(self.status_label)
        self.bar.layout().addStretch()
        self.bar.layout().addStretch()

        self.widget.layout().addWidget(self.bar)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)



        self.show()
        exit(self.qapp.exec_())

    def download_file(self,key,bucket):
        object_name=key.values[0].split('/')[4]
        output_dir="ui_objects"
        file = Path(output_dir+"/"+object_name)
        if not file.is_file():
            print("DOWNLOADING",object_name)
            if bucket=="nexrad":
                get_aws_object("noaa-nexrad-level2",key.values[0],output_dir+"/"+object_name)
            elif bucket=="goes":
                get_aws_object("noaa-goes16",key.values[0],output_dir+"/"+object_name)
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
        if self.counter<self.objects_length-1:
            self.counter+=1
            object=self.objects.iloc[[self.counter]]
            self.download_file(object['KEY'],"nexrad")
            path="ui_objects/"+object['KEY'].values[0].split('/')[4]
            self.render(str(self.counter+1)+"-"+object['KEY'].values[0].split('/')[4],path)
            self.status_label.setText(str(self.counter+1)+" out of "+str(self.objects_length))

    def handlePrev(self):
        if self.counter>=0:
            self.counter-=1
            object=self.objects.iloc[[self.counter]]

            path="ui_objects/"+object['KEY'].values[0].split('/')[4]
            self.render(str(self.counter+1)+"-"+object['KEY'].values[0].split('/')[4],path)
            self.status_label.setText(str(self.counter+1)+" out of "+str(self.objects_length))

    def handleExport(self):
        storm_foreign_key=self.objects.iloc[[0]]['FOREIGN_KEY'].values[0]

        img_dir="ui_objects/"+str(storm_foreign_key)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        for inst in range(self.objects_length):
            object=self.objects.iloc[[inst]]
            self.download_file(object['KEY'],"nexrad")
            path="ui_objects/"+object['KEY'].values[0].split('/')[4]
            self.render(str(inst+1)+"-"+object['KEY'].values[0].split('/')[4],path,
                    True,img_dir+"/"+str(inst+1)+"-"+object['KEY'].values[0].split('/')[4]+'.png')
            print("SAVING"+str(inst))
        print("DONE!")



def graph(objects):
    ScrollableWindow(objects)

