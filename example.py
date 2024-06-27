import sys
from PySide6.QtCore import Qt,QThread, QIODevice, QDateTime, QCoreApplication, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QTreeWidget, QWidget, QLabel, QLineEdit, QGridLayout, QApplication, QVBoxLayout,QPushButton, QFileDialog, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QSpinBox, QTextBrowser, QSizePolicy, QSplitter, QCheckBox, QDoubleSpinBox, QCompleter, QMessageBox, QColorDialog, QFrame, QMainWindow, QMenu, QTimeEdit, QAbstractItemView, QTreeWidgetItem, QTabWidget, QScrollArea, QInputDialog, QRadioButton, QTextEdit, QGraphicsEllipseItem, QDial
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtGui import QTextCursor, QColor, QKeyEvent, QFont, QPalette, QFontDatabase, QIcon, QKeySequence, QImage, QPainter, QAction
import pyqtgraph as pg
import numpy as np
import time
import os
import re
import math
from enum import Enum, auto
import csv

class main_widget(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.serial = QSerialPort()

        self.initUI()
    
    def initUI(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        self.setLayout(vbox)
        vbox.addWidget(self.total_layout())

    def total_layout(self):
        total_layout = QSplitter(Qt.Vertical)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0,0,0,0)
        top_layout_blank = QWidget()
        top_layout_blank.setLayout(top_layout)
        total_layout.addWidget(top_layout_blank)

        setting_layout_widget = self.setting_layout()
        top_layout.addWidget(setting_layout_widget)
        setting_layout_widget.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0,0,0,0)
        plot_layout_widget = self.plot_layout()
        bottom_layout.addWidget(plot_layout_widget)

        bottom_layout_blank = QWidget()
        bottom_layout_blank.setLayout(bottom_layout)

        total_layout.addWidget(bottom_layout_blank)
        return total_layout

    def setting_layout(self):
        vbox = QVBoxLayout()
        grid_layout = QGridLayout()
        vbox.addLayout(grid_layout)
        lb_serial_scan = QLabel("Serial scan", self)
        bt_serial_scan = QPushButton("Scan", self)
        lb_serial_port = QLabel("Serial port", self)
        self.cb_serial_port = QComboBox(self)
        lb_serial_conn = QLabel("Serial connect", self)
        self.bt_serial_conn = QPushButton("Connect", self)
        lb_clear_plot = QLabel("Clear plot", self)
        self.bt_clear_plot = QPushButton("Clear plot", self)
        lb_uwb_status = QLabel("UWB Status",self)
        self.lb2_uwb_status = QLabel("Disconnected",self)

        

        grid_layout.addWidget(lb_serial_scan,0,0)
        grid_layout.addWidget(bt_serial_scan,0,1)
        grid_layout.addWidget(lb_serial_port,1,0)
        grid_layout.addWidget(self.cb_serial_port,1,1)
        grid_layout.addWidget(lb_serial_conn,2,0)
        grid_layout.addWidget(self.bt_serial_conn,2,1)
        grid_layout.addWidget(lb_clear_plot,3,0)
        grid_layout.addWidget(self.bt_clear_plot,3,1)
        grid_layout.addWidget(lb_uwb_status,4,0)
        grid_layout.addWidget(self.lb2_uwb_status,4,1)

        vbox.addStretch(1)
        vbox_widget = QWidget()
        vbox_widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        vbox_widget.setLayout(vbox)
        return vbox_widget

    def plot_layout(self):
        plot_layout = QVBoxLayout()
        check_layout = QHBoxLayout()
        check_layout.setContentsMargins(0,0,0,0)
        self.checkbox_x = QCheckBox("x 축",self)
        self.checkbox_y = QCheckBox("y 축",self)
        self.checkbox_z = QCheckBox("z 축", self)
        check_layout.addSpacing(150)
        check_layout.addWidget(self.checkbox_x)
        check_layout.addWidget(self.checkbox_y)
        check_layout.addWidget(self.checkbox_z)
    
        
        graphWidget= pg.PlotWidget()
        plot_layout.addLayout(check_layout)
        plot_layout.addWidget(graphWidget)

        plot_layout_widget = QWidget()
        plot_layout_widget.setLayout(plot_layout)

        
        return plot_layout_widget

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.widget = main_widget(self)
        self.setCentralWidget(self.widget)
        menu = self.menuBar()
        menu_main= menu.addMenu("Main")

        menu_main_exit = QAction("Exit", self)
        menu_main_exit.triggered.connect(QCoreApplication.instance().quit)
        menu_main.addAction(menu_main_exit)

        self.setWindowTitle("UWB demo")

        self.resize(800,600)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_view = main_window()
    main_view.show()
    sys.exit(app.exec_())