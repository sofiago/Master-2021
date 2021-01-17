import sys

sys.path.insert(1,'BreezeStyleSheets-master/')
sys.path.insert(1,'../Data')
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,QGridLayout, QScrollArea
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from PixelWindow import PixelWindow
import pandas as pd


from threading import Timer, Thread
from data_processing_GDS import dataFrameASIC
from pedestal_processing_GDS import Pedestals
import numpy as np
from multiprocessing import Process, Queue, Event
from Gain_GDS import Gains
import breeze_resources
import matplotlib.pyplot as plt




class CalibrateTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.pedestals = Pedestals(1)
        self.gains = Gains(1)
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.timer = QTimer()
        self.timer2 = QTimer()
        self.timer3 = QTimer()
        self.gainTimer = QTimer()
        self.gainTimer2 = QTimer()

        #key values
        self.irn_tot = 0
        self.std_tot = 0


        self.keys = []
        for i in range(160):
            self.keys.append('Cell'+str(i))
        print('je')
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tabs.resize(400, 200)
        # Add tabs
        self.tabs.addTab(self.tab1, "ASIC 1")
        self.tabs.addTab(self.tab2, "ASIC 2")
        self.tabs.addTab(self.tab3, "ASIC 3")
        self.tabs.addTab(self.tab4, "ASIC 4")

        # Create tab
        self.tab1.layout = QGridLayout(self)
        self.tab1.setLayout(self.tab1.layout)

        self.pedestalsCalc = QPushButton('Calculate Pedestals')
        self.tab1.layout.addWidget(self.pedestalsCalc, 1,1)
        self.pedestalsCalc.clicked.connect(self.start_logging)
        self.gainCalcButt = QPushButton('Calculate Gain Alignment')
        self.tab1.layout.addWidget(self.gainCalcButt, 2,1)
        self.gainCalcButt.clicked.connect(self.calcGain)

        self.labelEvent = QLabel('')
        self.tab1.layout.addWidget(self.labelEvent, 1,2)
        self.gainLabelEvent = QLabel('')
        self.tab1.layout.addWidget(self.gainLabelEvent,2,2)

        self.quit = QPushButton('Back',self)
        self.quit.clicked.connect(self.quit_calibrate)
        self.tab1.layout.addWidget(self.quit,10,3)
        self.quit.setObjectName('quit')
        self.noisePixelMap = PixelMap(self)
        self.noisePixelMap.type = 'noise'
        self.pedestalPixelMap = PixelMap(self)
        self.pedestalPixelMap.type = 'pedestals'
        self.gainPixelMap = PixelMap(self)
        self.gainPixelMap.type = 'gain'

        self.noiseLabel = QLabel('Noise')
        self.tab1.layout.addWidget(self.noiseLabel,5,1)
        self.pedestalsLabel = QLabel('Average pedestals per channel')
        self.tab1.layout.addWidget(self.pedestalsLabel,5,2)
        self.gainLabel = QLabel('Gain factor per channel')
        self.tab1.layout.addWidget(self.gainLabel,5,3)


        self.tab1.layout.addWidget(self.noisePixelMap,6,1)
        self.tab1.layout.addWidget(self.pedestalPixelMap,6,2)
        self.tab1.layout.addWidget(self.gainPixelMap,6,3)

        self.stdOrIRN = stdOrIRN(self)
        self.tab1.layout.addWidget(self.stdOrIRN,10,1)

        self.ave_no_all_label = QLabel('Average noise all channels:')
        self.tab1.layout.addWidget(self.ave_no_all_label,7,1)

        #self.lightOrDark = LightOrDark(self)
        #self.tab1.layout.addWidget(self.lightOrDark,0,0)
        #Distributions
        self.std_distr = pg.PlotWidget()
        self.tab1.layout.addWidget(self.std_distr,9,1)
        self.std_distr.setTitle('Distribution of noise')
        self.std_distr.setMinimumWidth(20)
        self.std_distr.setMinimumHeight(150)

        self.std_distr.setLabel('bottom', 'Noise Value [ADC]')
        self.std_distr.setLabel( 'left' ,'Counts')

        self.ped_distr = pg.PlotWidget()
        self.tab1.layout.addWidget(self.ped_distr,9,2)
        self.ped_distr.setTitle('Distribution of pedestals')
        self.ped_distr.setMinimumWidth(20)
        self.ped_distr.setMinimumHeight(150)

        self.ped_distr.setLabel('bottom', 'Pedestal Value [ADC]')
        self.ped_distr.setLabel( 'left' ,'Counts')

        self.gain_distr = pg.PlotWidget()
        self.tab1.layout.addWidget(self.gain_distr,9,3)
        self.gain_distr.setTitle('Distribution of gain factors')
        self.gain_distr.setMinimumWidth(20)
        self.gain_distr.setMinimumHeight(150)

        self.gain_distr.setLabel('bottom', 'Gain Factor')
        self.gain_distr.setLabel( 'left' ,'Counts')

        self.cathode_push = QPushButton('Cathode Info')
        self.tab1.layout.addWidget(self.cathode_push,4,1)
        self.cathode_push.clicked.connect(self.cathode_info)


        #self.df_noise  = self.parent.parent.pedestals.noise_inp
        #self.df_noise_std = self.parent.parent.pedestals.std_each_cell

        #self.pixelMapInfo = PixelMapInfo(self)
        #self.tab1.layout.addWidget(self.pixelMapInfo, 3,2)

        #self.graphWidget = pg.PlotWidget()
    #    self.tab1.layout.addWidget(self.graphWidget,2,2)
    #    hour = [1,2,3,4,5,6,7,8,9,10]
    #    temperature = [30,32,34,32,33,31,29,32,35,45]

        # plot data: x, y values
        #self.graphWidget.plot(hour, temperature)
        self.t = Thread(target = self.startThreadPed)
        self.tgain = Thread(target = self.startGain)

        #self.t.timer.timeout.connect(self.updatePedestalCount)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        parent.setCentralWidget(self.tabs)

        #parent.setCentralWidget(self.tabs)

    def cathode_info(self):                                             # <===
        self.w = Cathode(self)
        self.w.show()

    def Update_Something(self):
        self.parent.something +=1
        self.parent.somethingstr=str(self.parent.something)
        self.somethingToUpdate.setText(self.parent.somethingstr)

    def updatePedestalCount(self):
        percent = int((self.pedestals.number_of_events / self.pedestals.chunksize )*100)

        self.labelEvent.setText(str(percent)+'%')
        if self.pedestals.finished:
            self.pedestalsCalc.setText('Pedestals Ready')
            self.timer.stop()
    def updateGainCount(self):

        percent = int((self.gains.number_of_events/self.gains.len)*100)
        #print(self.gains.number_of_events)
        #print(self.gains.len)
        #print(percent)
        self.gainLabelEvent.setText(str(percent)+'%')
        if self.gains.finished:
            self.gainCalcButt.setText('Gain Ready')

    def updateMainHistogram(self):


        print('updating')
    #    self.totalNumberOfEvents.setText('Event Counter = ' + str(self.parent.asic1.sum_events_all))
        df = self.pedestals.total_mean
        x = np.arange(0,160)
        for index, row in df.iterrows():
            if index == 0:
                self.graphWidget.plot(np.arange(0,160),row['Cell0':'Cell159'].values,clear = True)

            elif index in (1,10):
                self.graphWidget.plot(np.arange(0,160),row['Cell0':'Cell159'].values,clear = False)

    def total_noise(self):
        #print('heiiiiia')
        noise_inp = self.pedestals.noise_inp
    #    print('noise_inp',noise_inp)
        no_flat = [item for sublist in noise_inp[1:] for item in sublist[1:]]
    #    print(no_flat)
        #self.irn_tot = [[np.mean(l) for l  in p] for p in self.pedestals.noise_inp]

        self.irn_tot = np.mean(no_flat)
        no_flat = np.array(no_flat)
        datamin = no_flat.min()
        datamax = no_flat.max()
        numbins = 10
        mybins = np.linspace(datamin, datamax, numbins+1)
    #    print('mybins',mybins)

        irn_histogram, e = np.histogram(no_flat, bins = mybins)

        #print(self.irn_tot)
        std_ch = self.pedestals.std_each_cell
        std_ch = std_ch.drop(255, level = 'x')
        #std_ch = std_ch.drop(0, level = 'x')

        #print(std_ch)
        std_ch = std_ch['Average std'].to_numpy()
        #print(self.pedestals.std_each_cell)
        #print(std_ch)
        self.std_tot = std_ch.mean()
        datamin_std = std_ch.min()
        datamax_std = std_ch.max()
        numbins = 10
        mybins_std = np.linspace(datamin_std,datamax_std, numbins+1)
        #print(mybins)

        std_histogram, std_e = np.histogram(std_ch, bins = mybins_std)
        #print(self.std_tot)
        if self.stdOrIRN.irn_active:
            self.ave_no_all_label.setText('Average noise all channels: '+str(self.irn_tot))
            self.std_distr.plot(e, irn_histogram,stepMode=True, fillLevel=0, brush=(96, 125, 139,150), clear = True)

        else:
            self.ave_no_all_label.setText('Average noise all channels: '+str(self.std_tot))
            self.std_distr.plot(std_e, std_histogram, stepMode=True, fillLevel=0, brush=(96, 125, 139,150), clear = True)

    def distribution_pedestals(self):

        pedestals = self.pedestals.total_mean
        print(pedestals)
        pedestals['Mean Pedestals'] = pedestals[self.keys].mean(axis = 1)
        ped_tot = pedestals['Mean Pedestals'].to_numpy()[2:]
        print(ped_tot)
        datamin = ped_tot.min()
        datamax = ped_tot.max()
        numbins = 20
        mybins = np.linspace(datamin,datamax, numbins+1)
        ped_histogram, e = np.histogram(ped_tot, bins = mybins)
        self.ped_distr.plot(e, ped_histogram, stepMode=True, fillLevel=0, brush=(96, 125, 139,150), clear = True)

    def distributions_gain(self):
        gains = self.gains.total_gain
        print(gains)
        #print(gains)
        #g_flat = [item for sublist in gains[1:] for item in sublist[1:]]

        g_flat = gains['gain'].to_numpy()
        datamin = g_flat.min()
        datamax = g_flat.max()
        numbins = 20
        mybins = np.linspace(datamin, datamax, numbins+1)

        g_histogram, e = np.histogram(g_flat, bins = mybins)
        self.gain_distr.plot(e,g_histogram,stepMode=True, fillLevel=0, brush=(96, 125, 139,150), clear = True)

    def start_logging(self):
        self.pedestalsCalc.setText('Calculating Pedestals...')
        self.stop = False
        self.t.start()
        self.timer.timeout.connect(self.updatePedestalCount)
        self.timer.start(1500)
        self.timer2.start(2000)
        self.timer3.start(2000)
        #self.t.timer.start(1500)
        #self.parent.timer1.start(1500)

    def startThreadPed(self):
        #self.parent.timer1.start(1500)
        #print(0)
        self.pedestals.read_to_panda()
        #print(self.pedestals.total_mean)
        #t.stop()

    def quit_calibrate(self):
        print('some')
        self.pedestals.stop = True
        self.parent.timer1.stop()

        #self.close()
        self.parent.back_to_main()

    def calcGain(self):
        self.gainCalcButt.setText('Calculating Gain....')
        self.tgain.start()
        self.gainTimer.timeout.connect(self.updateGainCount)
        self.gainTimer.start(2000)
        self.gainTimer2.start(2000)

        print('soon')

    def startGain(self):
        self.gains.read_to_panda()


    def closeEvent(self,event):
        print('slutt')
        self.quit_calibrate()
        #self.timer.stop()


class Cathode(QMainWindow):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.layout = QGridLayout()
        keys = []
        for i in range(160):
            keys.append('Cell'+str(i))

        df_noise  = self.parent.pedestals.noise_values
        df_noise_std = self.parent.pedestals.std_each_cell
        df_pedestals = self.parent.pedestals.total_mean
        self.penColor = self.parent.parent.window.lightOrDark.penColor

    #    self.std =
        self.graph_std = pg.PlotWidget()
        self.graph_std.showGrid(x=True, y=True, alpha=0.8)
        self.graph_std.setLabel('left', text = 'Standard Deviation')
        self.graph_std.setLabel('bottom', text = 'Cell')
        self.graph_std.setTitle('Standard Deviation')

        self.layout.addWidget(self.graph_std,1,1)

        self.graph_ped = pg.PlotWidget()
        self.graph_ped.showGrid(x=True, y=True, alpha=0.8)
        self.graph_ped.setLabel('left', text = 'Pedestal[ADC]')
        self.graph_ped.setLabel('bottom', text = 'Cell')
        self.graph_ped.setTitle('Pedestals')

        self.layout.addWidget(self.graph_ped,1,2)

        self.noiseLabel = QLabel('Overall Standard Deviation: ')
        self.layout.addWidget(self.noiseLabel,0,1)

        self.noise_inp_graph = pg.PlotWidget()
        self.noise_inp_graph.showGrid(x = True, y = True, alpha = 0.8)
        self.noise_inp_graph.setLabel('left', text = 'Noise Amplitude[ADC]')
        self.noise_inp_graph.setLabel('bottom', text = 'Instances')
        self.noise_inp_graph.setTitle('Input referred noise')

        self.noise_inp_label = QLabel('Input referred noise: ')
        self.layout.addWidget(self.noise_inp_label,2,1)

        self.layout.addWidget(self.noise_inp_graph, 3, 1)


        if not df_pedestals.empty:

            _std = df_noise_std.loc[(0,255,255)].to_numpy()
            ijpedestals = df_pedestals[(df_pedestals['x'] == 255) & (df_pedestals['y']== 255)][keys].to_numpy()[0]
            x = np.arange(len(ijpedestals)+1)
            self.graph_ped.plot(x, ijpedestals, stepMode=True, fillLevel=0, pen = self.penColor ,brush=(96, 125, 139,150),clear = True)
            #self.pedestalswidget.plot(x, ijpedestals, clear = True)
            self.graph_ped.setYRange(4000, 6000)
            #self.pedestalswidget.setTitle(title = 'Pedestals')

            average_std = np.mean(_std)
            self.noiseLabel.setText('Overall Standard Deviation: '+str(average_std))
            pen = pg.mkPen(color = self.penColor, width = 3)
            self.graph_std.plot(np.arange(len(_std)), _std, pen = pen)
            noise_inp = df_noise[0][0]
            tot_noise_inp = np.std(noise_inp)
            self.noise_inp_label.setText('Overall Standard Deviation: '+str(tot_noise_inp))

            self.noise_inp_graph.plot(np.arange(len(noise_inp)), noise_inp, pen=None, symbol='o',brush=(96, 125, 139,150))

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('Cathode channel')


class stdOrIRN(QWidget):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)

        self.irn = QPushButton('Input Referred Noise')
        self.widget.layout.addWidget(self.irn,0,0)
        self.std = QPushButton('Average Standard Deviation')
        self.widget.layout.addWidget(self.std,0,1)

        #self.irn.setStyleSheet('background-color : #7f848a')
        self.irn.setStyleSheet('background-color : #e5e5e5')

        self.irn_active = True
        self.std_active = False
        self.std.setStyleSheet('background-color : #a6a6a6')
        self.irn.clicked.connect(self.display_irn)
        self.std.clicked.connect(self.display_std)

    def display_irn(self):

        if not self.irn_active:
            self.irn.setStyleSheet('background-color : #e5e5e5')
            self.std.setStyleSheet('background-color : #a6a6a6')
            self.irn_active = True
            self.std_active = False
            self.parent.noisePixelMap.irn = True
            self.parent.noisePixelMap.update_pixel_noise_label()
            #self.ave_no_all_label.setText('Average noise all channels:'+str(self.irn_tot))

    def display_std(self):
        if not self.std_active:
            self.irn.setStyleSheet('background-color : #e5e5e5')
            self.std.setStyleSheet('background-color : #a6a6a6')
            self.irn_active = False
            self.std_active = True
            self.parent.noisePixelMap.irn = False
            self.parent.noisePixelMap.update_pixel_noise_label()





class Pixel(QWidget):
    def __init__(self,parent,i,j):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        #self.name = '('+str(i)+','+str(j)+')'
        self.widget = QWidget()
        self.keys = self.parent.parent.keys
        self.i = i
        self.j = j
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        self.push = QPushButton()
        self.push.clicked.connect(self.PixelWindow)
        self.push.setObjectName('pixel')
        self.widget.layout.addWidget(self.push, 0, 0)
        #self.irn = self.parent.irn

    def PixelWindow(self):                                             # <===
        self.w = PixelWindow(self,self.i,self.j)
        self.w.show()

    def update_noise_name(self):
        max_std = 0

        df_noise  = self.parent.parent.pedestals.noise_inp
        df_noise_std = self.parent.parent.pedestals.std_each_cell
        df_noise_std = df_noise_std.drop(255, level = 'x')
        #df_noise_std = df_noise_std.drop(0, level = 'x')
        #print(df_noise_std)
        #print(df_noise)
        #print(df_noise)
        if self.parent.irn:
            #largest  = np.max(df_noise[1:])
            #print(largest)
            for list in df_noise[1:]:
                #list=filter(None, list)
                b= np.max(list)
                #print(b)
                if b>max_std:
                    max_std=b
            #b = max(df_noise)
            #print(b)
            #print('max',max_std)
            #print(self.i)
            #print(self.j)
            #print('noise',df_noise[self.i][self.j])
            noise = round(df_noise[self.i][self.j],2)
            #print(noise)
        else:
            #print('themaxest')

            max_std = df_noise_std['Average std'].max()
            #print(df_noise_std.loc[(self.i,self.j)][self.keys])
            noise = df_noise_std.loc[(1,self.i,self.j)]['Average std']
            #print(noise)



            #print(noise)

            #largest = np.max(df_noise_std)
            noise = round(np.mean(noise),2)


        self.push.setText(str(noise))

        c = format(int(205-((noise/max_std)*205)),'02x')

        self.push.setStyleSheet('background-color : #ff'+str(c)+str(c))


        #if noise <= 10:
        #    self.push.setStyleSheet('background-color : silver')
        #elif (noise > 10) and (noise <= 30):
        #    self.push.setStyleSheet('background-color : rosybrown')
        #elif (noise > 30) and (noise <= 40):
        #    self.push.setStyleSheet('background-color : indianred')
        #elif (noise > 40) and (noise <= 50):
        #    self.push.setStyleSheet('background-color : firebrick')
        #elif (noise > 50):
        #    self.push.setStyleSheet('background-color : maroon')



    def update_pedestal_name(self):
        mean_df = self.parent.parent.pedestals.total_mean
        #print(mean_df)
        meanInfo = mean_df[(mean_df['x'] == self.i) & (mean_df['y'] == self.j)].values[0][3:]

        mean = np.mean(meanInfo)
        #mean = int(df_mean[self.i][self.j])
        self.push.setText(str(int(mean)))
        if mean < 8000:
            self.push.setStyleSheet('background-color :lightblue')
        elif (mean > 8000) and (mean <= 8100):
            self.push.setStyleSheet('background-color : cadetblue')
        elif (mean > 8100) and (mean <= 8200):
            self.push.setStyleSheet('background-color : turquoise')
        elif (mean > 8200) and (mean <= 8300):
            self.push.setStyleSheet('background-color : teal')
        elif (mean > 8300) and (mean <= 8400):
            self.push.setStyleSheet('background-color : darkcyan')
        elif (mean > 8400):
            self.push.setStyleSheet('background-color : darkslategray')

    def update_gain_name(self):
        max_gain = 1
        gains = self.parent.parent.gains.total_gain
        #print(gains)
        #for list in gains[1:]:
            #for l in list:
            #list=filter(None, list)
                #b = np.max(list)
                #print(b)
                #print(b)
                #if b>max_gain:
                  # max_gain=b
        all_gain = gains['gain']
        max_gain = all_gain.max()
        min_gain = all_gain.min()
        gain = gains[(gains['x']==self.i) & (gains['y'] == self.j)]['gain'].to_numpy()[0]
        #c = format(int(205-(((gain-min_gain)/max_gain)*205)),'02x')
        #print(c)
        #print(gain)
        #print(min_gain)
        #print(max_gain)
        c = int(((gain-min_gain)/(max_gain-min_gain))*10)
        #print((gain-min_gain)/(max_gain-min_gain))
        #print(c)
        #print('max',max_gain)
        #print(gain)
        #gain = round(gain,2)
        #col_arr = ['#048048','#138551','#1b8554','#24875a','#2a875d','#308a61','#3a8764','#428768','#4d8a6e','#588771']
        col_arr = ['#6e8f7f','#588771','#4d8a6e','#428768','#3a8764','#308a61','#2a875d','#24875a','#1b8554','#138551','#048048']
        #print(len(col_arr))
        #print(str(c)+'ff'+str(c))

        self.push.setText(str(round(gain,2)))

        self.push.setStyleSheet('background-color : '+col_arr[c])


class PixelWindow(QMainWindow):
    def __init__(self,parent,i,j):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.i = i
        self.j = j
        self.pedestals = self.parent.parent.parent.pedestals.total_mean
        self.std = self.parent.parent.parent.pedestals.std_each_cell
        self.gains = self.parent.parent.parent.gains.gain_values
        self.noise_inp = self.parent.parent.parent.pedestals.noise_values

        self.keys = []
        for i in range(160):
            self.keys.append('Cell'+str(i))

        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QGridLayout()
        self.penColor = self.parent.parent.parent.parent.window.lightOrDark.penColor
        print(self.penColor)                                # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.noiseLabel=QLabel('Average Standard Deviation Noise:')
        #Add stuff here

        gainwidget = pg.PlotWidget()
        gainwidget.setLabel('left', text = 'Amplitude[ADC]')
        #gainwidget.setLabel('bottom', text = ' ')
        gainwidget.setTitle('Cal pulse amplitudes')
        gainwidget.showGrid(x=True, y=True, alpha=0.8)


        self.vbox.addWidget(gainwidget,3,3)

        self.pedestalswidget = pg.PlotWidget(font_size = 20)
        self.pedestalswidget.setLabel('left', text = 'Pedestals[ADC]')
        self.pedestalswidget.setLabel('bottom', text = 'Cell')
        self.pedestalswidget.setTitle(title = 'Pedestals')
        self.pedestalswidget.showGrid(x=True, y=True, alpha=0.8)

        self.noiseReadoutwidget = pg.PlotWidget()
        self.noiseReadoutwidget.showGrid(x=True, y=True, alpha=0.8)
        self.noiseReadoutwidget.setLabel('left', text = 'Standard Deviation')
        self.noiseReadoutwidget.setLabel('bottom', text = 'Cell')
        self.noiseReadoutwidget.setTitle('Standard Deviation')

        self.inpNoiseReadoutWidget = pg.PlotWidget()
        self.inpNoiseReadoutWidget.showGrid(x=True, y=True, alpha=0.8)
        self.inpNoiseReadoutWidget.setLabel('left', text = 'Input Referred Noise Amplitude[AC]')
        self.inpNoiseReadoutWidget.setTitle('Input Referred Noise')
        self.vbox.addWidget(self.inpNoiseReadoutWidget,3,2)

        self.vbox.addWidget(self.pedestalswidget,2,3)
        print(self.pedestals.empty)
        if not self.pedestals.empty:
            print('hei')
            ijpedestals = self.pedestals[(self.pedestals['x'] == self.i) & (self.pedestals['y']== self.j)][self.keys].to_numpy()[0]
            print(ijpedestals)
            #print(self.pedestals)
            x = np.arange(len(ijpedestals)+1)
            #print(len(x))
            self.pedestalswidget.plot(x, ijpedestals, stepMode=True, fillLevel=0, pen = self.penColor ,brush=(96, 125, 139,150),clear = True)
            #self.pedestalswidget.plot(x, ijpedestals, clear = True)
            self.pedestalswidget.setYRange(7500, 9000)
            #self.pedestalswidget.setTitle(title = 'Pedestals')
            _std = self.std.loc[(1,self.i,self.j)].to_numpy()
            average_std = np.mean(_std)
            self.noiseLabel.setText('Average Standard Deviation Noise: '+str(average_std))
            pen = pg.mkPen(color = self.penColor, width = 3)
            self.noiseReadoutwidget.plot(np.arange(len(_std)), _std, pen = pen)
            noise_inp = self.noise_inp[self.i][self.j]
            self.inpNoiseReadoutWidget.plot(np.arange(len(noise_inp)), noise_inp,pen=None, symbol='o',brush=(96, 125, 139,150))


        ch_gains = self.gains[self.i][self.j]
        print(ch_gains)
        if len(ch_gains)> 1:
            gainwidget.plot(np.arange(len(ch_gains)),ch_gains, pen=None, symbol='o',brush=(96, 125, 139,150))
            #scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'), symbol='o', size=1)
            #gainwidget.addItem(scatter)
            #pos = [{'pos': ch_gains[:, i]} for i in range(3)]
            #scatter.setData(pos)
        #print(self.std)
        #self.noiseReadoutwidget = pg.PlotWidget()
        #self.noiseReadoutwidget.setLabel('left', text = 'Standard Deviation')
        #self.noiseReadoutwidget.setLabel('bottom', text = 'Cell')
        #_std = self.std.loc[(self.i,self.j)].to_numpy()
        #print(_std)
        #average_std = round(np.mean(_std))
        #print('hallo???')
        #print(average_std)
        self.vbox.addWidget(self.noiseReadoutwidget,2,2)
        #self.noiseLabel=QLabel('Average Standard Deviation: '+str(average_std))
        self.vbox.addWidget(self.noiseLabel,1,2)


        #or i in range(1,50):
        #    object = QLabel("TextLabel")
        #    self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        df = pd.read_csv('asic_nr.csv', sep = ';')
        self.name = df[(df['x'] == self.i) & (df['y'] == self.j)]['asic'].values[0]


        self.setWindowTitle('X: '+ str(self.i)+ ' Y: '+str(self.j) + ' Channelnr: '+str(self.name))
        self.show()



class PixelMap(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        self.pixels = []
        self.type = ''
        self.irn  = True
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,i+2,0)
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,0,i+2)

        for i in range(1,12):
            for j in range(1,12):
                pix = Pixel(self,i,j)
                self.widget.layout.addWidget(pix, i+2, j+2)
                self.pixels.append(pix)

        self.parent.timer3.timeout.connect(self.check_finished)
        self.parent.gainTimer.timeout.connect(self.check_finished_gain)

    def check_finished(self):
        if self.parent.pedestals.finished:
            self.update_pixel_noise_label()
            self.parent.timer3.stop()

    def check_finished_gain(self):
        if self.parent.gains.finished:
            self.parent.gainTimer.stop()
            if self.type == 'gain':
                for pix in self.pixels:
                    pix.update_gain_name()
                    self.parent.distributions_gain()



    def update_pixel_noise_label(self):
        if self.type == 'noise':
            for pix in self.pixels:
                pix.update_noise_name()
            self.parent.total_noise()
        elif self.type == 'pedestals':
            for pix in self.pixels:
                pix.update_pedestal_name()
            self.parent.distribution_pedestals()
        elif self.type == 'gain':

            #
            print('ehm')
            #for pix in self.pixels:
            #    pix.update_gain_name()
            #print('Not ready freddy')


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
