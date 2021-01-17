import sys
sys.path.insert(1,'../')

import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import time
import os
from bitstring import BitArray
from sklearn.mixture import GaussianMixture
from calculate_amplitude import calculate_amplitude_average, calculate_amplitude_Kmeans, calculate_amplitude_GMM_improved, calculate_amplitude_trapezoidal, calculate_amplitude_GMM_improved
from struct import unpack


class Pedestals:
    def __init__(self,asic_id):
        self.asic_id = asic_id
        self.total_mean = pd.DataFrame()
        self.total_std = pd.DataFrame()
        self.stop = False
        self.number_of_events = 0
        self.finished = False
        self.current_dataframe = pd.DataFrame()
        self.noise_values = [[[] for i in range(12)] for j in range(12)]
        self.noise_inp = [[0 for i in range(12)] for j in range(12)]
        self.std_each_cell = pd.DataFrame()
        self.chunksize = 0

    #def pedestal_gain(self):


    def read_to_panda(self):
        #pedestal_file = 'pedestals.bin'

        cur_path = os.path.dirname(__file__)
        rel_path = '../../master-data/pedestal_whv.bin'
        new_path = os.path.relpath(rel_path, cur_path)
        pedestal_file = new_path#'pedestals1.bin'
        dataframe_events = pd.DataFrame()
        chunksize = 10000
        self.chunksize = chunksize
        not_empty = True
        keys = []
        counter= 0
        counter1 = 0
        GDS100 = False

        #self.finished = False
        columns = ['Anode', 'x', 'y']

        for i in range(160):
            keys.append('Cell'+str(i))
        columns = np.concatenate((columns,keys), axis = None )

        with open(pedestal_file, 'rb') as binary_file:
            data = binary_file.read(338*chunksize)

            while counter < 1:
                start = 0
                if self.stop:
                    return
                #_delay = float(int.from_bytes(data[11+start:13+start], byteorder = 'big', signed = False))
                for i in range(chunksize):

                    #print('hei')
                    #print('0')
                    new_row = {}
                    #timestamp = int.from_bytes(data[3+start:7+start],byteorder='big', signed=False)
                    d = unpack('>7x4x2xBxBBx160H',data[start:(start+338)])
                    #print(d)
                    values = np.array(d)
                    new_row = pd.Series(values, index = columns)


                    #new_row.update({'timestamp':timestamp})
                    #anode, x, y = self._dout(data[3+start:7+start])
                    #anode = int.from_bytes(data[13+start:14+start],byteorder='big', signed=False)
                    #x = int.from_bytes(data[14+start:15+start],byteorder='big', signed=False)
                    #y = int.from_bytes(data[15+start:16+start],byteorder='big', signed=False)

                    #new_row.update({'Anode':anode, 'x': x, 'y':y})
                    #if anode == 0:
                #        current_cell_pointer = x
                #    if anode ==0:
                #        new_row.update({'Anode':anode, 'x': 0, 'y':0})
                #    else:
                #        new_row.update({'Anode':anode, 'x': x, 'y':y})
                #    values = []

                    x = d[1]
                    y = d[2]

                    #if x == 4 and y == 1:
                    #    counter1 += 1

                    #print(d)

                    #d = unpack('>18x160H',data[start:(start+338)])
                    #print(d)
                    #print(data[11+start:13+start])

                    #values = np.array(d)

                    #start_cell = ((current_cell_pointer-2)%160)
                    #a = values[:start_cell]
                    #b = values[start_cell:]
                    #values = np.concatenate((a,b), axis = None)

                    #for i in range(len(values)):
                    #    new_row.update({keys[i]:values[i]})
                    #new_row = pd.Series(new_row)

                    if (new_row.y == 15) or (new_row.x == 15):
                    #    print('ye')
                        start +=338
                        continue
                    if (new_row.y == 0) or (new_row.x == 0):
                    #    print('ye')
                        start +=338
                        continue

                    if new_row.Anode == 0:
                        print(x,y)
                        #current_cell_pointer = d[7]
                        x = 0
                        y = 0

                    #else:
                        #noise = self.find_input_eq_noise(new_row[keys])
                    #    self.noise_values[x][y].append(self.find_input_eq_noise(new_row[keys]))


                    #if (y not in (15,255)) and (x not in (15,255)):
                        #print(x)
                        #print(y)
                    noise = self.find_input_eq_noise(new_row[keys])
                    self.noise_values[x][y].append(noise)
                    #print(self.noise_values)
                    #print(start)

                    #print(self.noise_values)
                    #print(x)
                    #print(y)
                    #self.noise_values[x][y].append(noise)

                    dataframe_events = dataframe_events.append(new_row, ignore_index = True)
                    self.number_of_events += 1
                    start += 338

                #print(dataframe_events)
                data = binary_file.read(338*chunksize)
                #dataframe_events.to_csv('test_read_15.csv')
                counter += 1
                #self.number_of_events = chunksize*counter
                #print(self.number_of_events)
                #print(dataframe_events)
                print(1)
                self.calculate_mean(dataframe_events,keys)
                print(2)
                self.get_std_dataframe(dataframe_events,keys)
                #self.calculate_std(dataframe_events, keys)
                print(3)
                dataframe_events = pd.DataFrame()
            print(4)
            self.calculate_inp_noise()
            self.total_mean.to_csv('pedestal_GDS_3_1_wo_hv.csv', header = True, index = True)
            self.finished = True
            print('counter!!!:', counter1)


    def get_std_dataframe(self,df,keys):
        #print(df)
        #std_each_cell = [[[] for i in range(12)] for i in range(12)]

        #df_1 = df.groupby(['x','y'], as_index = False).agg({'Anode':'first','Cell0':'std', 'Cell1':'std','Cell2':'std','Cell3':'std','Cell4':'std','Cell5':'std','Cell6':'std','Cell7':'std','Cell8':'std','Cell9':'std','Cell10':'std','Cell11':'std','Cell12':'std','Cell13':'std','Cell14':'std','Cell15':'std','Cell16':'std','Cell17':'std','Cell18':'std','Cell19':'std','Cell20':'std','Cell21':'std','Cell1':'std''Cell1':'std''Cell1':'std''Cell1':'std'})

        #keys_xy = keys + ['Anode','x','y']
        #df_1 = df[keys_xy]

        #print(df_1)
        df_1 = df.groupby(['Anode','x', 'y']).std()
        print('hello')
        print(df_1)
        #for x in range(1,12):
        #    for y in range(1,12):
        #        for i in range(160):
        #            sub_df = df[(df['x']==x) & (df['y'] == y)]
                    #print(sub_df['Cell'+str(i)].values)
        #            std = np.std(sub_df['Cell'+str(i)].values)
                    #print(std)
        #            std_each_cell[x][y].append(std)
        print(df_1.mean(axis = 1))

        df_1['Average std'] = df_1.mean(axis = 1)
        print(df_1)

        self.std_each_cell = df_1


    def calculate_mean(self,gm_chunk, _cells):
        curr_mean = gm_chunk.groupby(by =['Anode','x','y'], as_index = False )[_cells].mean()
        #print(curr_mean)
        gm_chunk_mean = pd.concat([curr_mean, self.total_mean], axis = 0 , sort = True)

        self.total_mean = gm_chunk_mean.groupby(by =['Anode','x','y'], as_index = False )[_cells].mean()


    #def calculate_std(self,gm_chunk,_cells):
        #curr_std = gm_chunk.groupby(by = ['Anode', 'x', 'y'], as_index = True)[_cells].std(ddof = 0)
        #print(curr_std)
        #gm_chunk_std = pd.concat([curr_std, self.total_std], axis = 0 , sort = True)
        #print(gm_chunk_std)
        #self.total_std = gm_chunk_std.groupby(by =['Anode','x','y'], as_index = True)[_cells].mean()
        #print(self.total_std)

    def calculate_inp_noise(self):
        noise_values = self.noise_values
        #print(len(self.noise_inp))
        #print(len(self.noise_inp[0]))
        #start_time = time.time()
        #noise_std_t = [[np.std(noise_values[i][j]) for j in range (1,12)] for i in range(1,12)]


        #print(noise_std_t)
        #print("--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        for x in range(1,12):
            for y in range(1,12):
                #print(i)
                #print(j)
                self.noise_inp[x][y] = np.std(noise_values[x][y])
        #print(self.noise_inp)
        #print("--- %s seconds ---" % (time.time() - start_time))


    def rearrange_values(self,values, start_cell):
        #print(values)
        a = values[:start_cell]
        b = values[start_cell:]
        return np.concatenate((b,a), axis = 0)

    def _dout(self,dout):
        _dout_bin = BitArray(dout).bin
        anode = int(_dout_bin[4:5])
        if anode:
            x = int(_dout_bin[7:11],2)
            y = int(_dout_bin[-4:],2)

        else:
            x = int(_dout_bin[-8:],2)
            y = None
        return anode, x,y

    def find_input_eq_noise(self,input):
        #ind = df_pedestals.loc[(df_pedestals['x'] == input_x) & (df_pedestals['y'] == input_y), _cells]
        #assert not ind.empty, 'x and y coordinates out of bounds, no pedestals found '
        #a = ind.values[0][:start_cell]
        #b = ind.values[0][start_cell:]

        #ind = np.concatenate([b,a], axis = None )
        #print(ind)
        #print(input)
        #input = input-ind
        #for index, row in input.iterrows():
        #    row['Cell0':'Cell159'].plot()
        #amplitude = find_amplitude(input)

        #amplitude = calculate_amplitude_GMM_improved(input, True)
        #amplitude_1 = calculate_amplitude_trapezoidal(input, 70, 14)
        #amplitude_3 = calculate_amplitude_trapezoidal(input, 70, 14)
        #amplitude = calculate_amplitude_GMM_improved(anode,input)

        #amplitude = calculate_amplitude_GMM_improved(input,True)
        #amplitude_ = calculate_amplitude_GMM_improved(input,False)
        #amplitude = calculate_amplitude_trapezoidal(input, 60, 14)
        #amplitude_1 = calculate_amplitude_trapezoidal(input,65,14)
        #start_time = time.time()
        amplitude = calculate_amplitude_trapezoidal(input,65,14,correct =False)
        #print("--- %s seconds ---" % (time.time() - start_time))

        #print(amplitude)
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


#ped = Pedestals(1)
#ped.read_to_panda()
