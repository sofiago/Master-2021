import sys

sys.path.insert(1,'BreezeStyleSheets-master/')
sys.path.insert(1,'../Data')
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,QGridLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from PixelWindow import PixelWindow
import threading
from data_processing_GDS import dataFrameASIC
import numpy as np
from multiprocessing import Process, Queue, Event
import breeze_resources
import matplotlib.pyplot as plt
from CalibrateTabWidget import CalibrateTabWidget



class PixelMap(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        self.curr_largest_sum = 0
        #changes the pixelmaps to all events
        self.all = False
        self.colormap = ['#581845','#5E35B1','#5C6BC0','#00838F','#00BFA5','#81C784','#4CAF50','#AEEA00','#EEFF41','#FDD835']
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,i+2,0)
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,0,i+2)
        self.pixels =[]

        for i in range(1,12):
            for j in range(1,12):
                pix = Pixel(self,i,j)
                self.widget.layout.addWidget(pix, i+2, j+2)
                self.pixels.append(pix)

        #self.button = PixelButton(self.w)
        #self.w.layout.addWidget(self.button, 0, 0)

        #self.push2 = QPushButton('Button (0, 1)')
        #self.push2.setObjectName('pixel')
        #self.layout.addWidget(self.push2, 0, 1)


        #self.layout.addWidget(QPushButton('Button (0, 2)'), 0, 2)
        #self.layout.addWidget(QPushButton('Button (1, 0)'), 1, 0)
        #self.layout.addWidget(QPushButton('Button (1, 1)'), 1, 1)
        #self.layout.addWidget(QPushButton('Button (1, 2)'), 1, 2)
        #self.layout.addWidget(QPushButton('Button (2, 0)'), 2, 0)
'''
class PixelmapInfo(QWidget):
    def __init__(self,parent, i ,j):
        self.parent = parent
        self.widget = QWidget()

        for i in range(1,12):
            for j in range(1,12):
                self.widget.layout.addWidget(PixelInfo(self,i,j), i+2, j+2)


class PixelInfo(QWidget):
    def __init__(self, parent, i, j):
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.noiseLabel = QLabel('Noise',self)
        self.widget.layout.addWidget(0,0)
        self.MeanLabel = QLabel('Mean',self)
        self.widget.layout.addWidget(0,1)
        self.GainAvLabel = QLabel('Gain Average',self)
        self.widget.layout.addWidget(1,1)
'''



class Pixel(QWidget):
    def __init__(self,parent,i,j):
        super(QWidget,self).__init__(parent)
        self.i = i
        self.j = j
        self.parent = parent
        self.name = '('+str(i)+','+str(j)+')'
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        self.pixButton = QPushButton(self.name)
        self.pixButton.clicked.connect(self.PixelWindow)
        self.pixButton.setObjectName('pixel')
        self.widget.layout.addWidget(self.pixButton, 0, 0)

    def update_amount(self):
        colormap = self.parent.colormap
        #print(self.parent.all)
        if self.parent.all:
            sub = self.parent.parent.parent.asic1.channelSpectras_all[self.i][self.j]
            #print('yes')
        else:
            sub = self.parent.parent.parent.asic1.channelSpectras[self.i][self.j]
        Sum = sum(sub)
        if Sum > self.parent.curr_largest_sum:
            self.parent.curr_largest_sum = Sum
        self.pixButton.setText(str(Sum))

        if  Sum == 0:
            self.pixButton.setStyleSheet('background-color : #263238')
            return


        part = int((Sum/self.parent.curr_largest_sum)*10)
        if part == 0:
            self.pixButton.setStyleSheet('background-color :'+str(colormap[0]))
            return

        self.pixButton.setStyleSheet('background-color :'+str(colormap[part-1]))


    def PixelWindow(self):                                             # <===
        self.w = PixelWindow(self,self.i,self.j)
        self.w.show()
