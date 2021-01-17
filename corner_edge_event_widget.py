
import sys
sys.path.append('../')
sys.path.insert(1,'BreezeStyleSheets-master/')
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,QGridLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import threading
import numpy as np
import copy
import pandas as pd

import breeze_resources


class Corner_Edge_EventWidget(QMainWindow):
    def __init__(self,parent,corner):
        super(QWidget, self).__init__(parent)
        self.parent = parent.parent
        self.widget = QWidget()
        self.master_layout = QGridLayout()
        self.corner = corner
        #total = self.parent.parent.asic1.single_total
        self.chan_spec = copy.deepcopy(self.parent.parent.asic1.channelSpectras)
        self.chan_spec_all = copy.deepcopy(self.parent.parent.asic1.channelSpectras_all)
        self.mybins = self.parent.parent.asic1.mybins
        self.single_total = []
        self.all = False
        if corner:
            self.create_corner_single_events()
        else:
            self.create_edge_single_events()

        self.chan_histogram = pg.PlotWidget()
        self.master_layout.addWidget(self.chan_histogram,1,1)
        self.penColor = self.parent.lightordark.penColor

        self.chan_histogram.plot(self.mybins,self.single_total, stepMode = True,  fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen = self.penColor)
        self.chan_histogram.showGrid(x=True, y=True, alpha=0.9)
        label_style = {"color":'#EEE',"font_size":"20pt"}
        self.chan_histogram.setLabel('bottom', 'ADC Value',**label_style)
        self.chan_histogram.setLabel( 'left' ,'Counts',**label_style)

        self.pixelmap = PixelMapSingle(self)
        self.master_layout.addWidget(self.pixelmap,1,2)

        self.widget.setLayout(self.master_layout)
        self.setCentralWidget(self.widget)

        self.blackOrWhite = BlackOrWhite(self)
        self.master_layout.addWidget(self.blackOrWhite,2,1)

        self.SingleOrAll = SingleOrAll(self)
        self.master_layout.addWidget(self.SingleOrAll,2,2)


    def create_corner_single_events(self):
        if self.all:
            chanSpec = self.chan_spec_all
        else:
            chanSpec = self.chan_spec

        subtotal, sube = np.histogram([], bins = self.mybins)

        for i in (1,11):
            for j in (1,11):
                subtotal += chanSpec[i][j]


        self.single_total = subtotal

    #def update_spectrum(self):
    #    for i in range(12):
    #        for j in range(12):
    #            if self.pixelmap.pixels[i][j].add:
    #                self.single_total += self.chanspec[i][j]

    def create_edge_single_events(self):

        if self.all:
            chanSpec = self.chan_spec_all
        else:
            chanSpec = self.chan_spec

        subtotal, sube = np.histogram([], bins = self.mybins)

        for i in (1,11):
            for j in range(2,11):
                subtotal += chanSpec[i][j]
        for i in range(2,11):
            for j in (1,11):
                subtotal += chanSpec[i][j]

        self.single_total = subtotal


    def add_subspectrum(self,i,j):
        #print(self.chan_spec[i-1][j-1])
        self.single_total += self.chan_spec[i][j]
        self.chan_histogram.plot(self.mybins,self.single_total, stepMode = True,  fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen =self.penColor)
        self.chan_histogram.showGrid(x=True, y=True, alpha=0.9)


    def remove_subspectrum(self,i,j):
        #print(self.single_total)
        #print(self.chan_spec[i-1][j-1])
        self.single_total -= self.chan_spec[i][j]
        self.chan_histogram.plot(self.mybins,self.single_total, stepMode = True, fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen = self.penColor)

        #print(self.single_total)
        self.chan_histogram.showGrid(x=True, y=True, alpha=0.9)

class BlackOrWhite(QWidget):
    def __init__(self,parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)

        self.whiteButt = QPushButton('White')
        self.blackButt = QPushButton('Black')

        self.widget.layout.addWidget(self.whiteButt, 0, 0)
        self.widget.layout.addWidget(self.blackButt, 0, 1)

        self.whiteButt.clicked.connect(self.white_theme)
        self.blackButt.clicked.connect(self.black_theme)



    def white_theme(self):
        self.parent.penColor = 'k'
        self.parent.chan_histogram.setBackground('w')
        self.parent.chan_histogram.plot(self.parent.mybins,self.parent.single_total, stepMode = True,  fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen = self.parent.penColor)


    def black_theme(self):
        self.parent.penColor = 'w'
        self.parent.chan_histogram.setBackground('k')
        self.parent.chan_histogram.plot(self.parent.mybins,self.parent.single_total, stepMode = True,  fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen = self.parent.penColor)

class SingleOrAll(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout =  QGridLayout(self)

        self.AllEvents = QPushButton('All Events')
        self.SingleEvents = QPushButton('Single Interaction Events')
        self.SingleEvents.setStyleSheet('background-color : #7f848a')
        self.AllEvents.setStyleSheet('background-color : #31363b')
        self.widget.layout.addWidget(self.AllEvents)
        self.widget.layout.addWidget(self.SingleEvents)

        self.AllEvents.clicked.connect(self.DisplayAllEvents)
        self.SingleEvents.clicked.connect(self.DisplaySingleEvents)


    def DisplayAllEvents(self):
        if not self.parent.all:
            self.AllEvents.setStyleSheet('background-color : #7f848a')
            self.SingleEvents.setStyleSheet('background-color : #31363b')
            self.parent.all = True
            if self.parent.corner:
                self.parent.create_corner_single_events()
            else:
                self.parent.create_edge_single_events()

    def DisplaySingleEvents(self):
        if self.parent.all:
            self.SingleEvents.setStyleSheet('background-color : #7f848a')
            self.AllEvents.setStyleSheet('background-color : #31363b')
            self.parent.all = False
            if self.parent.corner:
                self.parent.create_corner_single_events()
            else:
                self.parent.create_edge_single_events()





class PixelMapSingle(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.df_nr = pd.read_csv('asic_nr.csv', sep = ';')
        #print(self.df_nr)
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        #self.curr_largest_sum = 0
        #self.colormap = ['#581845','#5E35B1','#5C6BC0','#00838F','#00BFA5','#81C784','#4CAF50','#AEEA00','#EEFF41','#FDD835']
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,i+2,0)
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,0,i+2)
        self.pixels =[]

        for i in range(1,12):
            for j in range(1,12):
                pix = PixelSingle(self,i,j)
                self.widget.layout.addWidget(pix, i+2, j+2)
                self.pixels.append(pix)

class PixelSingle(QWidget):
    def __init__(self,parent,i,j):
        super(QWidget,self).__init__(parent)
        self.i = i
        self.j = j
        self.parent = parent
        df = self.parent.df_nr
        #print(df)
        #print(self.i)
        #print(self.j)
        self.name = df[(df['x'] == self.i) & (df['y'] == self.j)]['asic'].values[0]
        #print(self.name)


        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        #print(self.name)
        self.pixButton = QPushButton(str(self.name))
        self.pixButton.clicked.connect(self.add_to_single)
        self.pixButton.setObjectName('pixel')
        if self.parent.parent.corner:
            if self.i in (1,11) and self.j in (1,11):
                self.pixButton.setStyleSheet('background-color : green')
            else:
                self.pixButton.setStyleSheet('background-color : red')
        else:
            if (self.i in (1,11) and self.j in range(2,11)) or (self.i in range(2,11) and self.j in (1,11)):
                self.pixButton.setStyleSheet('background-color : green')
            else:
                self.pixButton.setStyleSheet('background-color : red')



        self.widget.layout.addWidget(self.pixButton, 0, 0)
        self.add = True

    def add_to_single(self):
        if self.add:
            self.add = False
            self.pixButton.setStyleSheet('background-color : red')
            self.parent.parent.remove_subspectrum(self.i, self.j)
        else:
            self.add = True
            self.pixButton.setStyleSheet('background-color : green')
            self.parent.parent.add_subspectrum(self.i, self.j)
