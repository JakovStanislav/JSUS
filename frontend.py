import gc
import sys
import threading
import time

import matplotlib
import numpy as np
from queue import Queue

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.Qt import Qt
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, \
    QTableWidget, QTableWidgetItem, QHBoxLayout, QToolBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar
from cycler import cycler

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

class MplCanvasColormap(FigureCanvasQTAgg):
    def __init__(self, parent=None, no_colors=1, width=5., height=4., dpi=100):
        self.fig_colormap, self.ax2_colormap = plt.subplots(
             no_colors, 1, figsize=(width, height), dpi=dpi)
        self.axes_colormap = self.ax2_colormap
        self.figs_colormap = self.fig_colormap
        self.figs_colormap.tight_layout()
        # self.axes = self.fig.add_subplot(111)
        super(MplCanvasColormap, self).__init__(self.fig_colormap)


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
    submit_event_spectrogram_to_gui = qtc.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.spectrogram_window = None
        self.setWindowTitle('Fourier Amplitude Spectra')
        self.setGeometry(20, 20, 850, 750)
        self.canvas_FAS = MplCanvasFAS(self, width=5, height=8, dpi=100)
        self.cid = self.canvas_FAS.figs_FAS.canvas.mpl_connect(
            "motion_notify_event", self.on_move)

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
        self.spectrogram_window = SpectrogramWindow()
        self.spectrogram_window.canvas_spectrogram.setContextMenuPolicy(
            Qt.ActionsContextMenu)
        self.fig_spectrogram_colormap = QtWidgets.QAction(
            'Change colormap', self)
        self.fig_spectrogram_colormap.triggered.connect(
            self.fig_canvas_colormap_change)
        self.spectrogram_window.canvas_spectrogram.addAction(
            self.fig_spectrogram_colormap)
        self.spectrogram_window.show()
        self.spectrogram_window.submit_clicked_spectrogram_to_fas.connect(
            self.connect_fas_spectrogram_gui)
        self.spectrogram_window.submit_event_spectrogram_to_fas.connect(
            self.connect_fas_spectrogram_gui_event)
    def connect_fas_spectrogram_gui(self, channel):
        self.submit_clicked_spectrogram_to_gui.emit(channel)
    def connect_fas_spectrogram_gui_event(self, str_phase, value):
        self.submit_event_spectrogram_to_gui.emit(str_phase, value)
    def fig_canvas_colormap_change(self):
        self.colormap_window = SelectColormapWindow()
        self.colormap_window.submit_clicked_colormap.connect(self.update_colors)
    def update_colors(self, cmap_str):
        ax = self.spectrogram_window.canvas_spectrogram.axes_spectrogram[0]
        print(cmap_str)
        cmap = pl.get_cmap(cmap_str)
        lines = ax._children
        colors = cmap(np.linspace(0, 1, len(lines)))
        for line, c in zip(lines, colors):
            line.set_color(c)
        self.spectrogram_window.canvas_spectrogram.fig_spectrogram.canvas.draw()

class SpectrogramWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    submit_clicked_spectrogram_to_fas = qtc.pyqtSignal(str)
    submit_event_spectrogram_to_fas = qtc.pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Spectrogram')
        self.setGeometry(20, 20, 850, 650)
        self.canvas_spectrogram = MplCanvas_Spectrogram(self, width=5,
                                                        height=4, dpi=100)
        self.cid = self.canvas_spectrogram.fig_spectrogram.canvas.mpl_connect(
            "motion_notify_event", self.on_move)
        plt.gcf().canvas.mpl_connect('pick_event', self.mouse_press_event)
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
        self.x_mouse_location = event.xdata
        self.y_mouse_location = event.ydata

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.ControlModifier:
            print('str(event)')
            if event.key() == Qt.Key_S and self.x_mouse_location is not None:
                print("Ctrl + S")
                self.submit_event_spectrogram_to_fas.emit(
                    'S_phase_draw', str(self.x_mouse_location))
            elif event.key() == Qt.Key_D and self.x_mouse_location is not None:
                print("Ctrl + D")
                self.submit_event_spectrogram_to_fas.emit(
                    'P_phase_draw', str(self.x_mouse_location))
            elif event.key() == Qt.Key_E:
                print("Ctrl + E")
                print(self.y_mouse_location)

    def mouse_press_event(self, event):
        print(event)
        if event.mouseevent.button == 2:
            this_line = event.artist
            value_of_deleted_line = this_line._x[0]
            print(value_of_deleted_line)

            self.submit_event_spectrogram_to_fas.emit(
                'Phase_delete', str(value_of_deleted_line))

class SelectColormapWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    submit_clicked_colormap = qtc.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.df_colormaps = pd.read_csv(r'ColorMaps.csv', delimiter=';')
        print(self.df_colormaps)
        self.setWindowTitle('Select colormap')
        self.setGeometry(20, 20, 500, 300)

        categories = self.df_colormaps['Categories']
        cmap_list = (self.df_colormaps['Colormaps'][
            self.df_colormaps['Categories'] == categories[0]]).item()
        cmap_list = list(cmap_list.split(', '))
        self.old_cmap_list = cmap_list
        self.combo_box_category = QComboBox()
        self.combo_box_category.addItems(categories)
        self.category_QLabel = QLabel(self)
        self.category_QLabel.setText('Select category:')
        self.category_QLabel.setFixedWidth(80)
        self.combo_box_category.currentTextChanged.connect(
            self.changed_category)
            #setContextMenuPolicy(Qt.Actions)
        #self.fig_canvas_grid = QtWidgets.QAction('Toggle grid', self)
        #self.fig_canvas_grid.triggered.connect(self.fig_canvas_grid_on_off)

        self.combo_box_colormap = QComboBox()
        self.combo_box_colormap.addItems(cmap_list)
        self.colormap_QLabel = QLabel(self)
        self.colormap_QLabel.setText('Select colormap:')
        self.colormap_QLabel.setFixedWidth(80)
        self.combo_box_colormap.currentTextChanged.connect(
            self.changed_colormap)

        self.category_layout = QHBoxLayout(self)
        self.category_widget = QWidget(self)
        self.category_layout.addWidget(self.category_QLabel)
        self.category_layout.addWidget(self.combo_box_category)
        self.category_widget.setLayout(self.category_layout)

        self.colormap_layout = QHBoxLayout(self)
        self.colormap_widget = QWidget(self)
        self.colormap_layout.addWidget(self.colormap_QLabel)
        self.colormap_layout.addWidget(self.combo_box_colormap)
        self.colormap_widget.setLayout(self.colormap_layout)

        category = categories[0]
        self.plot_color_gradients(category, cmap_list)
        self.main_layout = QVBoxLayout(self)
        self.main_widget = QWidget(self)
        self.main_layout.addWidget(self.category_widget)
        self.main_layout.addWidget(self.colormap_widget)
        self.main_layout.addWidget(self.fig_canvas_colormap)
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.setLayout(self.main_layout)
        self.show()

    def changed_category(self):
        new_category = self.combo_box_category.currentText()
        print(new_category)
        self.main_layout.removeWidget(self.fig_canvas_colormap)
        self.fig_canvas_colormap.deleteLater()
        self.fig_canvas_colormap = None

        self.combo_box_colormap.disconnect()
        cmap_list = (self.df_colormaps['Colormaps'][
            self.df_colormaps['Categories'] == new_category]).item()
        cmap_list = list(cmap_list.split(', '))
        print(cmap_list)
        self.combo_box_colormap.clear()
        self.combo_box_colormap.currentTextChanged.connect(
            self.changed_colormap)
        self.combo_box_colormap.addItems(cmap_list)
        self.plot_color_gradients(new_category, cmap_list)
        self.fig_canvas_colormap.figs_colormap.canvas.draw()
        self.main_layout.addWidget(self.fig_canvas_colormap)
        self.main_layout.addStretch()
        self.main_layout.update()
    def changed_colormap(self):
        new_colormap = self.combo_box_colormap.currentText()
        print(new_colormap)
        self.submit_clicked_colormap.emit(new_colormap)

    def plot_color_gradients(self, category, cmap_list):
        self.fig_canvas_colormap = None
        cmaps = {}
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))
        nrows = len(cmap_list)
        figh = 0.8 + (nrows + (nrows - 1) * 0.1) * 0.22
        self.fig_canvas_colormap = MplCanvasColormap(
            self, no_colors=nrows + 1, width=7, height=figh, dpi=100)
        fig = self.fig_canvas_colormap.figs_colormap
        axs = self.fig_canvas_colormap.axes_colormap
        fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0,
                            left=0.2, right=0.99)#.15 / figh
        #axs[0].set_title(' colormaps'.join([str(category), ' ']), fontsize=10)
        axs[0].set_title(f'{category} colormaps', fontsize=14)

        for ax, name in zip(axs, cmap_list):
            ax.imshow(gradient, aspect='auto', cmap=matplotlib.colormaps[name])
            ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                    transform=ax.transAxes)

        # Turn off *all* ticks & spines, not just the ones with colormaps.
        for ax in axs:
            ax.set_axis_off()

        # Save colormap list for later.
        cmaps[category] = cmap_list

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
        self.spec_canvas = None
        self.grid_dummy = True
        self.grid_FAS_dummy = True

        self.P_phase_time = 0
        self.S_phase_time = 0
        self.list_lines_P_phase = []
        self.list_lines_S_phase = []

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_layout = QHBoxLayout(self)
        self.right_layout = QVBoxLayout(self)
        self.right_layout_upper = QHBoxLayout(self)
        self.left_layout = QVBoxLayout(self)
        self.phases_layout_P = QVBoxLayout(self)
        self.phases_layout_S = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 0, 1, 1)
        self.main_widget = QWidget()
        self.widget_left = QWidget()
        self.widget_right = QWidget()
        self.widget_right_upper = QWidget()
        self.phases_widget_P = QWidget()
        self.phases_widget_S = QWidget()
        # self.widget_left.setMaximumSize(450, 500)
        self.widget_left.setFixedSize(450, 500)
        self.widget_right.setMinimumSize(900, 900)
        self.create_table()

        self.fig_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.cid = self.fig_canvas.figs.canvas.mpl_connect('key_press_event',
                                                           self.on_click)
        self.cid = self.fig_canvas.figs.canvas.mpl_connect('key_press_event',
                                                           self.keyPressEvent)
        #self.cid = self.fig_canvas.figs.canvas.mpl_connect('button_press_event',
        #                                                   self.mousePressEvent)
        plt.gcf().canvas.mpl_connect('pick_event', self.mouse_press_event)
        self.cid = self.fig_canvas.figs.canvas.mpl_connect(
            "motion_notify_event", self.on_move)
        # self.fig_canvas.figs.canvas.mpl_connect('pick_event', self.on_click_del)
        # self.fig_canvas.figs.canvas.mpl_connect('key_press_event',
        #                                         self.on_click)


        self.fig_canvas.axes[0].plot([], [])
        self.fig_canvas.axes[1].plot([], [])
        self.fig_canvas.axes[2].plot([], [])

        self.toolbar_fig = NavigationToolbar(self.fig_canvas, self)
        self.toolbar = QToolBar("My main toolbar")

        self.P_QLabel = QLabel(self)
        self.P_QLabel.setText('P phase:')
        self.P_QLabel.setFixedWidth(65)
        self.P_QLineEdit = QLineEdit(self)
        self.P_QLineEdit.setFixedWidth(180)
        self.P_QLineEdit.setText(str(0))

        self.S_QLabel = QLabel(self)
        self.S_QLabel.setText('S phase:')
        self.S_QLabel.setFixedWidth(65)
        self.S_QLineEdit = QLineEdit(self)
        self.S_QLineEdit.setFixedWidth(180)
        self.S_QLineEdit.setText(str(0))

        self.phases_layout_P.addWidget(self.P_QLabel)
        self.phases_layout_P.addWidget(self.P_QLineEdit)
        self.phases_widget_P.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)
        self.phases_layout_S.addWidget(self.S_QLabel)
        self.phases_layout_S.addWidget(self.S_QLineEdit)
        self.phases_widget_P.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)

        self.phases_widget_P.setLayout(self.phases_layout_P)
        self.phases_widget_S.setLayout(self.phases_layout_S)
        self.right_layout_upper.addWidget(self.toolbar_fig)
        self.right_layout_upper.addStretch()
        self.right_layout_upper.addWidget(self.phases_widget_P)
        self.right_layout_upper.addWidget(self.phases_widget_S)
        self.right_layout_upper.setContentsMargins(0, 0, 0, 0)
        self.right_layout_upper.setSizeConstraint(1)
        self.widget_right_upper.setSizePolicy(QSizePolicy.Expanding,
                                              QSizePolicy.Minimum)
        self.widget_right_upper.setLayout(self.right_layout_upper)

        self.widget_right_upper.setMaximumSize(900, 75)
        self.right_layout.addWidget(self.widget_right_upper)
        self.right_layout.addWidget(self.fig_canvas, stretch=20)

        self._background_reader_thread = threading.Thread(
            target=self._bg_reading_function)
        self._background_reader_thread.start()

        self.left_layout.addWidget(self.tableWidget)
        self.left_layout.addStretch()
        self.widget_left.setLayout(self.left_layout)
        self.right_layout.setContentsMargins(0, 0, 10, 10)
        self.widget_right.setLayout(self.right_layout)

        self.fig_canvas.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.fig_canvas_grid = QtWidgets.QAction('Toggle grid', self)
        self.fig_canvas_grid.triggered.connect(self.fig_canvas_grid_on_off)
        # self.ordinate_scale = QtWidgets.QAction("Change Y scale", self)
        # self.ordinate_scale.triggered.connect(self.change_ordinate_scale)
        self.fig_canvas.addAction(self.fig_canvas_grid)
        #self.fig_canvas.addAction(self.ordinate_scale)

        self.main_layout.addWidget(self.widget_left)
        self.main_layout.addWidget(self.widget_right)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.menu_main = QMenuBar(self)
        self.menu_main.setGeometry(0, 0, 150, 20)
        self.menu_main.setContentsMargins(0, 0, 0, 0)
        self.menu_files = self.menu_main.addMenu("&Files")
        read_file = QAction('Read file', self)
        read_file.triggered.connect(self.fun_read_file)
        read_batch = QAction('Read batch', self)
        read_batch.triggered.connect(self.fun_read_batch)

        self.menu_files.addAction(read_file)
        self.menu_files.addAction(read_batch)
        self.menu_data = self.menu_main.addMenu("&Data")
        open_map = QAction('Map selection', self)
        self.menu_data.addAction(open_map)
        self.show()
        self.window_FAS = FASWindow()
        self.window_FAS.hide()

        self.abscissa_FAS_log = True
        self.ordinate_FAS_log = False
        self.window_FAS.canvas_FAS.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.abscissa_scale = QtWidgets.QAction(
            'Change X scale to linear', self)
        self.ordinate_scale = QtWidgets.QAction(
            'Change Y scale to logarithmic', self)
        self.fig_canvas_FIG_grid = QtWidgets.QAction('Toggle grid', self)

        self.ordinate_scale.triggered.connect(self.change_ordinate_scale)
        self.abscissa_scale.triggered.connect(self.change_abscissa_scale)
        self.fig_canvas_FIG_grid.triggered.connect(
            self.fig_canvas_FAS_grid_on_off)

        self.window_FAS.canvas_FAS.addAction(self.abscissa_scale)
        self.window_FAS.canvas_FAS.addAction(self.ordinate_scale)
        self.window_FAS.canvas_FAS.addAction(self.fig_canvas_FIG_grid)

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
                # print(msg)
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
                self.plot_data_FAS(msg['DataX'], msg['DataTime'])
            elif msg['Action'] == 'DrawSpectrogram':
                self.plot_spectrogram_data(msg['DataFreq'], msg['DataTime'],
                                           msg['Amplitude'], msg['Frequency'])

    def contextMenuEventTable(self, point):
        contextMenu = QMenu(self)
        load_file = contextMenu.addAction("Draw file")
        load_file_FAS = contextMenu.addAction("Calculate FAS")
        action = contextMenu.exec_(self.tableWidget.mapToGlobal(point))
        if action == load_file:
            selected_row = self.tableWidget.selectedItems()
            selected_record = selected_row[0].text()
            self.record_name = selected_row[0].text()
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
            self.record_name = selected_row[0].text()
            print(selected_record)

            try:
                if selected_record != self.fig_canvas.figs._suptitle.get_text():
                    dummy_plot = True
                else:
                    dummy_plot = False
            except AttributeError:
                dummy_plot = True

            if dummy_plot:
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
            self.data_for_FAS()

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
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        # self.tableWidget.setFixedHeight(500)
        # self.tableWidget.setFixedWidth(600)

    def update_table(self, data):
        data_key = ['Record', 'Network', 'Station', 'Channel']
        self.tableWidget.setColumnCount(len(data_key))

        if len(data.shape) > 1:
            self.tableWidget.setRowCount(data.shape[0])
            for i in range(len(data)):
                table_item0 = QTableWidgetItem(data[i, 0])
                # table_item0.setFlags(qtc.Qt.ItemIsEnabled)
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
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        if data.shape[0] > 6:
            self.widget_left.setFixedSize(450, 1000)
            self.tableWidget.setFixedHeight(900)

        selected_record = self.tableWidget.item(0, 0).text()
        self.record_name = selected_record
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

    def plot_data(self, ordinate, period_all, channels):
        self.p_phase = None
        self.s_phase = None

        self.P_phase_time = 0
        self.S_phase_time = 0
        self.P_QLineEdit.setText(str(self.P_phase_time))
        self.S_QLineEdit.setText(str(self.P_phase_time))

        self.fig_canvas.axes[0].clear()
        self.fig_canvas.axes[1].clear()
        self.fig_canvas.axes[2].clear()
        self.list_ind_plot = []

        if self.grid_dummy:
            for i in range(3):
                self.fig_canvas.axes[i].grid(True)
        else:
            for i in range(3):
                self.fig_canvas.axes[i].grid(False)


        for i in range(len(ordinate)):
            period = float(period_all[i])
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
            self.list_ind_plot += [ind_plot]

            self.fig_canvas.axes[ind_plot].plot(
                np.arange(0, len(ordinate_float) * period, period),
                ordinate_float)
            self.fig_canvas.axes[ind_plot].set_title(channels[i])
            self.fig_canvas.axes[ind_plot].set_xlabel(
                'Time [s]')
            self.fig_canvas.axes[ind_plot].set_ylabel('Amplitude')

        self.fig_canvas.figs.suptitle(self.record_name, x=0.5, y=0.995)
        self.fig_canvas.figs.tight_layout()
        self.fig_canvas.figs.canvas.draw()

        if self.window_FAS.isVisible():
            self.data_for_FAS()

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
        if self.window_FAS.spectrogram_window is not None:
            print('close1')
            self.spec_canvas.axes_spectrogram[0].clear()
            self.spec_canvas.axes_spectrogram[1].clear()
            print('close2')
            self.spec_canvas.fig_spectrogram.canvas.draw()

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
                  'DataTime': self.data_ordinate}
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

        if self.grid_FAS_dummy:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].grid(True)
        else:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].grid(False)

        for i in range(3):
            if len(data_X[i]) > 1:
                self.window_FAS.canvas_FAS.axes_FAS[i].plot(data_X[i],
                                                                data_Y[i])
                self.window_FAS.canvas_FAS.axes_FAS[i].set_xlabel(
                    'Frequency [Hz]')
                self.window_FAS.canvas_FAS.axes_FAS[i].set_ylabel('Amplitude')

        if self.abscissa_FAS_log:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].set_xscale('log')
        else:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].set_xscale('linear')
        if self.ordinate_FAS_log:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].set_yscale('log')
        else:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].set_yscale('linear')

        self.window_FAS.canvas_FAS.figs_FAS.tight_layout()
        self.window_FAS.canvas_FAS.figs_FAS.canvas.draw()
        self.window_FAS.submit_clicked_spectrogram_to_gui.connect(
            self.initiate_plot_spectrogram_data)
        self.window_FAS.submit_event_spectrogram_to_gui.connect(
            self.spectrogram_phases_Picked_on_spectrogram)

        time.sleep(0.2)
        self.window_FAS.raise_()

    def spectrogram_phases_Picked_on_spectrogram(self, str_phase, value):
        self.x_mouse_location = float(value)
        if str_phase == 'P_phase_draw':
            self.draw_P_phase()
        elif str_phase == 'S_phase_draw':
            self.draw_S_phase()
        elif str_phase == 'Phase_delete':
            self.delete_phases(value)

    def initiate_plot_spectrogram_data(self, channel):
        self.spec_canvas = self.window_FAS.spectrogram_window.canvas_spectrogram
        self.spec_canvas.axes_spectrogram[0].clear()
        self.spec_canvas.axes_spectrogram[1].clear()

        self.list_lines_P_phase_spec_axes_0 = []
        self.list_lines_P_phase_spec_axes_1 = []
        self.list_lines_S_phase_spec_axes_0 = []
        self.list_lines_S_phase_spec_axes_1 = []

        self.index_channel = (np.array(['CH 1', 'CH 2', 'CH 3']) ==
                              channel).nonzero()[0][0]

        abscissa_spectrogram = self.data_abscissa[self.index_channel]
        ordinate_spectrogram = self.data_ordinate[self.index_channel]
        self.spec_canvas.axes_spectrogram[1].plot(abscissa_spectrogram,
                                                  ordinate_spectrogram)

        signal = {'Action': 'CalculateSpectrogram',
                  'DataX': abscissa_spectrogram,
                  'DataTime': ordinate_spectrogram}
        self.front_to_back_queue.put(signal)

    def plot_spectrogram_data(self, data_freq, data_time, amplitude, frequency):
        color_map = cm.viridis
        self.spec_canvas.axes_spectrogram[
            0].contourf(data_time, data_freq, amplitude,
                        levels=500, cmap=color_map)

        #self.spec_canvas.axes_spectrogram[0].set_ylabel('Frequency [Hz]')
        self.spec_canvas.axes_spectrogram[1].set_xlabel('Time [s]')
        self.spec_canvas.axes_spectrogram[0].set_aspect('auto')
        self.spec_canvas.axes_spectrogram[1].set_aspect('auto')
        self.spec_canvas.axes_spectrogram[0].set_xticks([])
        self.spec_canvas.axes_spectrogram[0].set_xlim(
            [0, len(self.data_abscissa[self.index_channel]) / frequency])
        self.spec_canvas.axes_spectrogram[1].set_xlim(
            [0, len(self.data_abscissa[self.index_channel]) / frequency])
        #plt.xlim([0, len(self.data_abscissa[self.index_channel]) / frequency])

        if self.P_phase_time != 0:
            self.list_lines_P_phase_spec_axes_0 += [
                self.spec_canvas.axes_spectrogram[0].axvline(
                    self.P_phase_time, color='green', picker=True, pickradius=1.5)]
            self.list_lines_P_phase_spec_axes_1 += [
                self.spec_canvas.axes_spectrogram[1].axvline(
                    self.P_phase_time, color='green', picker=True, pickradius=1.5)]

        if self.S_phase_time != 0:
            self.list_lines_S_phase_spec_axes_0 += [
                self.spec_canvas.axes_spectrogram[0].axvline(
                    self.S_phase_time, color='red', picker=True, pickradius=1.5)]
            self.list_lines_S_phase_spec_axes_1 += [
                self.spec_canvas.axes_spectrogram[1].axvline(
                    self.S_phase_time, color='red', picker=True, pickradius=1.5)]

        self.spec_canvas.fig_spectrogram.canvas.draw()

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            if event.key() == Qt.Key_S and self.x_mouse_location is not None:
                self.draw_S_phase()
            elif event.key() == Qt.Key_D and self.x_mouse_location is not None:
                self.draw_P_phase()
            elif event.key() == Qt.Key_E:
                print("Ctrl + E")
                print(self.y_mouse_location)

    def on_click(self, event):
        print(' x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.x, event.y, event.xdata, event.ydata))

    def on_move(self, event):
        self.x_mouse_location = event.xdata
        self.y_mouse_location = event.ydata

    def mouse_press_event(self, event):
        print(event)
        if event.mouseevent.button == 2:
            this_line = event.artist
            value_of_deleted_line = this_line._x[0]
            print(value_of_deleted_line)

            self.delete_phases(value_of_deleted_line)

    def delete_phases(self, value_of_deleted_line):
        value_of_deleted_line = float(value_of_deleted_line)
        if value_of_deleted_line == self.S_phase_time:
            self.S_phase_time = 0
            self.S_QLineEdit.setText(str(self.S_phase_time))
        elif value_of_deleted_line == self.P_phase_time:
            self.P_phase_time = 0
            self.P_QLineEdit.setText(str(self.P_phase_time))

        for i in range(len(self.list_ind_plot)):
            children = self.fig_canvas.axes[self.list_ind_plot[i]]._children
            for j in range(len(children)):
                if isinstance(children[j], matplotlib.lines.Line2D):
                    value_of_child = children[j]._x[0]
                    if value_of_child == value_of_deleted_line:
                        self.fig_canvas.axes[
                            self.list_ind_plot[i]]._children.pop(j)
                        break

        if self.spec_canvas is not None:
            children_spectrogram_axes0 = \
                self.spec_canvas.axes_spectrogram[0]._children
            children_spectrogram_axes1 = \
                self.spec_canvas.axes_spectrogram[1]._children

            for i in range(len(children_spectrogram_axes0)):
                if isinstance(children_spectrogram_axes0[i],
                              matplotlib.lines.Line2D):
                    value_of_child = \
                        children_spectrogram_axes0[i]._x[0]
                    print('value_of_child')
                    print(value_of_child)

                    if value_of_child == value_of_deleted_line:
                        self.spec_canvas.axes_spectrogram[0]._children.pop(i)
                        break

            for i in range(len(children_spectrogram_axes1)):
                if isinstance(children_spectrogram_axes1[i],
                              matplotlib.lines.Line2D):
                    value_of_child = \
                        children_spectrogram_axes1[i]._x[0]
                    print('value_of_child')
                    print(value_of_child)
                    if value_of_child == value_of_deleted_line:
                        self.spec_canvas.axes_spectrogram[1]._children.pop(i)
                        break

            self.spec_canvas.fig_spectrogram.canvas.draw()
        self.fig_canvas.figs.canvas.draw()

    def draw_S_phase(self):
        self.S_phase_time = np.round(self.x_mouse_location, 2)
        self.S_QLineEdit.setText(str(self.S_phase_time))

        if len(self.list_lines_S_phase) != 0:
            for j in range(len(self.list_ind_plot)):
                children = self.fig_canvas.axes[self.list_ind_plot[j]]._children
                for l in range(len(children)):
                    if id(children[l]) == id(self.list_lines_S_phase[j]):
                        self.fig_canvas.axes[
                            self.list_ind_plot[j]]._children.pop(l)
                        break
            self.list_lines_S_phase = []

        for i in range(len(self.list_ind_plot)):
            self.list_lines_S_phase += [
                self.fig_canvas.axes[self.list_ind_plot[i]].axvline(
                    self.S_phase_time, color='red',
                    picker=True, pickradius=1.5)]

        self.fig_canvas.figs.canvas.draw()

        if self.spec_canvas != None:

            if len(self.list_lines_S_phase_spec_axes_0) != 0:
                children_spectrogram_axes0 = self.spec_canvas.axes_spectrogram[0]._children
                for l in range(len(children_spectrogram_axes0)):
                    if id(children_spectrogram_axes0[l]) == \
                            id(self.list_lines_S_phase_spec_axes_0[0]):
                        self.spec_canvas.axes_spectrogram[0]._children.pop(l)
                        break
                self.list_lines_S_phase_spec_axes_0 = []

            self.list_lines_S_phase_spec_axes_0 += [self.spec_canvas.axes_spectrogram[
                0].axvline(self.S_phase_time, color='red',
                           picker=True, pickradius=1.5)]

            if len(self.list_lines_S_phase_spec_axes_1) != 0:
                children_spectrogram_axes1 = self.spec_canvas.axes_spectrogram[1]._children
                for l in range(len(children_spectrogram_axes1)):
                    if id(children_spectrogram_axes1[l]) == \
                            id(self.list_lines_S_phase_spec_axes_1[0]):
                        self.spec_canvas.axes_spectrogram[1]._children.pop(l)
                        break
                self.list_lines_S_phase_spec_axes_1 = []

            self.list_lines_S_phase_spec_axes_1 += [self.spec_canvas.axes_spectrogram[
                1].axvline(self.S_phase_time, color='red',
                           picker=True, pickradius=1.5)]



            self.spec_canvas.fig_spectrogram.canvas.draw()

    def draw_P_phase(self):
        self.P_phase_time = np.round(self.x_mouse_location, 2)
        self.P_QLineEdit.setText(str(self.P_phase_time))

        if len(self.list_lines_P_phase) != 0:
            for j in range(len(self.list_ind_plot)):
                children = self.fig_canvas.axes[self.list_ind_plot[j]]._children
                for l in range(len(children)):
                    if id(children[l]) == id(self.list_lines_P_phase[j]):
                        self.fig_canvas.axes[
                            self.list_ind_plot[j]]._children.pop(l)
                        break
            self.list_lines_P_phase = []

        for i in range(len(self.list_ind_plot)):
            self.list_lines_P_phase += [
                self.fig_canvas.axes[self.list_ind_plot[i]].axvline(
                    self.P_phase_time, color='green',
                    picker=True, pickradius=1.5)]

        self.fig_canvas.figs.canvas.draw()

        if self.spec_canvas != None:
            if len(self.list_lines_P_phase_spec_axes_0) != 0:
                children_spectrogram_axes0 = self.spec_canvas.axes_spectrogram[0]._children
                for l in range(len(children_spectrogram_axes0)):
                    if id(children_spectrogram_axes0[l]) == \
                            id(self.list_lines_P_phase_spec_axes_0[0]):
                        self.spec_canvas.axes_spectrogram[0]._children.pop(l)
                        break
                self.list_lines_P_phase_spec_axes_0 = []

            self.list_lines_P_phase_spec_axes_0 += [self.spec_canvas.axes_spectrogram[
                0].axvline(self.P_phase_time, color='green',
                           picker=True, pickradius=1.5)]

            if len(self.list_lines_P_phase_spec_axes_1) != 0:
                 children_spectrogram_axes1 = self.spec_canvas.axes_spectrogram[1]._children
                 for l in range(len(children_spectrogram_axes1)):
                     if id(children_spectrogram_axes1[l]) == \
                             id(self.list_lines_P_phase_spec_axes_1[0]):
                         self.spec_canvas.axes_spectrogram[1]._children.pop(l)
                         break
                 self.list_lines_P_phase_spec_axes_1 = []

            self.list_lines_P_phase_spec_axes_1 += [self.spec_canvas.axes_spectrogram[
                1].axvline(self.P_phase_time, color='green',
                           picker=True, pickradius=1.5)]

            self.spec_canvas.fig_spectrogram.canvas.draw()

    def change_abscissa_scale(self):
        if self.abscissa_FAS_log:
            self.abscissa_scale.setText('Change X scale to logarithmic')
            self.window_FAS.canvas_FAS.axes_FAS[0].set_xscale('linear')
            self.window_FAS.canvas_FAS.axes_FAS[1].set_xscale('linear')
            self.window_FAS.canvas_FAS.axes_FAS[2].set_xscale('linear')
            self.abscissa_FAS_log = False
        else:
            self.abscissa_scale.setText('Change X scale to linear')
            self.window_FAS.canvas_FAS.axes_FAS[0].set_xscale('log')
            self.window_FAS.canvas_FAS.axes_FAS[1].set_xscale('log')
            self.window_FAS.canvas_FAS.axes_FAS[2].set_xscale('log')
            self.abscissa_FAS_log = True
        self.window_FAS.canvas_FAS.figs_FAS.canvas.draw()

    def change_ordinate_scale(self):
        if self.ordinate_FAS_log:
            self.ordinate_scale.setText('Change Y scale to logarithmic')
            self.window_FAS.canvas_FAS.axes_FAS[0].set_yscale('linear')
            self.window_FAS.canvas_FAS.axes_FAS[1].set_yscale('linear')
            self.window_FAS.canvas_FAS.axes_FAS[2].set_yscale('linear')
            self.ordinate_FAS_log = False
        else:
            self.ordinate_scale.setText('Change Y scale to linear')
            self.window_FAS.canvas_FAS.axes_FAS[0].set_yscale('log')
            self.window_FAS.canvas_FAS.axes_FAS[1].set_yscale('log')
            self.window_FAS.canvas_FAS.axes_FAS[2].set_yscale('log')
            self.ordinate_FAS_log = True
        self.window_FAS.canvas_FAS.figs_FAS.canvas.draw()

    def fig_canvas_grid_on_off(self):
        if self.grid_dummy:
            for i in range(3):
                self.fig_canvas.axes[i].grid(False)
            self.grid_dummy = False
        else:
            for i in range(3):
                self.fig_canvas.axes[i].grid(True)
            self.grid_dummy = True
        self.fig_canvas.figs.canvas.draw()

    def fig_canvas_FAS_grid_on_off(self):
        if self.grid_FAS_dummy:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].grid(False)
            self.grid_FAS_dummy = False
        else:
            for i in range(3):
                self.window_FAS.canvas_FAS.axes_FAS[i].grid(True)
            self.grid_FAS_dummy = True
        self.window_FAS.canvas_FAS.figs_FAS.canvas.draw()