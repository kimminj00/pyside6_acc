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

class UWB_STATE(Enum):
    Disconnected = auto()
    Connecting = auto()
    Connected = auto()
    end = auto()


TIMER_DATA_INTERVAL = 100
TIMER_PLOT_INTERVAL = 5
TIMER_UWB_CONNTECTION_CHECK_TIME = 1000

UWB_DATA = "<info> app: "
UWB_DATA_X = "x:"
UWB_DATA_Y = "y:"
UWB_DATA_Z = "z:"

def print_debug(*args, **kwargs):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # with open(log_file_name , "a") as f:
    #     print(current_time, end=' ',file=f)
    #     print(*args, **kwargs, file=f)
    print(current_time, end=' ')
    print(*args, **kwargs)


class ACCGraph(QWidget):
    def __init__(self):
        super().__init__()

        self.time_data=[0]
        self.x_data=[0]
        self.y_data=[0]
        self.z_data=[0]

        self.graphWidget= pg.PlotWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.graphWidget)
        self.setLayout(vbox)

        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setMouseEnabled(x=False, y=False)


        self.pdi_x = self.graphWidget.plot(pen='r', name="X Data")
        self.pdi_y = self.graphWidget.plot(pen='g', name="Y Data")
        self.pdi_z = self.graphWidget.plot(pen='b', name="Z Data")
      

    
    def update_plot(self, data, flag, is_checked):
        self.time_data.append(self.time_data[-1]+1)
        if flag==0:
            self.x_data.append(data)
        if flag==1:
            self.y_data.append(data)
        if flag==2:
            self.z_data.append(data)


        if flag==0 and is_checked:
            self.pdi_x.setData(y= self.x_data)
        if flag==1 and is_checked:
            self.pdi_y.setData(y= self.y_data)
        if flag==2 and is_checked:
            self.pdi_z.setData(y= self.z_data)

    def clear_plot(self):
        self.x_data=[0]
        self.y_data=[0]
        self.z_data=[0]
        self.time_data[0]
        self.pdi_x.setData(x=self.time_data, y= self.x_data)
        self.pdi_y.setData(x=self.time_data, y= self.y_data)
        self.pdi_z.setData(x=self.time_data, y= self.z_data)


        
class main_widget(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.serial = QSerialPort()
        self.get_data = []
        self.uwb_status = UWB_STATE.Disconnected

        self.x_checkbox_state=False
        self.y_checkbox_state=False
        self.z_checkbox_state=False

        self.initUI()
        self.timer_data = QTimer()
        self.timer_data.timeout.connect(self.time_data_event)
        self.timer_data.start(TIMER_DATA_INTERVAL)

        self.uwb_connection_check_timer = QTimer()
        self.uwb_connection_check_timer.setSingleShot(True)
        self.uwb_connection_check_timer.timeout.connect(self.timer_uwb_connection_check)
        self.uwb_connection_check_timer.start(TIMER_UWB_CONNTECTION_CHECK_TIME)
    
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
        self.bt_serial_scan = QPushButton("Scan", self)
        self.bt_serial_scan.clicked.connect(self.fillSerialInfo)

        lb_serial_port = QLabel("Serial port", self)
        self.cb_serial_port = QComboBox(self)

        lb_serial_conn = QLabel("Serial connect", self)
        self.bt_serial_conn = QPushButton("Connect", self)
        self.bt_serial_conn.clicked.connect(self.serial_connect)
        self.serial.readyRead.connect(self.read_data)

        lb_clear_plot = QLabel("Clear plot", self)
        bt_clear_plot = QPushButton("Clear plot", self)
        bt_clear_plot.clicked.connect(self.clear_plot)

        lb_uwb_status = QLabel("UWB Status",self)
        self.lb2_uwb_status = QLabel("Disconnected",self)

        grid_layout.addWidget(lb_serial_scan,0,0)
        grid_layout.addWidget(self.bt_serial_scan,0,1)
        grid_layout.addWidget(lb_serial_port,1,0)
        grid_layout.addWidget(self.cb_serial_port,1,1)
        grid_layout.addWidget(lb_serial_conn,2,0)
        grid_layout.addWidget(self.bt_serial_conn,2,1)
        grid_layout.addWidget(lb_clear_plot,3,0)
        grid_layout.addWidget(bt_clear_plot,3,1)
        grid_layout.addWidget(lb_uwb_status,4,0)
        grid_layout.addWidget(self.lb2_uwb_status,4,1)

        vbox.addStretch(1)
        vbox_widget = QWidget()
        vbox_widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        vbox_widget.setLayout(vbox)
        return vbox_widget
    
    def is_checked_state(self):
        if self.checkbox_x.isChecked(): self.x_checkbox_state = True
        if self.checkbox_y.isChecked(): self.y_checkbox_state = True
        if self.checkbox_z.isChecked(): self.z_checkbox_state = True


    def plot_layout(self):

        plot_layout = QVBoxLayout()
        check_layout = QHBoxLayout()
        check_layout.setContentsMargins(0,0,0,0)
        self.checkbox_x = QCheckBox("x 축",self)
        self.checkbox_y = QCheckBox("y 축",self)
        self.checkbox_z = QCheckBox("z 축", self)
        check_layout.addWidget(self.checkbox_x)
        self.checkbox_x.clicked.connect(self.is_checked_state)
        check_layout.addWidget(self.checkbox_y)
        self.checkbox_y.clicked.connect(self.is_checked_state)
        check_layout.addWidget(self.checkbox_z)
        self.checkbox_z.clicked.connect(self.is_checked_state)
        self.checkbox_x.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        self.checkbox_y.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        self.checkbox_z.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
    
        
        self.UWB_ACC = ACCGraph()
        plot_layout.addLayout(check_layout)
        plot_layout.addWidget(self.UWB_ACC)

        plot_layout_widget = QWidget()
        plot_layout_widget.setLayout(plot_layout)

        
        return plot_layout_widget
    
    def fillSerialInfo(self):
        try:
            print_debug("fillSerialInfo")
            port_list = self.getAvailablePort()
            str_len=0
            for str_tmp in port_list:
                if len(str_tmp) > str_len:
                    str_len = len(str_tmp)
            
            portlist = list()
            for port_name in port_list:
                portlist.append(port_name)

            if not self.serial.isOpen():
                self.cb_serial_port.clear()
                self.cb_serial_port.insertItems(0,portlist)
                self.cb_serial_port.view().setFixedWidth(str_len*7)


        except:
            print_debug("fillSerialInfo error")

    def getAvailablePort(self):
        try:
            print_debug("getAvailablePort")
            available_port = list()
            port_path = 'COM'
            index_cnt = 0

            info = QSerialPortInfo.availablePorts()

            for i in info:
                available_port.append(i.portName()+' - '+i.description())
                index_cnt+=1
            
            return available_port

        except:
            print_debug("getAvailablePort error")

    def _open(self,port_name,baudrate=QSerialPort.Baud9600,data_bits=QSerialPort.Data8,flow_control=QSerialPort.NoFlowControl,parity=QSerialPort.NoParity,stop_bits=QSerialPort.OneStop):
        info = QSerialPortInfo(port_name)
        self.serial.setPort(info)
        if not self.serial.setBaudRate(baudrate):
            return False
        self.serial.setDataBits(data_bits)
        self.serial.setFlowControl(flow_control)
        self.serial.setParity(parity)
        self.serial.setStopBits(stop_bits)
        return self.serial.open(QIODevice.ReadWrite)


    def serial_connect(self):
        try:
            print_debug("serial_connect")

            if self.serial.isOpen():
                self.serial.close()
                self.bt_serial_conn.setText('Connect')
            else:
                port = self.cb_serial_port.currentText().split(' ')
                serial_info= {
                    "port_name" : port[0],
                    "baudrate" : QSerialPort.Baud115200,
                    "data_bits" : QSerialPort.Data8,
                    "flow_control" : QSerialPort.NoFlowControl,
                    "parity" : QSerialPort.NoParity,
                    "stop_bits" : QSerialPort.OneStop,
                }
                status = self._open(**serial_info)
                if status:
                    self.serial.setDataTerminalReady(True)
                    self.bt_serial_conn.setText('Close')

        except:
            print_debug("serial_connect error")

    def read_data(self):
        try:
            while self.serial.canReadLine():
                data = self.serial.readLine().data().decode().strip()
                print_debug(data)
                self.get_data.append(data)

        except:
            print_debug("read_data error")


    def time_data_event(self):
        try:
            #print_debug("time_data_event")
            while len(self.get_data):
                data= self.get_data.pop(0)
                if UWB_DATA in data and UWB_DATA_X in data and UWB_DATA_Y in data and UWB_DATA_Z in data:
                    if self.uwb_status!= UWB_STATE.Connected:
                        self.uwb_status = UWB_STATE.Connected
                        self.lb2_uwb_status.setText("Conntected")
                        self.lb2_uwb_status.setStyleSheet("color: green")
                    else:
                        self.uwb_connection_check_timer.stop()
                        self.uwb_connection_check_timer.start()

                    x_aixs=None
                    y_aixs=None
                    z_aixs=None
                    flag=0
                    
                    match= re.search(r"%s(-?\d+)"%UWB_DATA_X, data)
                    if match:
                        x_aixs = int(match.group(1))
                        flag=0
                        self.UWB_ACC.update_plot(x_aixs,flag,self.x_checkbox_state)
                    
                    match= re.search(r"%s(-?\d+)"%UWB_DATA_Y, data)
                    if match:
                        y_aixs= int(match.group(1))
                        flag=1
                        print_debug(y_aixs)
                        self.UWB_ACC.update_plot(y_aixs,flag,self.y_checkbox_state)

                    match= re.search(r"%s(-?\d+)"%UWB_DATA_Z, data)
                    if match:
                        z_aixs= int(match.group(1))
                        flag=2
                        self.UWB_ACC.update_plot(z_aixs,flag,self.z_checkbox_state)


        except:
            print_debug("time_data_event error")

    def timer_uwb_connection_check(self):
        try:
            print_debug("timer_uwb_connection_check")
            if self.uwb_status != UWB_STATE.Disconnected:
                self.uwb_status = UWB_STATE.Disconnected
                self.lb_status_text.setText("Disconnected")
                self.lb_status_text.setStyleSheet("color: red")

        except:
            print_debug("timer_uwb_connection_check error")

    
    def clear_plot(self):
        try:
            self.UWB_ACC.clear_plot()
        except:
            print_debug("clear_plot error")

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