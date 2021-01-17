
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


class SingleEventWidget(QMainWindow):
    def __init__(self,parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.master_layout = QGridLayout()
        #total = self.parent.parent.asic1.single_total
        self.chan_spec = copy.deepcopy(self.parent.parent.asic1.channelSpectras)
        self.mybins = self.parent.parent.asic1.mybins
        self.single_total = []
        self.create_all_channel_single_events()
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


    def create_all_channel_single_events(self):

        chanSpec = self.chan_spec

        subtotal, sube = np.histogram([], bins = self.mybins)

        for i in range(1,12):
            for j in range(1,12):
                subtotal += chanSpec[i][j]

        self.single_total = subtotal

    #def update_spectrum(self):
    #    for i in range(12):
    #        for j in range(12):
    #            if self.pixelmap.pixels[i][j].add:
    #                self.single_total += self.chanspec[i][j]
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
        print('hei')
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
        self.parent.chan_histogram.getAxis('bottom').setTextPen('k')
        self.parent.chan_histogram.getAxis('left').setTextPen('k')

    def black_theme(self):
        self.parent.penColor = 'w'
        self.parent.chan_histogram.setBackground('k')
        self.parent.chan_histogram.plot(self.parent.mybins,self.parent.single_total, stepMode = True,  fillLevel = 0, brush=(96, 125, 139,150),clear = True, pen = self.parent.penColor)
        self.parent.chan_histogram.getAxis('bottom').setTextPen('w')
        self.parent.chan_histogram.getAxis('left').setTextPen('w')



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
        self.pixButton.setStyleSheet('background-color : green')

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
