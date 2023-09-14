import threading
import time
from queue import Queue
from PyQt5.QtWidgets import *
import obspy as ob
import os
import numpy as np
import math
import re
from scipy import fft, signal
import pandas as pd

pd.options.mode.chained_assignment = None


def start_pnet_pc_read_thread(back_to_front_queue: Queue,
                              front_to_back_queue: Queue):
    BackendHandler(back_to_front_queue, front_to_back_queue)


class BackendHandler:
    def __init__(self, back_to_front_queue: Queue, front_to_back_queue: Queue):
        self.back_to_front_queue = back_to_front_queue
        self.front_to_back_queue = front_to_back_queue

        self.extension = ['.txt', '.CLS']

        # self._read_thread = threading.Thread(target=self._read_loop)
        # self._read_thread.start()

        self._write_thread = threading.Thread(target=self._write_loop)
        self._write_thread.start()

    # def _read_loop(self):
    # while True:
    # time.sleep(2)
    # self.value = self.value + 1
    # self.back_to_front_queue.put(self.value)
    def _write_loop(self):
        while True:
            signal = self.front_to_back_queue.get()

            if signal['Action'] == 'read_file':
                print(signal)
                if signal['FileExtension'] == '.v1':
                    read_traces = self.read_file_v1(signal['FilePath'])
                    signal_out = {'Action': 'Loaded traces v1',
                                  'Data': read_traces[:3],
                                  'Stations': read_traces[3],
                                  'Periods': read_traces[4],
                                  'Channels': read_traces[5],
                                  'Record': signal['FileName']}
                    self.back_to_front_queue.put(signal_out)
                else:
                    read_traces = ob.read(signal['FilePath'])

            elif signal['Action'] == 'read_batch':
                print(signal)

                files_all = []
                files_all = self.read_paths(signal['DirectoryPath'], files_all)
                self.sort_files(files_all)

                len_files_v1 = len(self.df_v1_sorted['File path v1'])
                network = np.array(np.zeros(len_files_v1), dtype='str')
                network[network == '0.0'] = '/'
                channel_v1 = np.array(np.zeros(len_files_v1), dtype='str')
                channel_v1[channel_v1 == '0.0'] = 'BHE, BHN, BHZ'

                hstack_files_v1_obs = np.hstack((self.df_all_obs['Trace_name'],
                                                 self.df_v1_sorted[
                                                     'File name v1']))
                hstack_network_v1_obs = np.hstack(
                    (self.df_all_obs['Obs_network'], network))
                hstack_station_v1_obs = np.hstack(
                    (self.df_all_obs['Obs_station'], network))
                hstack_channel_v1_obs = np.hstack(
                    (self.df_all_obs['Obs_channel'], channel_v1))

                obs_data = np.vstack((hstack_files_v1_obs,
                                      hstack_network_v1_obs))
                obs_data = np.vstack((obs_data, hstack_station_v1_obs))
                obs_data = np.vstack((obs_data, hstack_channel_v1_obs))
                obs_data = obs_data.T
                signal_out = {'Action': 'Loaded traces', 'Data': obs_data}
                self.back_to_front_queue.put(signal_out)

            elif signal['Action'] == 'OpenRecord':
                print(signal)
                if signal['Extension'] == '.v1':
                    read_traces = self.read_file_v1(signal['RecordPath'])

                    signal_out = {'Action': 'Draw record v1',
                                  'Data': read_traces[:3],
                                  'Stations': read_traces[3],
                                  'Periods': read_traces[4],
                                  'Channels': read_traces[5]}

                    self.back_to_front_queue.put(signal_out)

                # elif signal['Extension'] == '.txt':
                #     signal_out = {'Action': 'Draw record txt',
                #                   'Data': read_traces,
                #                   'Record': signal['FileName']}
                #     self.back_to_front_queue.put(signal_out)

                else:
                    trace_ind = int(
                        np.mean(np.array(self.df_all_obs['Trace_ID'][
                                             self.df_all_obs[
                                                 'Trace_name'] ==
                                             signal['RecordPath']],
                                         dtype=int)))
                    df_pom = self.df_sorted_obs[self.df_sorted_obs['Trace_ID']
                                                == trace_ind]
                    # print(df_pom['Obs_channel'])
                    read_traces = self.read_file_obspy(df_pom)
                    signal_out = {'Action': 'Draw record obspy',
                                  'Data': read_traces[0],
                                  'Periods': read_traces[1],
                                  'Channels': read_traces[2]}

                    self.back_to_front_queue.put(signal_out)

            elif signal['Action'] == 'CalculateFAS':
                self.calculate_FAS(signal['DataX'], signal['DataY'])
            elif signal['Action'] == 'CalculateSpectrogram':
                self.calculate_spectrogram(signal['DataX'], signal['DataY'])

    def read_paths(self, path, files_all):
        in_path_first = os.listdir(path)
        for files in in_path_first:
            files_path = os.path.join(path, files)
            try:
                self.read_paths(files_path, files_all)
            except NotADirectoryError:
                files_all += [files_path]
        return files_all

    def sort_files(self, files):
        self.files_txt = []
        files_v1 = []
        self.files_error_batch = []
        files_obs_batch = []
        files_obs_network = []
        files_obs_station = []
        files_obs_channel = []
        files_obs_start_time = []

        for file in files:
            if file.lower().endswith('.txt'):
                self.files_txt += [file]
            elif file.lower().endswith('.v1'):
                files_v1 += [file]
            elif file.lower().endswith('.zip'):
                continue
            else:
                try:
                    if file.lower().endswith('.mseed'):
                        read_traces = ob.read(file, format='MSEED')
                    else:
                        read_traces = ob.read(file)
                    files_obs_batch += [file]
                    files_obs_network += [read_traces[0].stats.network]
                    files_obs_station += [read_traces[0].stats.station]
                    files_obs_channel += [read_traces[0].stats.channel]
                    files_obs_start_time += [read_traces[0].stats.starttime]
                except Exception:
                    self.files_error_batch += [file]

        self.sort_obs_files(files_obs_station, files_obs_batch,
                            files_obs_channel, files_obs_start_time,
                            files_obs_network)

        self.sort_v1_files(files_v1)

    def sort_v1_files(self, files_v1):
        self.df_v1_sorted = pd.DataFrame()
        self.df_v1_sorted['File path v1'] = files_v1
        file_name = []
        for i in range(len(files_v1)):
            file_name += [os.path.split(files_v1[i])[-1]]
        self.df_v1_sorted['File name v1'] = file_name

    def sort_obs_files(self, files_obs_station, files_obs_batch,
                       files_obs_channel, files_obs_start_time,
                       files_obs_network):
        df_to_sort = pd.DataFrame()
        df_to_sort['Obs_station'] = files_obs_station
        df_to_sort['File_path'] = files_obs_batch
        df_to_sort['Obs_channel'] = files_obs_channel
        df_to_sort['Obs_start_time'] = files_obs_start_time
        df_to_sort['Obs_network'] = files_obs_network

        df_to_sort = df_to_sort.astype(
            {"Obs_station": str, "File_path": str, "Obs_channel": str,
             "Obs_start_time": str})
        df_to_sort['Trace_ID'] = int()
        stations = list(set(files_obs_station))
        count_trace = 0
        all_rows = []
        for i in range(len(stations)):
            df_pom = df_to_sort[df_to_sort['Obs_station'] == stations[i]].copy()
            start_times = df_pom['Obs_start_time']
            start_times = list(set(list((start_times).str[:22])))
            row_pom = [].copy()
            for j in range(len(start_times)):
                row_index = df_pom[df_pom['Obs_start_time'].str[:22] ==
                                   start_times[j]].index
                df_to_sort['Trace_ID'].iloc[row_index] = count_trace
                name_pom = \
                    os.path.split(df_to_sort['File_path'].iloc[row_index[0]])[
                        -1]
                remove_bhe = re.compile(re.escape('BHE'), re.IGNORECASE)
                remove_bhn = re.compile(re.escape('BHN'), re.IGNORECASE)
                remove_bhz = re.compile(re.escape('BHZ'), re.IGNORECASE)

                name_pom = remove_bhe.sub('', name_pom)
                name_pom = remove_bhn.sub('', name_pom)
                name_pom = remove_bhz.sub('', name_pom)
                name_pom = name_pom.replace('..', '.').replace('..', '.')
                if j == 0:
                    row_pom += [name_pom]
                    # str_path = ', '
                    # str_path = str_path.join(
                    #    np.array(df_to_sort['File_path'].iloc[row_index]))
                    # row_pom += [str_path]
                    row_pom += [stations[i]]
                    str_channel = ', '
                    str_channel = str_channel.join(
                        np.array(df_to_sort['Obs_channel'].iloc[row_index]))
                    row_pom += [str_channel]
                    row_pom += [df_to_sort['Obs_network'].iloc[row_index[0]]]
                    row_pom += [count_trace]
                count_trace += 1

            if i == 0:
                all_rows = row_pom.copy()
            else:
                all_rows = np.vstack((all_rows, row_pom))

        self.df_all_obs = pd.DataFrame(all_rows,
                                       columns=['Trace_name', 'Obs_station',
                                                'Obs_channel', 'Obs_network',
                                                'Trace_ID'])
        df_to_sort = df_to_sort.astype({'Trace_ID': int})
        self.df_sorted_obs = df_to_sort

    def read_file_v1(self, path_pom):
        path = self.df_v1_sorted['File path v1'][
            self.df_v1_sorted['File name v1'] == path_pom].item()
        file = open(path, 'r')
        file_read = file.read()
        file = open(path, 'r')
        file_read_lines = file.readlines()  # [:30]
        file.close()

        periods_all = []
        str_re_findall = "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"

        number_of_points_ch1 = int(
            re.findall(str_re_findall, file_read_lines[27])[0])
        periods_all += [re.findall(str_re_findall, file_read_lines[27])[1]]

        len_columns = len(re.findall(str_re_findall, file_read_lines[28]))
        len_rows_ch1 = number_of_points_ch1 / len_columns

        big_point_ch1 = 0
        for i in range(28):
            big_point_ch1 += len(file_read_lines[i])
        end_point_ch1 = int(big_point_ch1 + len_rows_ch1 * 73)

        str_data_ch1 = file_read[big_point_ch1: end_point_ch1]
        str_data_ch1 = re.findall(str_re_findall, str_data_ch1)
        array_data_ch1 = np.array(str_data_ch1)

        number_of_points_ch2 = int(re.findall(str_re_findall,
                                              file_read_lines[56 + math.ceil(
                                                  len_rows_ch1)])[0])
        periods_all += [re.findall(str_re_findall, file_read_lines[27])[1]]
        len_rows_ch2 = number_of_points_ch2 / len_columns

        big_point_ch2 = 0
        for i in range(28 + math.ceil(len_rows_ch1),
                       57 + math.ceil(len_rows_ch1)):
            big_point_ch2 += len(file_read_lines[i])

        big_point_ch2 = big_point_ch2 + end_point_ch1
        end_point_ch2 = big_point_ch2 + int(len_rows_ch2 * 73)

        str_data_ch2 = file_read[big_point_ch2: end_point_ch2]
        str_data_ch2 = re.findall(str_re_findall, str_data_ch2)
        array_data_ch2 = np.array(str_data_ch2)

        number_of_points_ch3 = int(re.findall(str_re_findall, file_read_lines[
            85 + math.ceil(len_rows_ch1) + math.ceil(len_rows_ch2)])[0])
        periods_all += [re.findall(str_re_findall, file_read_lines[27])[1]]
        len_rows_ch3 = number_of_points_ch3 / len_columns

        big_point_ch3 = 0
        for i in range(57 + math.ceil(len_rows_ch1) + math.ceil(len_rows_ch2),
                       86 + math.ceil(len_rows_ch1) + math.ceil(len_rows_ch2)):
            big_point_ch3 += len(file_read_lines[i])

        big_point_ch3 = big_point_ch3 + end_point_ch2
        end_point_ch3 = big_point_ch3 + int(len_rows_ch3 * 73)

        str_data_ch3 = file_read[big_point_ch3: end_point_ch3]
        str_data_ch3 = re.findall(str_re_findall, str_data_ch3)
        array_data_ch3 = np.array(str_data_ch3)

        #station = file_read_lines[4][:19].replace('  ', '')
        station = file_read_lines[4][11:20].replace(' ', '')
        period = re.findall(str_re_findall, file_read_lines[10])[-1]
        channels = ['CH 1', 'CH 2', 'CH 3']
        periods_all = 1/np.array(periods_all, dtype=np.float64)

        return array_data_ch1, array_data_ch2, array_data_ch3, \
            station, periods_all, channels

    def read_file_obspy(self, df_obs):
        array_data_all = []
        period_all = []
        channel_all = []
        df_obs = df_obs.reset_index(drop=True)
        for i in range(len(df_obs)):
            read_traces = ob.read(df_obs['File_path'][i])
            print(df_obs['File_path'][i])
            print(df_obs['Obs_channel'][i])
            if len(read_traces) == 1:
                array_data = np.array(read_traces[0].data, dtype=np.float64)
                array_data_all += [array_data]
                period_all += [1/float(read_traces[0].stats.sampling_rate)]
                channel_all += [df_obs['Obs_channel'][i]]
        return array_data_all, period_all, channel_all

    def calculate_FAS(self, X_data, Y_data):
        X_data_FAS = []
        Y_data_FAS = []
        for i in range(3):
            if len(X_data[i]) > 1:
                X_data_calc = np.array(X_data[i], dtype=np.float64)
                Y_data_calc = np.array(Y_data[i], dtype=np.float64)

                record_frequency = X_data_calc[1] - X_data_calc[0]

                X_data_FAS_calc = fft.fftfreq(len(X_data_calc)) * \
                                  record_frequency
                Y_data_FAS_calc = fft.fft(Y_data_calc)

                X_data_FAS_calc = np.array(X_data_FAS_calc)[1: int(
                    len(X_data_FAS_calc) / 2)]
                Y_data_FAS_calc = np.abs(np.array(Y_data_FAS_calc)[1: int(
                    len(Y_data_FAS_calc) / 2)])

                X_data_FAS += [np.array(X_data_FAS_calc, dtype=np.float64)]
                Y_data_FAS += [np.array(Y_data_FAS_calc, dtype=np.float64)]
            else:
                X_data_FAS += ['']
                Y_data_FAS += ['']

        signal_out = {'Action': 'DrawFAS', 'DataX': X_data_FAS,
                      'DataY': Y_data_FAS}
        self.back_to_front_queue.put(signal_out)

    def calculate_spectrogram(self, X_data, Y_data):
        frequency = 1 / (X_data[1] - X_data[0])
        freq_spectrogram, time_spectrogram, amplitude_spectrogram = \
            signal.spectrogram(Y_data, frequency)

        amplitude_spectrogram = 10 * np.log(amplitude_spectrogram /
                                            np.max(amplitude_spectrogram))

        signal_out = {'Action': 'DrawSpectrogram',
                      'DataFreq': freq_spectrogram,
                      'DataY': time_spectrogram,
                      'Amplitude': amplitude_spectrogram,
                      'Frequency': frequency}
        self.back_to_front_queue.put(signal_out)
