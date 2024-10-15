"""
Updated main.py combobox
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

class read_data_worker(QThread):
    can_data = pyqtSignal(list)

    def __init__(self, inverter):
        super().__init__()
        self.inverter = inverter
        self.data_list = []

    def run(self):
        print("Sending commands to set the voltage and current limit of each convertor as required.")
        self.inverter.Power_on_all_modules_grid_on()
        self.inverter.set_automatic_switching_mode()
        self.inverter.discharge_current_limit_mode_grid_on()
        self.inverter.discharge_cut_off_voltage()
        self.inverter.Power_on_all_modules()
        time.sleep(5)

        while True:
            self.inverter.Power_on_all_modules()
            self.data_list.append(self.convert_data(self.inverter.Module_dc_voltage()))
            self.data_list.append(self.convert_data(self.inverter.module_dc_current()))
            self.data_list.append(self.convert_data(self.inverter.ac_ab_line_voltage()))
            self.data_list.append(self.convert_data(self.inverter.ac_bc_line_voltage()))
            self.data_list.append(self.convert_data(self.inverter.ac_ca_line_voltage()))
            self.data_list.append(self.convert_data(self.inverter.ac_a_phase_current()))
            self.data_list.append(self.convert_data(self.inverter.ac_b_phase_current()))
            self.data_list.append(self.convert_data(self.inverter.ac_c_phase_current()))
            self.data_list.append(self.convert_data(self.inverter.total_active_power()))
            self.data_list.append(self.convert_data(self.inverter.module_ambient_temperature()))
            self.can_data.emit(self.data_list)

            self.data_list = []
            time.sleep(0.5)

    def convert_data(self, response):
        data = list(response)[4:8]
        hex_ = ''
        for a in data:
            hex_ = hex_+hex(a).lstrip('0x')
        if hex_ == '':
            return 0
        return (int(hex_, 16)/1000)

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

        # self.start_comm_btn.clicked.connect(self.read_data)

        # Dropdown to select the respective channel to display the respective CAN-data on the UI
        self.convertor_selector = QComboBox()
        self.convertor_selector.addItems(["Convertor", "Convertor_1", "Convertor_2"])
        # Connect the currentIndexChanged signal of the convertor_selector combo box to the switch_depending_on_convertor_selected function
        self.convertor_selector.currentIndexChanged[int].connect(self.switch_depending_on_convertor_selected)

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

        self.parameter_table_widget = QTableWidget()
        self.main_layout.addWidget(self.parameter_table_widget)
        self.set_table()

    def set_table(self):
        self.parameter_table_widget.setRowCount(5)
        self.parameter_table_widget.setColumnCount(5)
        self.parameter_table_widget.verticalHeader().setVisible(False)
        self.parameter_table_widget.horizontalHeader().setVisible(False)

        self.parameter_table_widget.setColumnWidth(1, 75)
        self.parameter_table_widget.setColumnWidth(0, 200)
        self.parameter_table_widget.setColumnWidth(2, 20)
        self.parameter_table_widget.setColumnWidth(3, 200)
        self.parameter_table_widget.setColumnWidth(4, 75)
        

        mid = int(len(self.parameters)/2)

        for i in range(0, mid):
            self.parameter_table_widget.setItem(i, 0, QTableWidgetItem(self.parameters[i]))
            self.parameter_table_widget.setItem(i, 3, QTableWidgetItem(self.parameters[i+mid]))

    def switch_depending_on_convertor_selected(self, index):
        text = self.convertor_selector.itemText(index)

        if self.data_worker:  # Check if a DataWorker is already running
            self.data_worker.quit()  # Quit the current DataWorker
            self.data_worker = None

        if (text == "Convertor_1"):
            print("First convertor selected")
            self.inverter = inverter_data(125000,'00', '0A', '23', '00', 'F0')
            self.result_file = "result_1.txt"
            self.read_data()
        
        elif (text == "Convertor_2"):
            print("Second convertor selected")
            self.inverter = inverter_data(125000,'00', '0A', '23', '01', 'F0')
            self.result_file = "result_2.txt"
            self.read_data()
            
        else:
            print("Invalid convertor selected")
            self.inverter = None
            self.result_file = None

    def read_data(self):
        if self.inverter:
            print("start communication on clicking the push button")
            self.data_worker = read_data_worker(self.inverter)
            self.data_worker.can_data.connect(self.update_table)
            self.data_worker.start()
        else:
            print("No valid convertor selected. Please choose a valid convertor.")

    def update_table(self, data):
        mid = int(len(data)/2)
        for i in range(0, mid):
            self.parameter_table_widget.setItem(i, 1, QTableWidgetItem(str(data[i])))
            self.parameter_table_widget.setItem(i, 4, QTableWidgetItem(str(data[i+mid])))
        
        if self.result_file:
            output_file = open(self.result_file, 'a')
            output_file.write(str(datetime.datetime.now()))
            output_file.write(" : ")
            output_file.write(str(data))
            output_file.write("\n")
            # output_file.write(str(temp))
            output_file.close()

def main():
    myApp = QApplication(sys.argv)
    bd_ui = biderectional_ui()
    bd_ui.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
    bd_ui.show()
    sys.exit(myApp.exec_())

if __name__ == "__main__":
    main()