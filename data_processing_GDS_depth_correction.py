import sys
sys.path.insert(1,'../')
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import time
import glob

from bitstring import BitArray
from sklearn.mixture import GaussianMixture
from calculate_amplitude import calculate_amplitude_average, calculate_amplitude_Kmeans, calculate_amplitude_GMM_improved, calculate_amplitude_trapezoidal, calculate_amplitude_GMM_improved
from struct import unpack
from datetime import datetime




class dataFrameASIC:
    def __init__(self,asic_id):
        self.asic_id = asic_id
        self.df_total = pd.Series()
        self.df_pedestals = pd.read_csv('pedestals_GDS_27_12_hv.csv',sep = ',')
        self.df_gains = pd.read_csv('finished_gain_1.csv', sep = ',')
        #print(self.df_gains)
        self.sum_events_all = 0
        self.stop = False
        self.skip = False
        self.waiting = ''
        #self.channelSpectras = [ pd.Series() for i in range(122)]

        self.start_time = 0
        self.current_dataframe = pd.DataFrame()



        datamin = 0
        datamax = 6000
        self.datamax = datamax
        self.numbins = 6000
        numbins = self.numbins
        self.mybins = np.linspace(datamin, datamax, numbins+1)
        print(self.mybins)
        self.total,self.e = np.histogram([],bins = self.mybins)
        print(len(self.total), len(self.e))
        subtotal, sube = np.histogram([], bins = self.mybins)
        self.channelSpectras = [[ subtotal for i in range(12)] for j in range(12)]
        self.channelSpectras_all = [[ subtotal for i in range(12)] for j in range(12)]
        self.single_total = []

    def find_occurance(self,dataFrame_added):
        #print('Finding Occurance')
        #df_chunk = dataFrame_added.reset_index(drop= True)
        #print(dataFrame_added)
        subtotal, sube = np.histogram(dataFrame_added['Amplitude'].values, bins = self.mybins)

        #self.df_total = self.df_total.add(df_chunk['Amplitude'].value_counts(),fill_value = 0)
        #print(self.channel11_total)
        #self.sum_events_all = self.df_total.sum()
        #print(self.df_total)
        #print('Occurance found')
        self.total += subtotal
        self.sum_events_all += sum(subtotal)
        #print("--- %s seconds ---this" % (time.time() - self.start_time))


    def group_events(self,df_chunk):
        #print('Grouping')
        df_total = pd.Series()
        #print(self.channel11_total)
        _columns =['Timestamp', 'Anode', 'x', 'y', 'Amplitude','Start_Cell']
        dataframe_added = pd.DataFrame(columns=_columns)
        series_ratio = [pd.Series([]) for _ in range(100)]
        #counter = 0
        #chunks = 1
        df_chunk = df_chunk[df_chunk['Anode']==1]
        #df_chunk = df_chunk.reset_index(drop=True)
        #print(df_chunk)
        df_chunk = df_chunk[(df_chunk['Amplitude']>=1)]
        df_chunk['consecutive'] = df_chunk.Timestamp.groupby((df_chunk.Timestamp != df_chunk.Timestamp.shift()).cumsum()).transform('size') * 1
        #df_chunk=df_chunk[df_chunk['consecutive']<7]
        df_chunk = df_chunk[(df_chunk['Amplitude']<=self.datamax)]
        single_df_chunk = df_chunk[df_chunk['consecutive']==1]

        single_events['C/A ratio'] = single_events.apply(lambda row: ratio(row),axis = 1 )

        single_events.to_hdf(store_in_file,key = 'df', mode = 'a', append = True, format = 'table')

    #    df_chunk = df_chunk.groupby(['Timestamp'], as_index = False).agg({'Anode':'first','x':'first', 'y':'first', 'Start_Cell':'first','consecutive':'first','Amplitude': 'sum'})
    #    df_chunk = df_chunk[(df_chunk['Amplitude']<=self.datamax)&(df_chunk['Amplitude']>=1)]

        #df_chunk = df_chunk[df_chunk['Amplitude']>=1]
        #print(df_chunk[df_chunk['Amplitude']==1900])


    #    self.find_occurance(df_chunk)

    def create_all_channel_single_events(self):
        chanSpec = self.channelSpectras

        subtotal, sube = np.histogram([], bins = self.mybins)

        for i in range(12):
            for j in range(12):
                subtotal += chanSpec[i][j]

        self.single_total = subtotal




    def read_to_panda(self,filename,subtract_pedestals = True):
        #print('hallo')
        #self.start_time = time.time()
        print('reading')
        dataframe_events = pd.DataFrame()
        remove_cathode = True
        chunksize =100
        bad_events = 0
        not_empty = True
        keys = []
        current_cell_pointer = 0
        columns = ['Timestamp', 'Delay', 'Anode', 'x', 'y','Start_Cell']

        for i in range(160):
            keys.append('Cell'+str(i))
        columns = np.concatenate((columns,keys), axis = None )
        columns = np.concatenate((columns,['Amplitude']),axis = None)
        columns = np.concatenate((columns,['Cathode']),axis = None)

        dataframe_events = pd.DataFrame(columns = columns)

        dataframe_events.to_hdf(store_in_file,key = 'df', mode = 'w', format = 'table')

        _cells = []
        for i in range(160):
            _cells.append('Cell'+str(i))
        if self.stop:
            return

        with open(filename, "rb") as binary_file:
            data = binary_file.read(338*chunksize)
            while not data:
                if self.stop:
                    self.save_data()
                    return
                self.waiting = 'Waiting for data'
                print('waiting')
                time.sleep(3)
                data = binary_file.read(338*chunksize)
                print(len(data))
            #print('----')

            data_len = int(len(data)/338)
            start = 0

            Time_delay = float(int.from_bytes(data[17+start:18+start], byteorder = 'big', signed = False))
            while not_empty:
                if self.stop:
                    print('Save Data')
                    self.save_data()
                    return
                start = 0
                for i in range(data_len):
                    new_row = {}
                         #> for not adding additional padding
                    d = unpack('>BHL4xHBxBBB160H',data[start:(start+338)])
                    #print(d)
                    values = np.array(d[8:])
                    #print('!!!!!!!!!!!!!!!')
                    #print(len(values))
                    info = np.array(d[2:8])
                    #print(info)
                    info[1] = 0
                    #print(values)
                    #print('hei')

                    #new_row.update({'Timestamp':float(int.from_bytes(data[8+start:12+start], byteorder = 'big', signed = False))})

                    #anode, x, y = self._dout(data[18+start:20+start])
                    x = info[3]
                    y = info[4]
                    if (x == 15) or ((info[3]==0) & (info[4] == 0)):
                        start+= 338
                        continue

                        #Set cell pointer to x-value
                    if info[2] == 0:
                        #print('hei')
                        current_cell_pointer = info[5]
                        #print(current_cell_pointer)
                        #if remove_cathode:
                        #start+= 338
                        #continue

                    info[5]=current_cell_pointer
                    #print(info)

                    #new_row.update({'Anode':anode, 'x': x, 'y':y})
                    #values = []
                    #keys = []

                    #for j in range(160):
                        #value.append(int.from_bytes(data[((j*2)+20+start):((j*2)+22+start)], byteorder='big', signed=False))
                    #    value = float(int.from_bytes(data[((j*2)+20+start):((j*2)+22+start)], byteorder='big', signed=False))

                    #    key = 'Cell'+str(j)
                    #    values.append(value)
                    #    keys.append(key)



                    #delay_time = 78#int(((79 + 160) - 1) % 160)
                      #set in data, delay = 80 so delay_time should be 79, but it seems the data is shifted
                    #start_cell =(((delay_time + 160) - current_cell_pointer) % 160)
                    #start_cell = 160-start_cell
                    start_cell = ((current_cell_pointer+68)+160)%160
                    #if start_cell == 160:
                    #    print(160)
                    #Get the cell in the the correct order
                    #a = values[:start_cell]
                    #b = values[start_cell:]

                    #values = np.concatenate([b,a], axis = None )
                    #print(values)

                #   values = np.array(values)

                    #start_cell = 0


                    #= np.append(values, 0)
                    if info[2] == 0:
                        cathode = self.subtract_pedestals_in_read_cathode(info[2],values,info[3],info[4], self.df_pedestals, self.df_gains, _cells, start_cell)
                        continue
                    #if values[-1] == 0:
                    #    bad_events += 1
                    else:
                        values = self.subtract_pedestals_in_read(info[2],values,info[3],info[4], self.df_pedestals, self.df_gains, _cells, start_cell)

                    all_val = np.concatenate((info, values),axis = None)
                    all_val = np.concatenate((all_val, cathode),axis = None)
                    #new_row.update({'Amplitude:'})

                    #for i in range(len(values)-1):

                    #    new_row.update({_cells[i]:values[i]})
                    #new_row.update(values)

                    #new_row.update({'Amplitude':values[-1]})
                    #new_row.update({'Amplitude_':values[-1]})
                    #new_row.update({'Amplitude_1':values[-2]})
                    #new_row.update({'Amplitude_2':values[-1]})
                    #new_row.update({'Amplitude_3':values[-1]})
                    #new_row.update({'Start_Cell':start_cell})
                    #new_row.update ({'std deviations':covar})


                    #new_row = pd.Series(new_row)
                    #print(new_row)
                    new_row = pd.Series(all_val, index = columns)
                    #print(new_row)

                    dataframe_events = dataframe_events.append(new_row, ignore_index=True)
                    start += 338
                #print(dataframe_events)
                #self.current_dataframe = dataframe_events
                #print(dataframe_events)

                #print('Dataframe Aquired')
                #if dataframe_events.empty:
                #    data = binary_file.read(338*chunksize)
                #    continue
                self.group_events(dataframe_events)

                #self.find_occurance(dataframe_events)
                dataframe_events = pd.DataFrame()
                if self.skip:

                    while data:
                        data = binary_file.read(338*10000)
                        print('skipped')
                        #print('End of file')
                        self.skip = False

                data = binary_file.read(338*chunksize)
                #print(data)
                while not data:
                    self.waiting = 'Waiting for data'
                    if self.stop:
                        return
                    print('waiting')
                    time.sleep(3)
                    data = binary_file.read(338*1000)
                    print(len(data))
                data_len = int(len(data)/338)
                #print(len(data))

    def save_data(self):
        print('saving_data')
        total = self.total
        total = np.append(total,[0])
        df = pd.DataFrame({'Bins':self.mybins,'Data':total})
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        print(dt_string)
        df.to_csv('spectras/'+dt_string+'-spectra.csv')

        #channelSpectras = np.array(self.channelSpectras)
        #arr_reshaped = channelSpectras.reshape(channelSpectras.shape[0], -1)
        #np.savetxt('subspectras/'+dt_string+'subspectra.csv', arr_reshaped)
        #print("shape of arr: ", channelSpectras.shape)
        #df_sub = pd.DataFrame()
        #for i in range(12):
        #    for j in range(12):
        #        df_sub.append()

        #with open('subspectras/'+dt_string+'-subspectra.csv', 'w+') as f:
        #    writer = csv.writer(f)
            #for i in range(12):
            #    writer.writerows(self.channelSpectras[i])
        #print(self.channelSpectras)

    def subtract_pedestals_in_read(self,anode,input,input_x,input_y, df_pedestals, df_gains,_cells, start_cell):
        #print(input_x)
        #print(input_y)
        rand = np.random.uniform(low = -0.5, high = 0.5, size = (160,))
        #print(rand)

        input = input + rand
        ind = df_pedestals.loc[(df_pedestals['x'] == input_x) & (df_pedestals['y'] == input_y), _cells]
        #print(input_x)
        #print(input_y)
        #print(df_gains)''
        #gain = df_gains.loc[(df_gains['x']==input_x)& (df_gains['y']==input_y)]['gain_finished'].values[0]

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
        #plt.grid()
    #    plt.xlabel('Cell')
        #plt.ylabel('Amplitude[ADC]')
        #plt.title('A')

        #plt.plot(np.arange(len(input)),input, label = 'Event data')
        #plt.legend()

        input = input-ind
        #input[0] = 0
        #amplitude = np.mean(input[120:])
        #print(input)
        #plt.figure()
        #plt.plot(np.arange(len(input)),input, label = 'Event data')
        #plt.grid()
        #plt.xlabel('Cell')
        #plt.ylabel('Amplitude[ADC]')
        #plt.legend()
        #plt.title('B')
        #plt.show()
        #plt.show()

        #for index, row in input.iterrows():
        #    row['Cell0':'Cell159'].plot()
        #amplitude = find_amplitude(input)

        #amplitude = calculate_amplitude_GMM_improved(input, True)
        #amplitude_1 = calculate_amplitude_trapezoidal(input, 70, 14)
        #amplitude_3 = calculate_amplitude_trapezoidal(input, 70, 14)
        amplitude = calculate_amplitude_GMM_improved(anode,input)*gain
        #print(amplitude)
        #amplitude = amplitude#*gain

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

        return amplitude

    def subtract_pedestals_in_read_cathode(self,anode,input,input_x,input_y, df_pedestals, df_gains,_cells, start_cell):
        #print(input_x)
        #print(input_y)
        rand = np.random.uniform(low = -0.5, high = 0.5, size = (160,))
        input = input + rand
        ind = df_pedestals.loc[(df_pedestals['x'] == input_x) & (df_pedestals['y'] == input_y), _cells]
        #print(input_x)
        #print(input_y)
        #print(df_gains)
        #gain = df_gains.loc[(df_gains['x']==input_x)& (df_gains['y']==input_y)]['gain'].values[0]

        #print(ind)
        #ind['Cell0']= 8200
        #assert not ind.empty, 'x and y coordinates out of bounds, no pedestals found '
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
        amplitude = calculate_amplitude_GMM_improved(anode,input)

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


        input = np.append(input, amplitude)
        #input = np.append(input, amplitude_1)
        #input = np.append(input, amplitude_2)
        #input = np.append(input, amplitude_3)

        return input#, covar



    def _dout(self,dout):
        _dout_bin = BitArray(dout).bin
        anode = int(_dout_bin[4:5])
        #print(_dout_bin[0:5])
        if anode:
            x = int(_dout_bin[7:11],2)
            y = int(_dout_bin[-4:],2)

        else:
            x = int(_dout_bin[-8:],2)
            y = None
        return anode, x,y

'''
data = dataFrameASIC(1)
cur_path = os.path.dirname(__file__)
#rel_path = '../logs/*'
rel_path = '../../master-data/2020-12-17__Cs137_th2200__GDS-100__raw_data_log.bin'
new_path = os.path.relpath(rel_path, cur_path)
#list_of_files = glob.glob(new_path)
#print(list_of_files)
#last_file = max(list_of_files, key = os.path.getctime)
data.read_to_panda(new_path)
'''
