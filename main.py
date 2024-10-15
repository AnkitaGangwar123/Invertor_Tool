"""
Updated main.py seperate tables
"""
import sys
from sys import argv
from os import getcwd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,QGroupBox, \
    QTableWidget, QTableWidgetItem,QLabel, QLineEdit, QScrollArea, QGridLayout, QComboBox, QFileDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

from can_data import inverter_data
import time
import datetime

class read_data_worker_1(QThread):
    can_data = pyqtSignal(list)

    def __init__(self, inverter_1):
        super().__init__()
        self.inverter_1 = inverter_1
        self.data_list_1 = []

    def run(self):
        print("Sending commands to set the voltage and current limit of each convertor as required.")
        self.inverter_1.Power_on_all_modules_grid_on()
        self.inverter_1.set_automatic_switching_mode()
        self.inverter_1.discharge_current_limit_mode_grid_on()
        self.inverter_1.discharge_cut_off_voltage()
        self.inverter_1.Power_on_all_modules()
        time.sleep(5)

        while True:
            self.inverter_1.Power_on_all_modules()
            self.data_list_1.append(self.convert_data(self.inverter_1.Module_dc_voltage()))
            self.data_list_1.append(self.convert_data(self.inverter_1.module_dc_current()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_ab_line_voltage()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_bc_line_voltage()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_ca_line_voltage()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_a_phase_current()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_b_phase_current()))
            self.data_list_1.append(self.convert_data(self.inverter_1.ac_c_phase_current()))
            self.data_list_1.append(self.convert_data(self.inverter_1.total_active_power()))
            self.data_list_1.append(self.convert_data(self.inverter_1.module_ambient_temperature()))
            self.can_data.emit(self.data_list_1)

            self.data_list_1 = []
            time.sleep(0.5)

    def convert_data(self, response):
        data = list(response)[4:8]
        hex_ = ''
        for a in data:
            hex_ = hex_+hex(a).lstrip('0x')
        if hex_ == '':
            return 0
        return (int(hex_, 16)/1000)

class read_data_worker_2(QThread):
    can_data = pyqtSignal(list)

    def __init__(self, inverter_2):
        super().__init__()
        self.inverter_2 = inverter_2
        self.data_list_2 = []

    def run(self):
        print("Sending commands to set the voltage and current limit of each convertor as required.")
        self.inverter_2.Power_on_all_modules_grid_on()
        self.inverter_2.set_automatic_switching_mode()
        self.inverter_2.discharge_current_limit_mode_grid_on()
        self.inverter_2.discharge_cut_off_voltage()
        self.inverter_2.Power_on_all_modules()
        time.sleep(5)

        while True:
            self.inverter_2.Power_on_all_modules()
            self.data_list_2.append(self.convert_data(self.inverter_2.Module_dc_voltage()))
            self.data_list_2.append(self.convert_data(self.inverter_2.module_dc_current()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_ab_line_voltage()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_bc_line_voltage()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_ca_line_voltage()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_a_phase_current()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_b_phase_current()))
            self.data_list_2.append(self.convert_data(self.inverter_2.ac_c_phase_current()))
            self.data_list_2.append(self.convert_data(self.inverter_2.total_active_power()))
            self.data_list_2.append(self.convert_data(self.inverter_2.module_ambient_temperature()))
            self.can_data.emit(self.data_list_2)

            self.data_list_2 = []
            time.sleep(0.5)

    def convert_data(self, response):
        data = list(response)[4:8]
        hex_ = ''
        for a in data:
            hex_ = hex_+hex(a).lstrip('0x')
        if hex_ == '':
            return 0
        return (int(hex_, 26)/2000)

class biderectional_ui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bidirectional Converter.")
        self.init_ui()

    def init_ui(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.main_layout = QHBoxLayout()
        self.centralWidget.setLayout(self.main_layout)

        # self.inverter = inverter_data(125000,'00', '0A', '23', '00', 'F0')
        self.inverter = None
        self.result_file = None
        self.data_worker = None

        self.start_comm_btn = QPushButton()
        self.start_comm_btn.setText("Start Communication")
        self.start_comm_btn.setFixedWidth(200)

        self.start_comm_btn.clicked.connect(self.read_data)

        self.main_layout.addWidget(self.convertor_selector)
        self.main_layout.addWidget(self.start_comm_btn)

        self.parameters = ['DC Voltage',
                           'DC Current', 
                           'AC AB Line Voltage', 
                           'AC BC Line Voltage',
                           'AC CA Line Voltage',
                           'A Phase current',
                           'B Phase current',
                           'C Phase current',
                           'Total Active Power',
                           'Temperature']

        self.parameter_table_widget_1 = QTableWidget()
        self.main_layout.addWidget(self.parameter_table_widget_1)
        self.set_table_1()

        self.parameter_table_widget_2 = QTableWidget()
        self.main_layout.addWidget(self.parameter_table_widget_2)
        self.set_table_2()

    def set_table_1(self):
        self.parameter_table_widget_1.setRowCount(5)
        self.parameter_table_widget_1.setColumnCount(5)
        self.parameter_table_widget_1.verticalHeader().setVisible(False)
        self.parameter_table_widget_1.horizontalHeader().setVisible(False)

        self.parameter_table_widget_1.setColumnWidth(1, 75)
        self.parameter_table_widget_1.setColumnWidth(0, 200)
        self.parameter_table_widget_1.setColumnWidth(2, 20)
        self.parameter_table_widget_1.setColumnWidth(3, 200)
        self.parameter_table_widget_1.setColumnWidth(4, 75)
        

        mid = int(len(self.parameters)/2)

        for i in range(0, mid):
            self.parameter_table_widget_1.setItem(i, 0, QTableWidgetItem(self.parameters[i]))
            self.parameter_table_widget_1.setItem(i, 3, QTableWidgetItem(self.parameters[i+mid]))
    
    def set_table_2(self):
        self.parameter_table_widget_2.setRowCount(5)
        self.parameter_table_widget_2.setColumnCount(5)
        self.parameter_table_widget_2.verticalHeader().setVisible(False)
        self.parameter_table_widget_2.horizontalHeader().setVisible(False)

        self.parameter_table_widget_2.setColumnWidth(2, 75)
        self.parameter_table_widget_2.setColumnWidth(0, 200)
        self.parameter_table_widget_2.setColumnWidth(2, 20)
        self.parameter_table_widget_2.setColumnWidth(3, 200)
        self.parameter_table_widget_2.setColumnWidth(4, 75)
        

        mid = int(len(self.parameters)/2)

        for i in range(0, mid):
            self.parameter_table_widget_2.setItem(i, 0, QTableWidgetItem(self.parameters[i]))
            self.parameter_table_widget_2.setItem(i, 3, QTableWidgetItem(self.parameters[i+mid]))

    def read_data(self):
        print("start communication on clicking the push button")

        self.inverter_1 = inverter_data(125000,'00', '0A', '23', '00', 'F0')
        self.inverter_2 = inverter_data(125000,'00', '0A', '23', '01', 'F0')

        # Worker for first invertor
        self.data_worker_1 = read_data_worker_1(self.inverter_1)
        self.data_worker_1.can_data.connect(self.update_table_1)
        self.data_worker_1.start()

        # Worker for second invertor
        self.data_worker_2 = read_data_worker_2(self.inverter_2)
        self.data_worker_2.can_data.connect(self.update_table_2)
        self.data_worker_2.start()


    def update_table_1(self, data):
        mid = int(len(data)/2)
        for i in range(0, mid):
            self.parameter_table_widget_1.setItem(i, 1, QTableWidgetItem(str(data[i])))
            self.parameter_table_widget_1.setItem(i, 4, QTableWidgetItem(str(data[i+mid])))
        
        # if self.result_file:
        #     output_file = open(self.result_file, 'a')
        #     output_file.write(str(datetime.datetime.now()))
        #     output_file.write(" : ")
        #     output_file.write(str(data))
        #     output_file.write("\n")
        #     # output_file.write(str(temp))
        #     output_file.close()
    
    def update_table_2(self, data):
        mid = int(len(data)/2)
        for i in range(0, mid):
            self.parameter_table_widget_2.setItem(i, 1, QTableWidgetItem(str(data[i])))
            self.parameter_table_widget_2.setItem(i, 4, QTableWidgetItem(str(data[i+mid])))
        
        # if self.result_file:
        #     output_file = open(self.result_file, 'a')
        #     output_file.write(str(datetime.datetime.now()))
        #     output_file.write(" : ")
        #     output_file.write(str(data))
        #     output_file.write("\n")
        #     # output_file.write(str(temp))
        #     output_file.close()

def main():
    myApp = QApplication(sys.argv)
    bd_ui = biderectional_ui()
    bd_ui.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
    bd_ui.show()
    sys.exit(myApp.exec_())

if __name__ == "__main__":
    main()