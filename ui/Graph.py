import matplotlib.pyplot as plt
import pyart
import settings.local as local
import boto3
import os
import math


import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class ScrollableWindow(QtGui.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtGui.QApplication([])

        QtGui.QMainWindow.__init__(self)
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtGui.QVBoxLayout())
        self.widget.layout().setContentsMargins(5,5,5,5)
        self.widget.layout().setSpacing(5)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtGui.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        exit(self.qapp.exec_())



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

def render(ax,title,path):
    radar = pyart.io.read_nexrad_archive(path)
    display = pyart.graph.RadarDisplay(radar)
    display.plot('reflectivity', 0, title=title,ax=ax)

def graph(objects):
    objects_length=len(objects)
    rows=math.ceil(objects_length/2)

    # single graph
    if rows==1 and objects_length==1:
        fig, ax = plt.subplots(ncols=1, nrows=rows, figsize=(10,5))
        object=objects.iloc[[0]]
        path="ui_objects/"+object['KEY'].values[0].split('/')[4]
        print('GRAPHING',path)
        render(ax,object['KEY'].values[0].split('/')[4],path)
        ScrollableWindow(fig)
        return

    fig, axes = plt.subplots(ncols=2, nrows=rows, figsize=(19,39))
    c=0
    for ax in axes.flatten():
        if c<objects_length:
            object=objects.iloc[[c]]
            path="ui_objects/"+object['KEY'].values[0].split('/')[4]
            print((c+1),'GRAPHING',path)
            render(ax,object['KEY'].values[0].split('/')[4],path)
            c+=1

    ScrollableWindow(fig)

