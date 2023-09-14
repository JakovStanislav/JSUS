import gc
import sys
import threading
import time

import matplotlib
import numpy as np
from queue import Queue
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtCore as qtc
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, \
    QTableWidget, QTableWidgetItem, QHBoxLayout, QToolBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar

# matplotlib.use('Qt5Agg')
matplotlib.use('agg')


def start_gui_thread(back_to_front_queue: Queue, front_to_back_queue: Queue):
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setApplicationName("Example.")
    gui = Gui(front_to_back_queue, back_to_front_queue)
    gui.setGeometry(100, 100, 900, 400)
    gui.show()
    app.exec_()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax2 = plt.subplots(3, 1, figsize=(width, height),
                                          dpi=dpi)
        self.axes = self.ax2
        self.figs = self.fig
        self.figs.tight_layout()
        # self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class MplCanvasFAS(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig_FAS, self.ax2_FAS = plt.subplots(3, 1, figsize=(width, height),
                                                  dpi=dpi)
        self.axes_FAS = self.ax2_FAS
        self.figs_FAS = self.fig_FAS
        self.figs_FAS.tight_layout()
        # self.axes = self.fig.add_subplot(111)
        super(MplCanvasFAS, self).__init__(self.fig_FAS)


class MplCanvas_Spectrogram(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig_spectrogram, self.axes_spectrogram = plt.subplots(
            2, 1, figsize=(width, height), dpi=dpi)
        self.axes_spectrogram = self.axes_spectrogram
        self.fig_spectrogram = self.fig_spectrogram
        self.fig_spectrogram.subplots_adjust(wspace=0, hspace=0)
        # self.figs.tight_layout()
        # self.axes = self.fig.add_subplot(111)
        super(MplCanvas_Spectrogram, self).__init__(self.fig_spectrogram)


class LoadingWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setWindowTitle('Loading')
        self.label = QLabel("Reading all files in directory ...")
        layout.addWidget(self.label)
        self.setGeometry(20, 20, 300, 50)
        self.setLayout(layout)


class FASWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    submit_clicked_spectrogram_to_gui = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fourier Amplitude Spectra')
        # self.label = QLabel("Reading all files in directory ...")
        self.setGeometry(20, 20, 600, 600)
        self.canvas_FAS = MplCanvasFAS(self, width=5, height=4, dpi=100)
        # self.cid = self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.onclick)
        # self.cid = self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.keyPressEvent)
        self.cid = self.canvas_FAS.figs_FAS.canvas.mpl_connect(
            "motion_notify_event", self.on_move)
        # plt.gcf().canvas.mpl_connect('pick_event', self.onclick_del)
        # self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.onclick)

        self.canvas_FAS.axes_FAS[0].plot([], [])
        self.canvas_FAS.axes_FAS[1].plot([], [])
        self.canvas_FAS.axes_FAS[2].plot([], [])

        toolbar_FAS = NavigationToolbar(self.canvas_FAS, self)

        FAS_upper_layout = QHBoxLayout(self)
        FAS_wind_layout = QVBoxLayout(self)
        FAS_wind_main = QWidget(self)
        upper_widget = QWidget(self)

        self.pybutton_show_spectrogram = QPushButton(
            'Show spectrogram', self)
        self.pybutton_show_spectrogram.resize(100, 32)
        self.pybutton_show_spectrogram.move(50, 50)
        self.pybutton_show_spectrogram.clicked.connect(
            self.fun_show_spectrogram)

        FAS_upper_layout.addWidget(toolbar_FAS)
        FAS_upper_layout.addStretch()
        FAS_upper_layout.addWidget(self.pybutton_show_spectrogram)
        upper_widget.setLayout(FAS_upper_layout)
        FAS_wind_layout.addWidget(upper_widget)
        FAS_wind_layout.addWidget(self.canvas_FAS)
        FAS_wind_layout.addStretch()
        self.setLayout(FAS_wind_layout)
        self.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def on_move(self, event):
        x_pom = event.xdata
        y_pom = event.ydata

    def fun_show_spectrogram(self):
        self.spectogram_window = SpectrogramWindow()
        self.spectogram_window.show()
        self.spectogram_window.submit_clicked_spectrogram_to_fas.connect(
            self.connect_fas_spectrogram_gui)

    def connect_fas_spectrogram_gui(self, channel):
        self.submit_clicked_spectrogram_to_gui.emit(channel)


class SpectrogramWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    submit_clicked_spectrogram_to_fas = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Spectrogram')
        self.setGeometry(20, 20, 850, 650)
        self.canvas_spectrogram = MplCanvas_Spectrogram(self, width=5,
                                                        height=4, dpi=100)
        # self.cid = self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.onclick)
        # self.cid = self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.keyPressEvent)
        self.cid = self.canvas_spectrogram.fig_spectrogram.canvas.mpl_connect(
            "motion_notify_event", self.on_move)
        # plt.gcf().canvas.mpl_connect('pick_event', self.onclick_del)
        # self.sc2.figs_New_Wind.canvas.mpl_connect('key_press_event', self.onclick)
        self.canvas_spectrogram.axes_spectrogram[0].plot([], [])
        self.canvas_spectrogram.axes_spectrogram[1].plot([], [])
        toolbar_spectrogram = NavigationToolbar(self.canvas_spectrogram, self)

        self.combobox = QComboBox(self)
        self.combobox.addItems(['CH 1', 'CH 2', 'CH 3'])

        self.pybutton_plot_spectrogram = QPushButton(
            'Show spectrogram', self)
        self.pybutton_plot_spectrogram.resize(100, 32)
        self.pybutton_plot_spectrogram.move(50, 50)
        self.pybutton_plot_spectrogram.clicked.connect(
            self.get_data_to_plot)

        spectrogram_layout_upper = QHBoxLayout(self)
        spectrogram_layout = QVBoxLayout(self)
        spectrogram_upper_widget = QWidget(self)
        spectrogram_layout_upper.addWidget(toolbar_spectrogram)
        spectrogram_layout_upper.addStretch()
        spectrogram_layout_upper.addWidget(self.combobox)
        spectrogram_layout_upper.addWidget(self.pybutton_plot_spectrogram)
        spectrogram_upper_widget.setLayout(spectrogram_layout_upper)
        spectrogram_layout.addWidget(spectrogram_upper_widget)
        spectrogram_layout.addWidget(self.canvas_spectrogram)
        spectrogram_layout.addStretch()
        self.setLayout(spectrogram_layout)
        self.show()

    def get_data_to_plot(self):
        selected_channel = self.combobox.currentText()
        self.submit_clicked_spectrogram_to_fas.emit(selected_channel)

    def on_move(self, event):
        x_pom = event.xdata
        y_pom = event.ydata


class Gui(QMainWindow):

    def __init__(self, front_to_back_queue: Queue, back_to_front_queue: Queue):
        super().__init__()
        self.front_to_back_queue = front_to_back_queue
        self.back_to_front_queue = back_to_front_queue

        self.title = 'Just a Simple Ui for Seismographs'
        self.left = 350
        self.top = 35
        self.width = 15000
        self.height = 15000
        self.window_loading = None
        self.window_FAS = None

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_layout = QHBoxLayout(self)
        self.right_layout = QVBoxLayout(self)
        self.left_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 35, 1, 1)
        self.main_widget = QWidget()
        self.widget_left = QWidget()
        # self.widget_left.setMaximumSize(450, 500)
        self.widget_left.setFixedSize(450, 500)
        self.widget_right = QWidget()
        self.widget_right.setMinimumSize(900, 600)
        self.create_table()

        self.fig_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        # self.cid = self.fig_canvas.figs.canvas.mpl_connect('key_press_event',
        #                                             self.onclick)
        # self.cid = self.fig_canvas.figs.canvas.mpl_connect('key_press_event',
        #                                             self.keyPressEvent)
        # self.cid = self.fig_canvas.figs.canvas.mpl_connect("motion_notify_event",
        #                                             self.on_move)
        # plt.gcf().canvas.mpl_connect('pick_event', self.onclick_del)

        # self.fig_canvas.figs.canvas.mpl_connect('key_press_event', self.onclick)

        self.fig_canvas.axes[0].plot([], [])
        self.fig_canvas.axes[1].plot([], [])
        self.fig_canvas.axes[2].plot([], [])

        self.toolbar_fig = NavigationToolbar(self.fig_canvas, self)
        self.toolbar = QToolBar("My main toolbar")

        self.right_layout.addWidget(self.toolbar_fig)
        self.right_layout.addWidget(self.fig_canvas)

        self._background_reader_thread = threading.Thread(
            target=self._bg_reading_function)
        self._background_reader_thread.start()

        self.left_layout.addWidget(self.tableWidget)
        self.left_layout.addStretch()
        self.widget_left.setLayout(self.left_layout)
        self.widget_right.setLayout(self.right_layout)
        self.main_layout.addWidget(self.widget_left)
        self.main_layout.addWidget(self.widget_right)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.menu_main = QMenuBar(self)
        self.menu_files = self.menu_main.addMenu("&Files")
        read_file = QAction('Read file', self)
        read_file.triggered.connect(self.fun_read_file)
        read_batch = QAction('Read batch', self)
        read_batch.triggered.connect(self.fun_read_batch)

        self.menu_files.addAction(read_file)
        self.menu_files.addAction(read_batch)
        self.menu_data = self.menu_main.addMenu("&Data")
        open_map = QAction('Map selection', self)
        # open_map.triggered.connect(self.show_new_window_MAP)
        self.menu_data.addAction(open_map)
        self.show()
        self.window_FAS = FASWindow()
        self.window_FAS.hide()

    def fun_read_file(self):
        self.fun_browser_file()

    def fun_read_batch(self):
        self.fun_browser_directory()

    def fun_browser_file(self):
        # file_path_pom = ''
        file_path_pom = QFileDialog.getOpenFileNames(self, 'Search file',
                                                     r":\Users",
                                                     "SAC (*.SAC);; "
                                                     "Text files (*.txt);; "
                                                     "V1 (*.v1)")

        if file_path_pom[0]:
            print(file_path_pom[0][0])
            self.file_path = str(file_path_pom[0][0])
            self.file_name = os.path.basename(self.file_path)
            send_back = {'Action': 'read_file', 'FilePath': self.file_path,
                         'FileName': self.file_name, 'FileExtension':
                             os.path.splitext(self.file_path)[-1].lower()}
            self.front_to_back_queue.put(send_back)
        else:
            print('No path selected')

    def fun_browser_directory(self):
        # file_path_pom = ''
        directory_path = QFileDialog.getExistingDirectory(self, 'Search file',
                                                          r":\Users")
        if directory_path:
            print(directory_path)
            self.directory_path = str(directory_path)
            send_back = {'Action': 'read_batch',
                         'DirectoryPath': self.directory_path}
            self.show_loading_window()
            self.front_to_back_queue.put(send_back)
        else:
            print('No directory selected')

    def _bg_reading_function(self):
        while True:
            msg = self.back_to_front_queue.get()

            if msg['Action'] == 'Loaded traces':
                #print(msg)
                self.update_table(msg['Data'])
                if self.window_loading.isVisible():
                    print('Close')
                    time.sleep(0.25)
                    self.window_loading.hide()
            elif msg['Action'] == 'Loaded traces v1':
                data_for_table = np.array([msg['Record'], '/', msg['Data'][-2]])
                self.update_table(data_for_table)
                self.plot_data(msg['Data'], msg['Periods'], msg['Channels'])
            elif msg['Action'] == 'Draw record v1':
                self.plot_data(msg['Data'], msg['Periods'], msg['Channels'])
            elif msg['Action'] == 'Draw record obspy':
                self.plot_data(msg['Data'], msg['Periods'], msg['Channels'])
            elif msg['Action'] == 'DrawFAS':
                self.plot_data_FAS(msg['DataX'], msg['DataY'])
            elif msg['Action'] == 'DrawSpectrogram':
                self.plot_spectrogram_data(msg['DataFreq'], msg['DataY'],
                                           msg['Amplitude'], msg['Frequency'])

    def contextMenuEventTable(self, point):
        contextMenu = QMenu(self)
        load_file = contextMenu.addAction("Draw file")
        load_file_FAS = contextMenu.addAction("Calculate FAS")
        # quitAct = contextMenu.addAction("Quit")
        # action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        action = contextMenu.exec_(
            self.tableWidget.mapToGlobal(point))
        if action == load_file:
            selected_row = self.tableWidget.selectedItems()
            selected_record = selected_row[0].text()
            self.recoed_name = selected_row[0].text()
            print(selected_record)

            if selected_record.lower().endswith('.txt'):
                send_back = {'Action': 'OpenRecord', 'Extension': '.txt',
                             'RecordPath': selected_record}
                self.front_to_back_queue.put(send_back)
            elif selected_record.lower().endswith('.v1'):
                send_back = {'Action': 'OpenRecord', 'Extension': '.v1',
                             'RecordPath': selected_record}
                self.front_to_back_queue.put(send_back)
            else:
                send_back = {'Action': 'OpenRecord', 'Extension': 'obspy',
                             'RecordPath': selected_record}
                self.front_to_back_queue.put(send_back)

        elif action == load_file_FAS:
            selected_row = self.tableWidget.selectedItems()
            selected_record = selected_row[0].text()
            self.recoed_name = selected_row[0].text()
            print(selected_record)
            dummy_plot = []

            # for i in range(3):
            #     try:
            #         lines = self.fig_canvas.axes[i].lines
            #         data = lines[0].get_data()[0]
            #         dummy_plot = [True]
            #     except IndexError:
            #         dummy_plot = [False]
            try:
                if selected_record != self.fig_canvas.figs._suptitle.get_text():
                    dummy_plot = [True]
                else:
                    dummy_plot = [False]
            except AttributeError:
                dummy_plot = [True]

            if any(dummy_plot):
                if selected_record.lower().endswith('.txt'):
                    send_back = {'Action': 'OpenRecord', 'Extension': '.txt',
                                 'RecordPath': selected_record}
                    self.front_to_back_queue.put(send_back)
                elif selected_record.lower().endswith('.v1'):
                    send_back = {'Action': 'OpenRecord', 'Extension': '.v1',
                                 'RecordPath': selected_record}
                    self.front_to_back_queue.put(send_back)
                else:
                    send_back = {'Action': 'OpenRecord', 'Extension': 'obspy',
                                 'RecordPath': selected_record}
                    print(selected_record)
                    self.front_to_back_queue.put(send_back)

            time.sleep(0.25)
            print('Fas started0')
            self.data_for_FAS()
            print('Fas ended0')

    def create_table(self):
        # Create table
        data_key = ['Record', 'Network', 'Station', 'Channel']
        self.tableWidget = QTableWidget()
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(
            self.contextMenuEventTable)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(len(data_key))
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setHorizontalHeaderLabels(data_key)
        self.tableWidget.setColumnWidth(0, 125)
        self.tableWidget.setColumnWidth(1, 75)
        self.tableWidget.setColumnWidth(2, 75)
        self.tableWidget.setColumnWidth(3, 100)
        # self.tableWidget.setFixedHeight(500)
        # self.tableWidget.setFixedWidth(600)

    def update_table(self, data):
        data_key = ['Record', 'Network', 'Station', 'Channel']
        self.tableWidget.setColumnCount(len(data_key))

        if len(data.shape) > 1:
            self.tableWidget.setRowCount(data.shape[0])
            for i in range(len(data)):
                table_item0 = QTableWidgetItem(data[i, 0])
                self.tableWidget.setItem(i, 0, table_item0)

                table_item1 = QTableWidgetItem(data[i, 1])
                self.tableWidget.setItem(i, 1, table_item1)

                table_item2 = QTableWidgetItem(data[i, 2])
                self.tableWidget.setItem(i, 2, table_item2)

                table_item3 = QTableWidgetItem(data[i, 3])
                self.tableWidget.setItem(i, 3, table_item3)
        else:
            self.tableWidget.setRowCount(1)
            table_item0 = QTableWidgetItem(data[0])
            self.tableWidget.setItem(0, 0, table_item0)

            table_item1 = QTableWidgetItem(data[1])
            self.tableWidget.setItem(0, 1, table_item1)

            table_item2 = QTableWidgetItem(data[2])
            self.tableWidget.setItem(0, 2, table_item2)

        self.tableWidget.setColumnWidth(1, 75)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.resizeRowsToContents()
        if data.shape[0] > 6:
            self.widget_left.setFixedSize(450, 1000)
            self.tableWidget.setFixedHeight(900)

    def plot_data(self, ordinate, period_all, channels):
        self.fig_canvas.axes[0].clear()
        self.fig_canvas.axes[1].clear()
        self.fig_canvas.axes[2].clear()
        #period = float(period_all)
        for i in range(len(ordinate)):
            period = float(period_all[i])
            print(period)
            ordinate_float = np.array(ordinate[i], dtype=np.float64)
            if channels[i].find('1') != -1 or channels[i].lower().find(
                    'n') != -1:
                ind_plot = 0
            elif channels[i].find('2') != -1 or channels[i].lower().find(
                    'e') != -1:
                ind_plot = 1
            elif channels[i].find('3') != -1 or channels[i].lower().find(
                    'z') != -1:
                ind_plot = 2

            self.fig_canvas.axes[ind_plot].plot(
                np.arange(0, len(ordinate_float) * period, period),
                ordinate_float)
            self.fig_canvas.axes[ind_plot].set_title(channels[i])
            self.fig_canvas.axes[ind_plot].set_xlabel(
                'Time [s]')
            self.fig_canvas.axes[ind_plot].set_ylabel('Amplitude')

        self.fig_canvas.figs.suptitle(self.recoed_name, x=0.5, y=0.995)
        self.fig_canvas.figs.tight_layout()
        self.fig_canvas.figs.canvas.draw()

        if self.window_FAS.isVisible():
            print('Fas started')
            self.data_for_FAS()
            print('Fas ended')

    def draw_selected_record(self):
        selected_row = self.tableWidget.selectedItems()
        selected_record = selected_row[0].text()
        print(selected_record)

        if selected_record.lower().endswith('.txt'):
            send_back = {'Action': 'OpenRecord', 'Extension': '.txt',
                         'RecordPath': selected_record}
            self.front_to_back_queue.put(send_back)
        elif selected_record.lower().endswith('.v1'):
            send_back = {'Action': 'OpenRecord', 'Extension': '.v1',
                         'RecordPath': selected_record}
            self.front_to_back_queue.put(send_back)
        else:
            send_back = {'Action': 'OpenRecord', 'Extension': 'obspy',
                         'RecordPath': selected_record}
            self.front_to_back_queue.put(send_back)

    def data_for_FAS(self):
        self.data_abscissa = []
        self.data_ordinate = []
        for i in range(3):
            try:
                lines = self.fig_canvas.axes[i].lines
                self.data_abscissa += [lines[0].get_data()[0]]
                self.data_ordinate += [lines[0].get_data()[1]]
            except IndexError:
                self.data_abscissa += ['']
                self.data_ordinate += ['']

        signal = {'Action': 'CalculateFAS', 'DataX': self.data_abscissa,
                  'DataY': self.data_ordinate}
        self.front_to_back_queue.put(signal)

    def show_loading_window(self):
        if self.window_loading is None:
            self.window_loading = LoadingWindow()
        self.window_loading.show()

    def plot_data_FAS(self, data_X, data_Y):
        if self.window_FAS.isVisible() != True:
            time.sleep(0.25)
            self.window_FAS.show()
        self.window_FAS.canvas_FAS.axes_FAS[0].clear()
        self.window_FAS.canvas_FAS.axes_FAS[1].clear()
        self.window_FAS.canvas_FAS.axes_FAS[2].clear()
        for i in range(3):
            if len(data_X[i]) > 1:
                self.window_FAS.canvas_FAS.axes_FAS[i].semilogx(data_X[i],
                                                                data_Y[i])
                self.window_FAS.canvas_FAS.axes_FAS[i].set_xlabel(
                    'Frequency [Hz]')
                self.window_FAS.canvas_FAS.axes_FAS[i].set_ylabel('Amplitude')
        self.window_FAS.canvas_FAS.figs_FAS.tight_layout()
        self.window_FAS.canvas_FAS.figs_FAS.canvas.draw()
        self.window_FAS.submit_clicked_spectrogram_to_gui.connect(
            self.initiate_plot_spectrogram_data)
        time.sleep(0.2)
        self.window_FAS.raise_()

    def initiate_plot_spectrogram_data(self, channel):
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[0] \
            .clear()
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[1] \
            .clear()

        self.index_channel = (np.array(['CH 1', 'CH 2', 'CH 3']) ==
                              channel).nonzero()[0][0]

        abscissa_spectrogram = self.data_abscissa[self.index_channel]
        ordinate_spectrogram = self.data_ordinate[self.index_channel]
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[1
        ].plot(abscissa_spectrogram, ordinate_spectrogram)

        signal = {'Action': 'CalculateSpectrogram',
                  'DataX': abscissa_spectrogram,
                  'DataY': ordinate_spectrogram}
        self.front_to_back_queue.put(signal)

    def plot_spectrogram_data(self, data_freq, data_time, amplitude, frequency):
        color_map = cm.jet
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[
            0].contourf(data_time, data_freq, amplitude,
                        levels=500, cmap=color_map)

        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[
            0].set_ylabel('Frequency [Hz]')
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[
            1].set_xlabel('Time [s]')
        self.window_FAS.spectogram_window.canvas_spectrogram.axes_spectrogram[
            0].set_aspect('auto')

        plt.xlim([0, len(self.data_abscissa[self.index_channel]) / frequency])
        self.window_FAS.spectogram_window.canvas_spectrogram.fig_spectrogram.canvas.draw()

