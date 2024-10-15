"""
Updated can_data.py seperate tables
"""
import cantools
from can import Message
from can.interfaces.ixxat import IXXATBus, exceptions
import time
import binascii

class inverter_data:
    def __init__(self, baudrate, error_code, device_num, command, destination_address, source_address):
        # set badurate
        self.baudrate = baudrate
        # set can bus
        self.bus = None
        self.error_code = error_code
        self.device_num = device_num
        self.command = command
        self.destination_address = destination_address
        self.source_address = source_address
        # set can command
        self.can_command = Message(is_extended_id=True,
                                   arbitration_id=0x77F,
                                   dlc=0x07,
                                   data=[0x00, 0x000, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # self.cycle_time = time.time()+5
        self.message = []
        self.can_bus()

    def hex_to_binary(self, hex_num):
        # Convert hex to integer
        decimal_num = int(hex_num, 16)
        # Convert integer to binary and remove the '0b' prefix
        binary_num = bin(decimal_num)[2:]
        # Ensure the binary representation is 4 bits per hex digit
        binary_num = binary_num.zfill(8)
        
        return binary_num
    
    def binary_to_hex(self, binary_num):
        # Convert binary to integer
        decimal_num = int(binary_num, 2)
        # Convert integer to hex and format it to include the '0x' prefix
        hex_num = hex(decimal_num)

        integer_val = int(hex_num, 16)
        a = hex(integer_val)

        return a

    def convert_identifier(self):
        hex_err_code = self.hex_to_binary(self.error_code)
        hex_device_number = self.hex_to_binary(self.device_num)
        hex_command = self.hex_to_binary(self.command)[2:]
        hex_destination_address = self.hex_to_binary(self.destination_address)
        hex_source_address = self.hex_to_binary(self.source_address)
        binary_string = hex_err_code + hex_device_number + hex_command + hex_destination_address + hex_source_address

        # print(self.binary_to_hex(binary_string))
        return self.binary_to_hex(binary_string)

    def can_bus(self):
        # print("I am here")
        self.bus = IXXATBus(channel=0,
                            can_filters=[{"can_id": 0x00, "can_mask": 0x00}],
                            bitrate=self.baudrate)
        
        
    def read_can_message(self):
        self.message = self.bus.recv()
        return(self.message)

    def send_message(self, identifier, data):
        """

        Args:
            identifier ([type]): Identifier for CAN command to be sent.
            data (list): Data to be sent via CAN.
        """
        # identifier = identifier.astype(hex)
        # print(type(identifier))
        if isinstance(identifier, str) and identifier.startswith("0x"):
            identifier = int(identifier, 16)  # Convert from hex string to integer
        
        command = Message(is_extended_id=True,
                          arbitration_id=identifier,
                          dlc=0x08,
                          data=data)
        self.bus.send(command)
        return(self.read_can_message())

    def system_dc_voltage(self):
        """

        Args:
            identifier ([type]): Identifier for CAN command to be  sent.
        """
        identifier = self.convert_identifier()
        data=[0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        response = self.send_message(identifier, data)
        return(response.data)

    def system_dc_current(self):
        """

        Args:
            identifier ([type]): Identifier for CAN command to be  sent.
        """
        identifier = self.convert_identifier()
        data=[0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        response = self.send_message(identifier, data)
        return(response.data)

    def Module_dc_voltage(self):
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 1 :
                flag = 1
                return(response.data)

    def module_dc_current(self):
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 2 :
                flag = 1
                return(response.data)

    def ac_ab_line_voltage(self):
        """AI is creating summary for ac_ab_line_voltage
        """
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 3:
                flag = 1
                return(response.data)
            
    def ac_a_phase_current(self):
        """AI is creating summary for ac_ab_line_voltage
        """
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x21, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 4 :
                flag = 1
                return(response.data)

    def ac_bc_line_voltage(self):
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 4 :
                flag = 1
                return(response.data)
            
    def ac_b_phase_current(self):
        """AI is creating summary for ac_ab_line_voltage
        """
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x21, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 5 :
                flag = 1
                return(response.data)

    def ac_ca_line_voltage(self):
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 5 :
                flag = 1
                return(response.data)
            
    def ac_c_phase_current(self):
        """AI is creating summary for ac_ab_line_voltage
        """
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x21, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 6 :
                flag = 1
                return(response.data)

    def module_ambient_temperature(self):
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x11, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 6 :
                flag = 1
                return(response.data)
            
    def total_active_power(self):
        """AI is creating summary for ac_ab_line_voltage
        """
        # identifier = 0x2A300F0
        identifier = self.convert_identifier()
        data=[0x21, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        flag = 0
        while flag == 0:
            response = self.send_message(identifier, data)
            if list(response.data)[1] == 8 :
                flag = 1
                return(response.data)
            
    def grid_off_inverter_mode(self):
        """
        02 A4 3F F0 21 10 00 00 00 00 00 A2
        """
        identifier = 0x02A43FF0
        data=[0x21, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0xA2]
        self.send_message(identifier, data)

    def discharge_current_limit_mode(self):
        identifier = 0x02A43FF0
        """
        02 A4 3F F0 11 02 00 00 00 011 E 54
        """
        data=[0x11, 0x02, 0x00, 0x00, 0x00, 0x01, 0x1E, 0x54]
        self.send_message(identifier, data)

    def discharge_current_limit_mode_grid_on(self):
        identifier = 0x02A43FF0
        data = [0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0xC3, 0x50]
        self.send_message(identifier, data)

    def discharge_cut_off_voltage(self):
        identifier = 0x02A43FF0
        data=[0x11, 0x32, 0x00, 0x00, 0x00, 0x04, 0x93, 0xE0]
        self.send_message(identifier, data)

    def Power_on_all_modules(self):
        identifier = 0x02A43FF0
        data=[0x11, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0xA0]
        self.send_message(identifier, data)

    def Power_on_all_modules_grid_on(self):
        print("Grid ON")
        identifier = 0x02A43FF0
        data=[0x21, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0xA1]
        self.send_message(identifier, data)

    def set_automatic_switching_mode(self):
        print("Automatic mode")
        identifier = 0x02A43FF0
        data=[0x11, 0x26, 0x00, 0x00, 0x00, 0x00, 0x00, 0xA2]
        self.send_message(identifier, data)