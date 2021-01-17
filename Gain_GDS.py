import sys
sys.path.insert(1,'../')

import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import time
from bitstring import BitArray
from struct import unpack
import os
from calculate_amplitude import calculate_amplitude_average, calculate_amplitude_Kmeans, calculate_amplitude_GMM_improved, calculate_amplitude_trapezoidal, calculate_amplitude_GMM_improved


class Gains:
    def __init__(self, asic_id):
        self.asic_id = asic_id
        self.total_gain = pd.DataFrame()
        self.gain_values = [[[] for i in range(12)] for j in range(12)]
        self.finished = False
        self.len = 0
        self.number_of_events = 0

        #self.df_gains = pd.read_csv('gain_factors.csv', sep = ',')



    def read_to_panda(self):
        cur_path = os.path.dirname(__file__)
        rel_path = '../../master-data/gain_cal_100_la.bin'
        new_path = os.path.relpath(rel_path, cur_path)
        df_ped  = pd.read_csv('pedestals_GDS_27_12_hv.csv')
        gain_values = [[[] for i in range(12)] for j in range(12)]
        #df_gains = self.df_gains

        dataframe_events = pd.DataFrame()
        not_empty = True
        end_counter = 0


        keys = []
        counter = 0
        for i in range(160):
            keys.append('Cell'+str(i))

    #    columns = ['Packettype','packetcount', 'timestamp', 'hold delay', 'Anode', 'x', 'y', 'cell pointer']

        with open(new_path, "rb") as bin_file:
            data = bin_file.read()
            #print(data)
            self.len = len(data)/338
            print(len(data))

            start = 0
            #while not_empty:
            while start < (len(data)):
                new_row = {}
                #print(start)
                #print(3380000 < 388*10000)
            #    print(len(data[start:(start+338)]))
                d = unpack('>BHL4xHBxBBB160H',data[start:(start+338)])
                #print(d)
                x = d[5]
                y = d[6]
                if x == 15:
                    start += 338
                    continue
                elif d[4] == 0:
                    start += 338
                    current_cell_pointer = d[7]
                    #print(d[7])
                    continue
                inp = d[8:]
                #if (x == 4 and y == 1):
                #    print(1)
                start_cell = ((current_cell_pointer-92)+160)%160

                #test another way of calculating amplitude
                #print(inp)
                mean = np.mean(inp[90:])
                #print(mean)
                if mean > 8600:
                    #print('si')
                    #gain = df_gains.loc[(df_gains['x']==x)& (df_gains['y']==y)]['gain'].values[0]

                    amplitude = self.subtract_pedestals_in_read(d[4],inp,x,y,df_ped,keys,start_cell)
                    #mean = (mean1-mean2)#*gain
                    gain_values[x][y].append(amplitude)
                    if (x == 2) and (y==9):
                        end_counter += 1
                        if end_counter == 9000:
                            break
                    #print(np.mean(inp[90:]))
                    #print(mean)
                    #print(x,y)

                    #plt.figure()
                    #plt.plot(np.arange(len(inp)),inp)
                    #plt.show()
                start += 338
                #print(start)
                #data = bin_file.read(338*1000000)
                #counter+=1
                #print(counter)
                #start = 0
                #if not data:
                #    not_empty = False
                self.number_of_events += 1
                #print(self.gain_values)
                #print(self.number_of_events)
        #print(self.gain_values)
        self.gain_values = gain_values
        print(gain_values)
        self.finished = True
        for i in range(1,12):
            for j in range(1,12):
                if np.mean(gain_values[i][j])<1:
                    factor = 0
                else:
                    factor = 545/np.mean(gain_values[i][j])
                new_row = pd.Series([i,j,factor], index = ['x','y','gain'])
                #print(new_row)
                dataframe_events = dataframe_events.append(new_row, ignore_index = True)

                #print(dataframe_events)
        self.total_gain = dataframe_events
        #self.total_mean.to_csv('pedestal_test_GDS_30_11.csv', header = True, index = True)
        dataframe_events.to_csv('gain_factors_100.csv', header = True, index = True)
        print(self.finished)

    def subtract_pedestals_in_read(self,anode,input,input_x,input_y, df_pedestals, _cells, start_cell):
        #print(input_x)
        #print(input_y)
        #rand = np.random.rand(160)
        #input = input + rand
        ind = df_pedestals.loc[(df_pedestals['x'] == input_x) & (df_pedestals['y'] == input_y), _cells]
        #print(ind)
        #ind['Cell0']= 8200
        assert not ind.empty, 'x and y coordinates out of bounds, no pedestals found '
        a = ind.values[0][:start_cell]
        b = ind.values[0][start_cell:]
        #ind = ind.values[0]
        #print(start_cell)
        ind = np.concatenate([b,a], axis = None )
        #print(ind)
        #print(input)
        #print(ind)
        #print(input)
        #plt.figure()
        #plt.plot(np.arange(len(ind)), ind)
        #plt.figure()

        #plt.plot(np.arange(len(input)),input)

        input = input-ind
        #input[0] = 0
        #input[1] = 0
        #amplitude = np.mean(input[120:])
        #print(input)
        #plt.figure()
        #plt.plot(np.arange(len(input)),input)
        #plt.show()
        #plt.show()

        #for index, row in input.iterrows():
        #    row['Cell0':'Cell159'].plot()
        #amplitude = find_amplitude(input)

        #amplitude = calculate_amplitude_GMM_improved(input, True)
        #amplitude_1 = calculate_amplitude_trapezoidal(input, 70, 14)
        #amplitude_3 = calculate_amplitude_trapezoidal(input, 70, 14)
        amplitude = calculate_amplitude_average(input)

        #amplitude = calculate_amplitude_GMM_improved(input,True)
        #amplitude_ = calculate_amplitude_GMM_improved(input,False)
        #amplitude = calculate_amplitude_trapezoidal(input, 60, 14)
        #amplitude_1 = calculate_amplitude_trapezoidal(input,65,14)
        #amplitude = calculate_amplitude_trapezoidal(input,75,14)
        #amplitude_3 = calculate_amplitude_trapezoidal(input,80,14)

        #amplitude_1 = calculate_amplitude_trapezoidal(input,70,6)
        #amplitude_2 = calculate_amplitude_trapezoidal(input,70,14)
        #amplitude_3 = calculate_amplitude_trapezoidal(input,70,10)
        #amplitude_1 = calculate_amplitude_GMM_improved(input)
        #find_amplitude_KMeans calculate_amplitude_Kmeans
        #print(amplitude)


        #input = np.append(input, amplitude)
        #input = np.append(input, amplitude_1)
        #input = np.append(input, amplitude_2)
        #input = np.append(input, amplitude_3)

        return amplitude#, covar

#gain = Gains(1)

#gain.read_to_panda()
