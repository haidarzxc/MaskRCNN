from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pyart

'''
Frame class
inherits QtGui window
input arguments:
    1. data (goes clipped version)
    2. nexrad_object
    3. goes_object

output: export .png image of nexrad and goes
'''
class Frame(QtGui.QMainWindow):
    def __init__(self,data,nexrad_object,goes_object):
        self.qapp = QtGui.QApplication([])
        self.nexrad_object=nexrad_object
        self.data=data
        self.goes_object=goes_object


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
        # , extent=[1000,120,32,0] changes axis
        ax0.imshow(data)

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


        self.fig.savefig("goes_intersections/output/"+nexrad_object['KEY'].replace("/","_")+"__"+goes_object['KEY'].replace("/","")+".png", dpi=100)
        # self.show()
        # exit(self.qapp.exec_())