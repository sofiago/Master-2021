import sys

sys.path.insert(1,'BreezeStyleSheets-master/')
sys.path.insert(1,'../Data')
from PyQt5.QtCore import QFile, QTextStream, Qt, QTimer, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel,QGridLayout
from pyqtgraph import PlotWidget, plot
from pyqtgraph.Qt import QtGui, QtCore

import pyqtgraph as pg
from PixelWindow import PixelWindow
import threading
from data_processing_GDS import dataFrameASIC
import numpy as np
from multiprocessing import Process, Queue, Event
import breeze_resources
import matplotlib.pyplot as plt
from CalibrateTabWidget import CalibrateTabWidget
from single_event_widget import SingleEventWidget
from corner_edge_event_widget import Corner_Edge_EventWidget
from PixelMap import PixelMap
import time
import os
import glob
import csv
import pandas as pd



#pyrcc5 BreezeStyleSheets-master/breeze.qrc -o breeze_resources.py


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        #main code here
        self.width = 400
        self.height = 200
        self.left = 0
        self.top = 0
        self.stop = False #flagg in thread
        self.stop_calibrate = False
        self.something = 0 #for testing
        self.somethingstr = str(self.something)
        self.timer = QTimer()
        self.timer1 = QTimer()
        self.asic1 = dataFrameASIC(1)
        self.app = app

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.title = ('Optimizer Sofiatron 3000')
        self.setWindowTitle(self.title)
        #pg.setConfigOption('background', 'w')
        #pg.setConfigOption('foreground', 'b')
        #print(pg.getConfigOption)
        #self.setFixedSize(self.layout.sizeHint())
        #self.tab_widget = MyTabWidget(self)
        #self.setCentralWidget(self.tab_widget)
        '''
        self.verticalLayout = QGridLayout()

        self.quit  = QPushButton('Quit')
        self.quit.clicked.connect(self.calibrateMode)
        self.quit.setObjectName('quit')

        self.verticalLayout.addWidget(self.quit,3,3)

        self.calibrateButton = QPushButton('Calibrate')
        self.verticalLayout.addWidget(self.calibrateButton, 1,1)
        self.calibrateButton.setObjectName('calibrate')
        self.calibrateButton.clicked.connect(self.calibrateMode)

        self.calibratedButton = QPushButton('Calibrated')
        self.verticalLayout.addWidget(self.calibratedButton,1,2)
        self.calibratedButton.setObjectName('calibrate')

        self.calibratedButton.clicked.connect(self.calibratedMode)

        #self.start_button = QPushButton('Start logging')
        #self.verticalLayout.addWidget(self.button)

        self.widget = QWidget()
        self.setLayout(self.verticalLayout)
        #elf.widget.show()
        self.setCentralWidget(self.widget)

        #work stuff

        #self.button.clicked.connect(self.another_function)


        #t = threading.Thread(target = self.threadingFunction)
        #t.start()
        #updating

        '''
        self.show()
        self.window = mainStuff(self)
        self.setCentralWidget(self.window)

    def another_function(self):
        print(2)

    def threadingFunction(self):
        cur_path = os.path.dirname(__file__)
        rel_path = '../logs/*'
        rel_path = '../../master-data/2020-12-17__Cs137_th2200__GDS-100__raw_data_log.bin'
        new_path = os.path.relpath(rel_path, cur_path)
        #list_of_files = glob.glob(new_path)
        #print(list_of_files)
        #last_file = max(list_of_files, key = os.path.getctime)
        #self.asic1.read_to_panda('S-proj-11-Cs137-HV2500-vthr2915_1.bin')
        #print(last_file)
        #rel_path = '..'
        #rel_path ='../logs/2020-12-16__17_34_02__GDS-100__raw_data_log.bin'
        last_file = os.path.relpath(rel_path, cur_path)

        self.asic1.read_to_panda(last_file)
        #self.asic1.read_to_panda('S-proj-11-Cs137-HV2500-vthr2915_1.bin')
        #self.asic1.read_to_panda('nov_30_cs137_na22_1ch.bin')

    def quit_everything(self):
        self.asic1.stop = True
        self.stop = True
        #Should wait for thread to close.
        self.close()

    def back_to_main(self):
        #print('thing')
        #self.multiprocess1.shutdown()
        #self.close()


        self.main = mainStuff(self)
        #self.main.show()
        self.setCentralWidget(self.main)


    def start_logging(self):
        self.stop = False
        #self.multiprocess1 = MyProcess(self.asic1)
        #self.multiprocess1.deamon = True
        #self.multiprocess1.start()

        t = threading.Thread(target = self.threadingFunction)

        t.start()
        self.timer.start(1000)

    def stop_logging(self):
        #should wait for thread to close
        self.stop = True
        #t.stop()
        self.asic1.stop = True

    def calibratedMode(self):
        self.w = CalibratedTabWidget(self)
        #self.window.close()
        #self.w.show()


    def calibrateMode(self):
        self.w = CalibrateTabWidget(self)
        #self.window.close()
        #self.w.show()
        #self.w.show()
    def closeEvent(self,event):
        self.stop_logging()
        self.timer.stop()
        #self.window.


class MyProcess(Process):
        def __init__(self,asic):
            super(MyProcess, self).__init__()
            self.asic = asic
            self.dostuff = DoStuff(self.asic)
            self.exit = Event()

        def run(self):
            #while not self.exit.is_set():
            #    pass
            print("MyProcess.run()")
            self.dostuff.start_thread()
        def shitdown(self):
            print('shutdown')
            self.exit.set()

class DoStuff(object):
    def __init__(self,asic):
        super(DoStuff, self).__init__()
        self.asic = asic

    def start_thread(self):
        self.my_thread_instance = MyThread(self.asic)
        self.my_thread_instance.start()
        #time.sleep(0.1)
class MyThread(threading.Thread):
    def __init__(self,asic):
        super(MyThread, self).__init__()
        self.asic = asic

    def run(self):
        self.asic.read_to_panda('nov27-na22-1ch-vthr2800.bin')

class mainStuff(QWidget):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent

        self.verticalLayout = QGridLayout()

        self.quit  = QPushButton('Quit')
        self.quit.clicked.connect(self.quit_all)
        self.quit.setObjectName('quit')
        logomap = QLabel()
        logo = QtGui.QPixmap('new_logo.png')
        logo = logo.scaledToWidth(100)


        logomap.setPixmap(logo)
        #self.verticalLayout.addWidget(logomap,0,1)
        self.verticalLayout.addWidget(self.quit,3,3)

        self.calibrateButton = QPushButton('Calibrate System')
        self.verticalLayout.addWidget(self.calibrateButton, 1,1)
        self.calibrateButton.setObjectName('calibrate')
        self.calibrateButton.clicked.connect(parent.calibrateMode)

        self.calibratedButton = QPushButton('Process Data')
        self.verticalLayout.addWidget(self.calibratedButton,1,2)
        self.calibratedButton.setObjectName('calibrate')

        self.calibratedButton.clicked.connect(parent.calibratedMode)
        self.setLayout(self.verticalLayout)

        self.lightOrDark = LightOrDark(self)
        self.verticalLayout.addWidget(self.lightOrDark,0,1)



    def quit_all(self):
        self.close()
        self.parent.quit_everything()

class LightOrDark(QWidget):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.penColor = 'w'

        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)

        self.lightPush = QPushButton('Light Mode')
        self.darkPush = QPushButton('Dark Mode')

        self.lightPush.clicked.connect(self.lightmode)
        self.darkPush.clicked.connect(self.darkmode)

        self.widget.layout.addWidget(self.lightPush,1,0)
        self.widget.layout.addWidget(self.darkPush,1,1)

        logomap = QLabel()
        logo = QtGui.QPixmap('new_logo.png')
        logo = logo.scaledToWidth(100)


        logomap.setPixmap(logo)
        self.widget.layout.addWidget(logomap,0,0)


    def lightmode(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        file = QFile(':/light.qss')
        self.penColor = 'k'
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

    def darkmode(self):
        print('dark')
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'w')
        self.penColor = 'w'
        file = QFile(':/dark.qss')
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())


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
        self.parent.penColor = 'w'



    def white_theme(self):
        self.parent.penColor = 'k'
        self.parent.graphWidget.setBackground('w')
        self.parent.updateMainHistogram()
        self.parent.graphWidget.getAxis('bottom').setTextPen('k')
        self.parent.graphWidget.getAxis('left').setTextPen('k')

    def black_theme(self):
        self.parent.penColor = 'w'
        self.parent.graphWidget.setBackground('k')
        self.parent.updateMainHistogram()
        self.parent.graphWidget.getAxis('bottom').setTextPen('w')
        self.parent.graphWidget.getAxis('left').setTextPen('w')


class CalibratedTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tabs.resize(300, 200)
        self.pause = False

        # Add tabs
        self.tabs.addTab(self.tab1, "ASIC 1")
        self.tabs.addTab(self.tab2, "ASIC 2")
        self.tabs.addTab(self.tab3, "ASIC 3")
        self.tabs.addTab(self.tab4, "ASIC 4")

        # Create tab
        self.tab1.layout = QGridLayout(self)

        self.tab1.setLayout(self.tab1.layout)
        #self.tab1.layout = QVBoxLayout(self)
        #self.penColor = 'w'

        self.lightordark = self.parent.window.lightOrDark
        self.tab1.layout.addWidget(self.lightordark,0,1)

        #self.black = QPushButton('Black')
        #self.tab1.layout.addWidget(self.black,8,8)


        self.graphWidget = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True, alpha=0.8)
        self.tab1.layout.addWidget(self.graphWidget,2,2)
        #self.graphWidget.setBackground('k')
        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]
        #label_style = {"color":'#EEE',"font_size":"20pt"}

        self.graphWidget.setLabel('bottom', 'ADC Value')
        self.graphWidget.setLabel( 'left' ,'Counts')
        #self.graphWidget.getAxis('bottom').setTextPen(self.penColor)
        #self.graphWidget.getAxis('left').setTextPen(self.penColor)
        # plot data: x, y values
        self.graphWidget.plot(hour, temperature)
        self.graphWidget.setMinimumWidth(600)

        self.pixLabel = QLabel(self)
        #self.pixLabel.setText('Pixel Map')
        #self.tab1.layout.addWidget(self.pixLabel,1,1)

        self.pixelMap = PixelMap(self)
        self.tab1.layout.addWidget(self.pixelMap,2,1)



        #self.calibration = Calibration(self.tab1)
        #self.tab1.layout.addWidget(self.calibration,3,3)

        self.startButton = QPushButton('Start Logging')
        self.startButton.clicked.connect(parent.start_logging)
        self.tab1.layout.addWidget(self.startButton,0,3)

        self.totalNumberOfEvents = QLabel('Event Counter = ' + str(parent.asic1.sum_events_all))
        self.tab1.layout.addWidget(self.totalNumberOfEvents,3,2)

        self.stopButton = QPushButton('Stop Logging')
        self.stopButton.clicked.connect(parent.stop_logging)
        self.tab1.layout.addWidget(self.stopButton,1,3)

        #self.somethingToUpdate = QLabel(parent.somethingstr,self)
        #self.tab1.layout.addWidget(self.somethingToUpdate,0,4)

        self.quit = QPushButton('Back',self)
        self.quit.clicked.connect(self._quit)
        self.tab1.layout.addWidget(self.quit,7,3)



        self.reloadButton = QPushButton('Reload Last Spectrum')
        self.tab1.layout.addWidget(self.reloadButton, 0,2)
        self.reloadButton.clicked.connect(self.reload)



        self.allSingleWidget = AllSingleWidget(self)
        self.tab1.layout.addWidget(self.allSingleWidget,1,1)

        self.options = Options(self)
        self.tab1.layout.addWidget(self.options,2,3)
        self.peak_channel = [[0 for j in range(12)] for i in range(12)]

        self.calculate_gains = QPushButton('Calculate Gain-Factors')
        self.tab1.layout.addWidget(self.calculate_gains,3,1)
        self.calculate_gains.clicked.connect(self.get_peak_gain_factors)

        #parent.timer1.timeout.connect(self.Update_Something)
        parent.timer.timeout.connect(self.updateMainHistogram)
        #parent.timer.start(100)
        #parent.timer1.start(1000)
        # Add tabs to widget
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)
        parent.setCentralWidget(self.tabs)

    def get_peak_gain_factors(self):
        gain_df = pd.DataFrame()

        for i in range(12):
            for j in range(12):
                peak = int(self.peak_channel[i][j])
                new_row = pd.Series([i,j,peak],index = ['x','y','gain'])
                gain_df = gain_df.append(new_row,ignore_index = True)
        gain_df.to_csv('gain_factors_na22_1.csv')


    def single_event_spectrum(self):
        self.single_event = SingleEventWidget(self)
        self.single_event.show()


    def Update_Something(self):
        self.parent.something +=1
        self.parent.somethingstr=str(self.parent.something)
        self.somethingToUpdate.setText(self.parent.somethingstr)

    def reload(self):
        print('Reload')
        list_of_files = glob.glob('spectras/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
    #    list_of_files_sub = glob.glob('subspectras/*') # * means all if need specific format then *.csv
    #    latest_file_sub = max(list_of_files_sub, key=os.path.getctime)
    #    channelSpectras = [[[] for i in range(12)] for j in range(12)]
        #print(df)
    #    i = 0
    #    j = 0
        #with open(latest_file_sub) as f:
        #    f_reader = csv.reader(f)
        #    for row in f_reader:
        #        i += 1
        #print(i)
    #    numbins = 6000

    #    loaded_arr = np.loadtxt(latest_file_sub)
    #    print(loaded_arr)

    #    load_original_arr = loaded_arr.reshape(
    #loaded_arr.shape[0], loaded_arr.shape[1] // numbins , numbins)
    #    print(load_original_arr)


        self.parent.asic1.total = df['Data'][:-1]
        self.parent.asic1.e = df['Bins']
        self.updateMainHistogram()


    def updateMainHistogram(self):

        #now = pg.ptime.time()
        #pg.disableAutoRange()
        #self.totalNumberOfEvents.setText('Event Counter = ' + str(self.parent.asic1.sum_events_all))
        #df_tot = self.parent.asic1.df_total
        #df_tot = df_tot.sort_index(axis = 0, level = None, ascending = True)

        #x = df_tot.index.values
        #y = df_tot.values
        if self.pause:
            return
        y = self.parent.asic1.total
        x = self.parent.asic1.e
        #print(self.lightordark.penColor)
        self.graphWidget.plot(x, y, stepMode=True, fillLevel=0,pen = self.lightordark.penColor, brush=(96, 125, 139,255), clear = True)
        #self.graphWidget.showGrid(x=True, y=True, alpha=0.8)

        self.totalNumberOfEvents.setText('Event Counter = ' + str(self.parent.asic1.sum_events_all))
        #self.parent.asic.
        for pix in self.pixelMap.pixels:
            pix.update_amount()
        #pg.autoRange()
        #print( "Plot time: %0.2f sec" % (pg.ptime.time()-now))
        #self.graphWidget.plot(x,y,clear = True)

    def skipEvents(self):
        self.parent.asic1.skip = True

    def _quit(self):
        self.parent.stop_logging()
        self.close()
        self.parent.back_to_main()
        self.parent.timer.stop()

    def show_random_event(self):
        #start_time = time.time()

        self.pause = True
        self.sub = SubWindowx(self)
        self.sub.show()
        #self.tab1.layout.addWidget(self.sub,3,2)
        #self.sub._start()
        self.t1 = threading.Thread(target = self.sub._start())
        self.t1.start()
        #print('hallo')
        #print("--- %s seconds ---" % (time.time() - start_time))


    def clear_all(self):
        print('clear')
        self.parent.asic1.total, e = np.histogram([], bins = self.parent.asic1.mybins)
        self.parent.asic1.sum_events_all = 0
        subtotal, sube = np.histogram([], bins = self.parent.asic1.mybins)
        self.parent.asic1.channelSpectras = [[ subtotal for i in range(12)] for j in range(12)]
        self.parent.asic1.channelSpectras_all = [[ subtotal for i in range(12)] for j in range(12)]

class Options(QWidget):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)

        self.edge = QPushButton('Edge Pixels Spectrum')
        self.widget.layout.addWidget(self.edge,3,0)

        self.corner = QPushButton('Corner Pixels Spectrum')
        self.widget.layout.addWidget(self.corner,4,0)

        self.corner.clicked.connect(self.corner_window)
        self.edge.clicked.connect(self.edge_window)

        self.random_event = QPushButton('Vizualize random event')
        self.random_event.clicked.connect(self.parent.show_random_event)
        self.widget.layout.addWidget(self.random_event,5,0)

        self.clearAllButton = QPushButton('Clear Spectrum')
        self.widget.layout.addWidget(self.clearAllButton,1,0)
        self.clearAllButton.clicked.connect(self.parent.clear_all)

        self.skipButton = QPushButton('Skip to end of file ')
        self.widget.layout.addWidget(self.skipButton,6,0)
        self.skipButton.clicked.connect(self.parent.skipEvents)

        self.single_event_button = QPushButton('Single Event Spectrum')
        self.widget.layout.addWidget(self.single_event_button, 2,0)
        self.single_event_button.clicked.connect(self.parent.single_event_spectrum)
        filler1 = QLabel(' ')
        self.widget.layout.addWidget(filler1,8,0)
        filler2 = QLabel(' ')
        self.widget.layout.addWidget(filler2,8,0)
        filler3 = QLabel(' ')
        self.widget.layout.addWidget(filler3,8,0)


    def corner_window(self):
        new_window = Corner_Edge_EventWidget(self, corner = True)
        new_window.show()

    def edge_window(self):
        new_window = Corner_Edge_EventWidget(self, corner = False)
        new_window.show()



class AllSingleWidget(QWidget):
    def __init__(self,parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.singleDisplay = True
        self.widget.layout = QGridLayout(self)

        self.all_events_butt = QPushButton('All Events')
        self.all_events_butt.clicked.connect(self.change_all)
        self.widget.layout.addWidget(self.all_events_butt,0,0)

        self.single_events_butt = QPushButton('Single Interaction Events')
        self.single_events_butt.setStyleSheet('background-color : #7f848a')

        self.single_events_butt.clicked.connect(self.change_single)
        self.widget.layout.addWidget(self.single_events_butt,0,1)
        self.display_all = False

    def change_single(self):
        if self.display_all:
            self.parent.pixelMap.all = False
            self.display_all = False
            self.single_events_butt.setStyleSheet('background-color : #7f848a')
            self.all_events_butt.setStyleSheet('background-color : #31363b')

    def change_all(self):
        if not self.display_all:
            self.parent.pixelMap.all = True
            self.display_all = True
            self.all_events_butt.setStyleSheet('background-color : #7f848a')
            self.single_events_butt.setStyleSheet('background-color : #31363b')


class BlackOrWhiteRandom(QWidget):
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
        self.parent.graphWidget.setBackground('w')
        #self.parent.updateMainHistogram()
        self.parent.graphWidget.getAxis('bottom').setTextPen('k')
        self.parent.graphWidget.getAxis('left').setTextPen('k')

    def black_theme(self):
        self.parent.penColor = 'w'
        self.parent.graphWidget.setBackground('k')
        #self.parent.updateMainHistogram()
        self.parent.graphWidget.getAxis('bottom').setTextPen('w')
        self.parent.graphWidget.getAxis('left').setTextPen('w')

class SubWindowx(QMainWindow):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self._cells = []

        for i in range(160):
            self._cells.append('Cell'+str(i))
        self.widget = QWidget()
        self.check = True
        self.layout = QGridLayout(self)
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True, alpha=0.8)
        self.penColor = self.parent.lightordark.penColor


        self.graphWidget.setLabel('bottom', 'Cell')
        self.graphWidget.setLabel( 'left' ,'Amplitude [ADC]')
        self.layout.addWidget(self.graphWidget,1,0)
        self.i = 0
        #hour = [1,2,3,4,5,6,7,8,9,10]
        #temperature = [30,32,34,32,33,31,29,32,35,45]

        # plot data: x, y values
        #self.graphWidget.plot(hour, temperature)

        self.blackOrWhiteRandom = BlackOrWhiteRandom(self)
        self.layout.addWidget(self.blackOrWhiteRandom,0,0)

        self.new_widget = QWidget()
        self.layout2 = QGridLayout()
        self.nextbutton = QPushButton('Next')

        self.backbutton = QPushButton('Previous')
        self.layout2.addWidget(self.nextbutton,1,1)
        self.backbutton.clicked.connect(self.previous)

        self.layout2.addWidget(self.backbutton,1,0)
        self.new_widget.setLayout(self.layout2)
        self.nextbutton.clicked.connect(self.next)

        self.pixelmap = PixelMapRandom(self)
        self.layout.addWidget(self.pixelmap,1,1)

        self.layout.addWidget(self.new_widget,2,0)
        #t = Threading.self.get_event()
        self.widget.setLayout(self.layout)
        #print('hei')
        self.setCentralWidget(self.widget)
        #self.t = threading.Thread(target = self._start())
        #self.t.start()
        #self._start()

    def next(self):
        for i in range(len(self.x)):
            self.pixelmap.pixelrandom[self.x[i]-1][self.y[i]-1].setStyleSheet('background-color : grey')
            self.pixelmap.pixelrandom[self.x[i]-1][self.y[i]-1].pix11.setText(' ')

        self.get_event()

    def previous(self):
        #print('hei')
        if self.i == 0:
            return
        else:
            print(self.i)
            self.i = self.i - 2
            print(self.i)
            self.get_event()

    def _start(self):
        self.df = self.parent.parent.asic1.current_dataframe
        self.get_event()


    def get_event(self):
        df = self.df

        print(df)
        length = len(df.index)
        #while self.check:
        print(length)
        print(self.i)
        if self.i >= length:
            #Get new dataframe
            self.df = self.parent.parent.asic1.current_dataframe
            print(self.df)
            df = self.df
            self.i = 0
        #if df.iloc[i]['Anode'] != 0:
        #    i += 1
        #    continue

        self.x = []
        self.y = []
        pen = pg.mkPen(color='r', width = 2)
        pen2 = pg.mkPen(color = self.penColor, width = 2)
        self.amplitude = []
        event = df.iloc[self.i]
        if not event['Anode']:
            #print('yes')
            #self.amplitude.append(event['Amplitude'])
            count = event[self._cells].values
            cells = np.arange(len(count))



            self.graphWidget.plot(cells, count, clear = True, pen = pen)
            print(cells)

            self.i +=1
            #DO SOMETHING
        else:

            self.x.append(int(event['x']))
            self.y.append(int(event['y']))

            self.amplitude.append(event['Amplitude'])

        #self.pixelmap.pixelrandom[self.x-1][self.y-1].setStyleSheet('background-color : yellow')
        #print(event)

            count = event[self._cells].values
        #print(len(y))
        #print('y')
        #print(y)
            cells = np.arange(len(count))

            self.graphWidget.plot(cells, count,clear = True, pen = pen2)

            self.i +=1
        #self.t.stop()
        #print(df.iloc[i]['Timestamp'])
        if not self.i >= length:

            while df.iloc[self.i]['Timestamp'] == event['Timestamp']:
                event = df.iloc[self.i]
                if event['Anode'] == 0:
                    count = event[self._cells].values
                    cells = np.arange(len(count))

                    self.self.graphWidget.plot(cells,count, pen = pen)
                    continues
                count = event[self._cells].values
                cells = np.arange(len(count))
                self.graphWidget.plot(cells,count, pen = pen2)
                self.x.append(int(event['x']))
                self.y.append(int(event['y']))
                self.amplitude.append(event['Amplitude'])
                self.i+=1
        print(self.x, self.y)
        for i in range(len(self.x)):
            self.pixelmap.pixelrandom[self.x[i]-1][self.y[i]-1].setStyleSheet('background-color : goldenrod')
            self.pixelmap.pixelrandom[self.x[i]-1][self.y[i]-1].pix11.setText(str(int(self.amplitude[i])))

    def closeEvent(self,event):
        self.parent.pause = False
    #    self.timer.stop()
    #def pixelMapRandom(self):

#class ClassifyingOptions(QWidget):





class PixelRandom(QWidget):
    def __init__(self,parent,i,j):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        #self.name = '('+str(i)+','+str(j)+')'
        self.widget = QWidget()
        self.i = i
        self.j = j
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)
        self.pix11 = QPushButton()
        self.pix11.setObjectName('pixel')
        #self.pix11.clicked.connect(self.PixelWindow)
        #self.pix11.setObjectName('pixel')
        self.widget.layout.addWidget(self.pix11, 0, 0)


class PixelMapRandom(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QGridLayout(self)
        self.widget.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.layout.setSpacing(0)


        self.pixelrandom = [[None for i in range(11)] for i in range(11)]
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,i+2,0)
        for i in range(1,12):
            lab = QLabel(str(i),self)
            self.widget.layout.addWidget(lab,0,i+2)

        for i in range(1,12):
            for j in range(1,12):
                self.pixelrandom[i-1][j-1] = PixelRandom(self,i,j)
                self.widget.layout.addWidget(self.pixelrandom[i-1][j-1], i+2, j+2)



class Calibration(QWidget):
    def __init__(self, parent):
        super(QWidget,self).__init__(parent)
        self.parent = parent
        self.widget = QWidget()
        self.widget.layout = QVBoxLayout(self)

        self.empty = QLabel(' ')
        self.widget.layout.addWidget(self.empty)

        self.calLab = QLabel('Calibration')
        self.widget.layout.addWidget(self.calLab)

        self.pedestalCal = QPushButton('Pedestal Correction')
        self.widget.layout.addWidget(self.pedestalCal)
        self.pedestalCal.setGeometry(QRect(520, 27, 171, 121))

        self.gainCal = QPushButton('Gain Correction')
        self.widget.layout.addWidget(self.gainCal)



class MyProcess2(Process):
        def __init__(self):
            super(MyProcess2, self).__init__()

            self.dostuff2 = DoStuff2()
            self.exit = Event()

        def run(self):
            #while not self.exit.is_set():
            #    pass
            print("MyProcess.run()")
            self.dostuff2.start_thread()
        def shitdown(self):
            print('shutdown')
            self.exit.set()

class DoStuff2(object):
    def __init__(self):
        super(DoStuff2, self).__init__()


    def start_thread(self):
        self.my_thread_instance = MyThread2()
        self.my_thread_instance.start()
        #time.sleep(0.1)
class MyThread2(threading.Thread):
    def __init__(self):
        super(MyThread2, self).__init__()


    def run(self):

        ex = App()



if __name__ == '__main__':

    app = QApplication(sys.argv)
    file = QFile(':/dark.qss')
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    #multiprocess2 = MyProcess2()
    #multiprocess2.deamon = True
    #multiprocess2.start()

    ex = App()

    sys.exit(app.exec_())
