import sys
sys.path.append('../')
sys.path.insert(1,'BreezeStyleSheets-master/')
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,QGridLayout,QGroupBox,QSpinBox,QFormLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import threading
import numpy as np
from scipy.signal import find_peaks, peak_widths

import breeze_resources

#pyrcc5 BreezeStyleSheets-master/breeze.qrc -o breeze_resources.py

class PixelWindow(QMainWindow):
    def __init__(self,parent, i , j):
        super(QWidget,self).__init__(parent)
        self.i = i
        self.j = j
        self.parent = parent
        self.widget = QWidget()
        self.master_layout = QGridLayout()

        self.nr_events_label=QLabel()
        #self.nr_of_events = 44656
        self.nr_events_label.setText(str(0))
        self.penColor = self.parent.parent.parent.lightordark.penColor

        self.master_layout.addWidget(self.nr_events_label, 1,2)
        self.quit  = QPushButton('Quit', self)
        self.quit.clicked.connect(self.quit_pixel)

        self.master_layout.addWidget(self.quit,20,20)

        self.widget.setLayout(self.master_layout)
        self.setCentralWidget(self.widget)
        #datamin = 0
        #datamax = 6000
        #numbins = 2000
        self.mybins = self.parent.parent.parent.parent.asic1.mybins
        #self.hist, self.e = np.histogram([],numbins, range = (0,numbins ))

        self.chan_histogram = pg.PlotWidget()
        self.chan_histogram.showGrid(x=True, y=True, alpha=0.8)
        self.chan_histogram.setLabel('bottom', 'ADC Value')
        self.chan_histogram.setLabel( 'left' ,'Counts')
        self.master_layout.addWidget(self.chan_histogram,2,2)
        #self.chan_histogram.plot([0,0],[0,0])
        self.timer = QTimer()
        #self.tot = self.parent.parent.parent.parent.asic1.channelSpectras[3]
        self.timer.timeout.connect(self.updateChannelHistogram)
        self.timer.start(3000)
        #print(self.tot)

        self.fwhmWidget = fwhmWidget(self)

        self.master_layout.addWidget(self.fwhmWidget,4,2)

        #---------------Manually peak entry -------------------------
        self.formGroupBox = QGroupBox("Peak Value")
        self.peakEntry = QSpinBox()
        self.enterPush = QPushButton('Manual Peak Entry')
        self.enterPush.clicked.connect(self.collectPeaks)
        self.peakEntry.setRange(0,50000)
        layout = QFormLayout()
        layout.addRow(self.enterPush, self.peakEntry)

        self.formGroupBox.setLayout(layout)

        self.master_layout.addWidget(self.formGroupBox, 3,2)


    def updateChannelHistogram(self):
        if self.parent.parent.all:
            sub = self.parent.parent.parent.parent.asic1.channelSpectras_all[self.i][self.j]
        else:
            sub = self.parent.parent.parent.parent.asic1.channelSpectras[self.i][self.j]
        #print(sub)
        #df_sub = self.sub.sort_index(axis = 0, level = None, ascending = True)
        #print(self.sub.index)
        #print()
        #hist, sube = np.histogram(self.sub.index, bins = self.mybins)
        #print(hist)
        #print(sube)
        #x = df_tot.index.values
        #y = df_tot.values
        self.chan_histogram.plot(self.mybins,sub, stepMode=True, fillLevel=0, brush=(96, 125, 139,150),clear = True, pen = self.penColor)
        Sum = sum(sub)
        #print(sub)
        self.nr_events_label.setText('Event Counter: '+str(Sum))




        #self.chan_histogram.plot(x,y,clear = True)

    def quit_pixel(self):
        self.timer.stop()
        self.close()

    def closeEvent(self,event):
        self.timer.stop()

    def get_text(self):
        self.peak_value = self.peakEntry.text()

    def detect_peak(self):
        sub = self.parent.parent.parent.parent.asic1.channelSpectras_all[self.i][self.j]
        peaks, properties = find_peaks(sub, prominence = 5, width=2)
        print(peaks)

        left_ips = [round(properties["left_ips"][-1])]
        right_ips = [round(properties["right_ips"][-1])]
        left_ips = sub[left_ips]
        right_ips = sub[right_ips]
        x_peak = sub[peaks[-1]]
        #print(left_ips, right_ips, x_peak )
        self.fwhm = (right_ips - left_ips)/x_peak*10

        self.peak_value.setValue(x_peak)


    def collectPeaks(self):
        print(self.peakEntry.text())
        self.parent.parent.parent.peak_channel[self.i][self.j] = self.peakEntry.text()



class fwhmWidget(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent

        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.fwhmButton = QPushButton('FWHM')
        self.fwhmButton.clicked.connect(self.parent.detect_peak)
        self.fwhmLabel = QLabel('FWHM: ')
        self.widget.layout.addWidget(self.fwhmButton, 1, 1)
        self.widget.layout.addWidget(self.fwhmLabel, 1, 2)
