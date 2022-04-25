__author__ = 'mark-IV-II'
__version__ = '2.1.2-tk'
__name__ = "Serial Datalogger Module"


import os  # For writing to temp file
import sys  # To identify platform
import time  # To set a wait time
import json  # to write to json file
import logging  # for logging to console and file
from logging import DEBUG, INFO, WARN
from io import TextIOWrapper
from datetime import datetime  # to save timestamp
from tempfile import gettempdir
import serial  # pip install pyserial
# from icecream import ic



class Logger:
    '''Serial data Logger  class.'''

    def __init__(self, save_dir=None):
        '''Initialise class variables. Accepted arguments are
            log - a flag to set whether to start logging
            save_dir - directory or location to which log files are saved'''

        self.mod_logger = logging.getLogger('Module Logger')
        self.mod_logger.setLevel(DEBUG)

        file_handle = logging.FileHandler(
            filename=f"{__name__} v{__version__}.log", mode='a'
        )
        file_handle.setLevel(WARN)
        console_handle = logging.StreamHandler()
        console_handle.setLevel(INFO)

        formatter1 = logging.Formatter(
            '%(asctime)s: %(name)s - %(levelname)s - %(message)s')
        formatter2 = logging.Formatter(
            '%(name)s: - %(levelname)s - %(message)s')

        # Add formatters
        file_handle.setFormatter(formatter1)
        console_handle.setFormatter(formatter2)

        # add the handlers to the Logger
        self.mod_logger.addHandler(file_handle)
        self.mod_logger.addHandler(console_handle)

        self.file_name = f'Log-{self._get_time(file=True)}'
        self.json_warn = False
        self.serial_data = None

        self.out_format_select = {
            'txt': self._write_to_txt,
            'csv': self._write_to_csv,
            'json': self._write_to_json
        }

        self.file_names = {
            'txt': f'{self.file_name}.txt',
            'csv': f'{self.file_name}.csv',
            'json': f'{self.file_name}.json'
        }
        self.full_file_name = ''

        try:
            self.dir_name = os.path.normpath(save_dir)

            logfile = open(
                os.path.join(self.dir_name, f'{self.file_name}.temp'), "w", encoding='UTF-8'
            )
            self.mod_logger.info(
                f'File write permissions checked for: {self.dir_name}'
            )
            logfile.close()
            os.remove(logfile.name)
            self.is_temp = False

        except Exception as err:
            self.dir_name = os.path.normpath(gettempdir())
            self.is_temp = True
            self.mod_logger.warning(f"Error setting up given directory: {err}.")
            self.mod_logger.warning("Using temporary directory instead")

    def _get_time(self, file=False):
        """Get current time in required format"""

        if file:
            return datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        else:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_to_txt(self, string, timestamp=0):
        """Write output to a plain text file"""

        self.full_file_name = os.path.join(
            self.dir_name, self.file_names['txt']
        )
        if timestamp:
            string = f'{self._get_time()}: {string}'
        with open(self.full_file_name, "a+") as logfile:
            logfile.write(string)
        self.mod_logger.info(string)

    def _write_to_csv(self, string, timestamp=0):
        """Write output to a comma seperated file"""
        self.full_file_name = os.path.join(
            self.dir_name, self.file_names['csv']
        )

        if timestamp:
            string = f'{self._get_time()},{string}'
        with open(self.full_file_name, "a+") as logfile:
            logfile.write(string)
        self.mod_logger.info(string)

    def _write_to_json(self, string, timestamp=0):
        '''Write output to a JSON file.
        Experimental, could be slow or in wrong format in certian situations'''

        self.full_file_name = os.path.join(
            self.dir_name, self.file_names['json']
        )
        log_dict = {}
        if not self.json_warn:
            self.mod_logger.warning(
                'Saving to JSON adds timestamp regardless of timestamp flag'
            )
            self.json_warn = True

        log_dict[self._get_time()] = string

        try:
            with open(self.full_file_name, 'ab+') as logfile:
                logfile.seek(0, 2)

                if logfile.tell() == 0:
                    json_string = json.dumps([log_dict])
                    logfile.write(json_string.encode())

                else:
                    json_string = json.dumps(log_dict, indent=8)
                    logfile.seek(-1, 2)
                    logfile.truncate()
                    logfile.write(' , '.encode())
                    logfile.write(json_string.encode())
                    logfile.write(']'.encode())
            self.mod_logger.info(json_string)

        except Exception as err:
            self.mod_logger.error(f'Error with json file: {err}')

    def set_out_path(self, new_path):
        """Set the output path for saving files. Arguments - new_path"""

        self.dir_name = os.path.normpath(new_path)
        self.full_file_name = os.path.join(self.dir_name, self.file_name)
        self.is_temp = False

    # Function to list all available serial ports
    def find_all_ports(self):
        '''Return a list of port names found. OS independent in nature.
        Unsupported OS raises OSError exception. Linux & MacOS experimental'''

        port_list = []  # List to return ports information

        # Find all ports for Windows
        if sys.platform.startswith('win'):
            import serial.tools.list_ports_windows as sertoolswin
            ports = sertoolswin.comports()

        # Find all ports for Linux based OSes
        elif sys.platform.startswith('linux') or sys.platform.startswith(
                'cygwin'):
            import serial.tools.list_ports_linux as sertoolslin
            ports = sertoolslin.comports()

        # Find all ports for MacOSX
        elif sys.platform.startswith('darwin'):
            import serial.tools.list_ports_osx as sertoolsosx
            ports = sertoolsosx.comports()

        # Raise exception for unsupported OS
        else:
            raise OSError("Unsupported Platform/OS")

        # Fill the return list with information found

        if ports:
            self.mod_logger.info('Available ports are:')
            for port, desc, hwid in sorted(ports):
                port_list.append(port)
                self.mod_logger.info(f"{port}: {desc} with id: {hwid}")
        else:
            self.mod_logger.warning(
                '''No serial ports detected. Please make sure the device is connected properly'''
            )
            port_list.append('No ports found')

        return port_list

    # Main function that captures the data from serial port

    def capture(
            self,
            port_name,
            baud_rate=9600,
            timestamp=0,
            raw_mode=0,
            format_ext='txt',
            decoder='utf-8',
            non_blocking=1):
        '''Capture data coming through serial port of the computer.
        Parameters include port number, baud rate,
        Integer flag to add timestamp to files,
        File formats - .txt (default), .csv, .json,
        Decoder - default utf-8'''

        self.mod_logger.info('Capturing')

        try:

            # Intialise function parameters
            port = str(port_name)
            baud_rate = int(baud_rate)
            data = self.serial_data = serial.Serial(
                port, baud_rate, timeout=.1, rtscts=non_blocking)

            while self.log:
                # ic(self.full_file_name)
                # print('logging') #-- can be used for debugging
                if raw_mode:
                    line = data.read(data.in_waiting)
                else:
                    line = data.readline()

                line = line.decode(decoder)

                # Skip if line is empty
                if line == '':
                    continue

                self.out_format_select[format_ext](
                    string=line, timestamp=timestamp
                )
        # Catch exception, print the error and stop logging
        except Exception as err:

            self.mod_logger.error(f'Error: {str(err)}')
            self.log = False  # Set flag to false to stop logging

    # Function to save the data to a file

    def save_capture(self, result_file: TextIOWrapper):
        '''Save captured data to desired file.
        Parameter: result_file - full path to save file'''

        self.stop_capture()  # Stop logging before saving file

        # Copy the contents of the temp file to result file
        with open(self.full_file_name, 'rb') as file1:
            with open(result_file.name, "wb") as file2:
                for line in file1:
                    file2.write(line)

        self.file_name = result_file.name
        self.mod_logger.info(f'File {self.file_name} saved')
        # Open a new temp file since old one is closed
        self.file_name = f'Log-{self._get_time(file=True)}.txt'

    # Function to stop the logging. Sets log flag to false.

    def stop_capture(self):
        """Stop execution of serial logger. Sets internal log flag to False"""

        self.mod_logger.info("Stopping. All data while paused is not logged")
        self.log = False  # Set flag to false to stop logging
        time.sleep(1)
        try:
            if self.serial_data.is_open:
                self.serial_data.close()
        except Exception as err:
            self.mod_logger.error(
                f"Error while saving file at stop: {str(err)}")

    def new_file(self):
        """Create a new file object with new file name"""
        self.stop_capture()
        self.file_name = f'Log-{self._get_time(file=True)}'
        self.file_names = {
            'txt': f'{self.file_name}.txt',
            'csv': f'{self.file_name}.csv',
            'json': f'{self.file_name}.json'
        }
        self.mod_logger.info(
            "New file name generated. Start capturing to save to new file"
        )
