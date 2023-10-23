__author__ = "mark-IV-II"
__version__ = "3.0.0-qt"
__name__ = "Serial Datalogger Module"

from io import TextIOWrapper
import os  # For writing to temp file
import sys  # To identify platform
import time  # To set a wait time
import json
import traceback  # to write to json file
import logging  # for logging to console and file
from logging import DEBUG, INFO, WARN

from serial import Serial  # pip install pyserial

# from icecream import ic
from datetime import datetime  # to save timestamp
from tempfile import gettempdir


class logger:
    """Serial data Logger  class. Variable: log, save_dir.
    Functions: find_all_ports, capture, save_capture, stop_capture, ."""

    # Initialise class parameters
    def __init__(self, log=True, save_dir: "str|None" = None):
        self.mod_logger = logging.getLogger("Module logger")
        self.mod_logger.setLevel(DEBUG)

        fh = logging.FileHandler(filename=f"{__name__} v{__version__}.log", mode="a")
        fh.setLevel(WARN)
        ch = logging.StreamHandler()
        ch.setLevel(INFO)

        formatter1 = logging.Formatter(
            "%(asctime)s: %(name)s - %(levelname)s - %(message)s"
        )
        formatter2 = logging.Formatter("%(levelname)s - %(message)s")

        # Add formatters
        fh.setFormatter(formatter1)
        ch.setFormatter(formatter2)

        # add the handlers to the logger
        self.mod_logger.addHandler(fh)
        self.mod_logger.addHandler(ch)

        # self.mod_logger.basicConfig(level=logging.INFO)

        self.file_name = f"Log-{self._get_time(file=True)}"
        self.json_warn = False
        self.serial_object: serial.Serial  # type: ignore

        self.out_format_select = {
            "txt": self._write_to_txt,
            "csv": self._write_to_csv,
            "json": self._write_to_json,
        }
        self.file_names = {
            "txt": f"{self.file_name}.txt",
            "csv": f"{self.file_name}.csv",
            "json": f"{self.file_name}.json",
        }
        self.full_file_name = ""

        try:
            self.dir_name = os.path.normpath(save_dir)  # type: ignore

            logfile = open(os.path.join(self.dir_name, f"{self.file_name}.temp"), "w")
            self.mod_logger.info(f"File write permissions checked for: {self.dir_name}")
            logfile.close()
            os.remove(logfile.name)
            self.is_temp = False

        except Exception as error:
            self.dir_name = os.path.normpath(gettempdir())
            self.is_temp = True
            self.mod_logger.warning(f"Error setting up given directory: {error}.")
            self.mod_logger.warning("Using temporary directory instead")
            self.mod_logger.debug(self._format_error_trace(error))

    def _format_error_trace(self, error):
        """Format Exception message as a string to have as much info as needed for debugging"""

        return "".join(traceback.format_exception(None, error, error.__traceback__))

    def _get_time(self, file=False):
        """Get current time in required format"""

        if file:
            return datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        else:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_to_txt(self, string, timestamp=0):
        """Write output to a plain text file"""

        self.full_file_name = os.path.join(self.dir_name, self.file_names["txt"])
        self.mod_logger.debug(f"Writing to file {self.full_file_name}")
        if timestamp:
            string = f"{self._get_time()}: {string}"
        with open(self.full_file_name, "a+") as logfile:
            logfile.write(string)
        self.mod_logger.info(string)
        

    def _write_to_csv(self, string, timestamp=0):
        """Write output to a comma seperated file"""

        self.full_file_name = os.path.join(self.dir_name, self.file_names["csv"])
        self.mod_logger.debug(f"Writing to file {self.full_file_name}")
        if timestamp:
            string = f"{self._get_time()},{string}"
        with open(self.full_file_name, "a+") as logfile:
            logfile.write(string)
        self.mod_logger.info(string)

    def _write_to_json(self, string, timestamp=0):
        """Write output to a JSON file.
        Experimental, could be slow or in wrong format in certian situations"""

        self.full_file_name = os.path.join(self.dir_name, self.file_names["json"])
        self.mod_logger.debug(f"Writing to file {self.full_file_name}")

        log_dict = {}
        if not self.json_warn:
            self.mod_logger.warning(
                "Saving to JSON adds timestamp regardless of timestamp flag"
            )
            self.json_warn = True

        log_dict[self._get_time()] = string

        try:
            with open(self.full_file_name, "ab+") as logfile:
                logfile.seek(0, 2)

                if logfile.tell() == 0:
                    json_string = json.dumps([log_dict])
                    logfile.write(json_string.encode())

                else:
                    json_string = json.dumps(log_dict, indent=8)
                    logfile.seek(-1, 2)
                    logfile.truncate()
                    logfile.write(" , ".encode())
                    logfile.write(json_string.encode())
                    logfile.write("]".encode())
            self.mod_logger.info(json_string)

        except Exception as error:
            self.mod_logger.error(f"Error with json file: {error}")
            self.mod_logger.debug(self._format_error_trace(error))

    def set_out_path(self, new_path: str):
        """Set the output path for saving files. Arguments - new_path"""

        self.mod_logger.debug("Setting the output path for saving files")
        self.dir_name = os.path.normpath(new_path)
        self.full_file_name = os.path.join(self.dir_name, self.file_name)
        self.is_temp = False
        self.mod_logger.debug(
            f"The output path for saving files set as {self.full_file_name}"
        )

    def get_supported_file_formats(self) -> dict:
        """Return a dict of supported file types and their extensions"""

        ext_dict = {
            "Text File (.txt)": "txt",
            "Comma Seperated Values (.csv)": "csv",
            "JavaScript Object Notation (.json)": "json",
        }
        return ext_dict

    def init_serial_object(self, **kwargs):
        """Initialize Serial object with given keyword arguments"""

        return Serial(**kwargs)

    def get_default_baud_rates(self) -> tuple:
        """Return a tuple of predefined baud rates"""
        try:
            baud_rates = Serial.BAUDRATES
        except Exception as error:
            baud_rates = (
                "300",
                "1200",
                "2400",
                "4800",
                "9600",
                "19200",
                "38400",
                "57600",
                "74880",
                "115200",
                "230400",
            )
            self.mod_logger.error(f"Error: {str(error)}")
            self.mod_logger.debug(self._format_error_trace(error))

        return baud_rates

    # Function to list all available serial ports
    def find_all_ports(self):
        """Return a list of port names found. OS independent in nature.
        Unsupported OS raises OSError exception.
        Support for Linux & MacOS is experimental"""

        port_list = []  # List to return ports information

        platform_os = sys.platform
        self.mod_logger.debug(f"Current Platform/OS is {platform_os}")

        # Find all ports for Windows
        if platform_os.startswith("win"):
            import serial.tools.list_ports_windows as sertoolswin

            ports = sertoolswin.comports()

        # Find all ports for Linux based OSes
        elif platform_os.startswith("linux") or sys.platform.startswith("cygwin"):
            import serial.tools.list_ports_linux as sertoolslin

            ports = sertoolslin.comports()

        # Find all ports for MacOSX
        elif platform_os.startswith("darwin"):
            import serial.tools.list_ports_osx as sertoolsosx

            ports = sertoolsosx.comports()  # type: ignore

        # Raise exception for unsupported OS
        else:
            self.mod_logger.debug(f"Unsupported Platform/OS {sys.platform}")
            raise OSError("Unsupported Platform/OS")

        # Fill the return list with information found

        if ports:
            self.mod_logger.info("Available ports are:")
            for port, desc, hwid in sorted(ports):
                port_list.append(port)
                self.mod_logger.info(f"{port}: {desc} with id: {hwid}")
        else:
            self.mod_logger.warning(
                "No serial ports detected. Please make sure the device is connected properly"
            )
            port_list.append("No ports found")

        return port_list

    # Main function that captures the data from serial port
    def capture(
        self,
        raw_mode=False,
        timestamp=False,
        format_ext="txt",
        decoder="UTF-8",
        **kwargs,
    ):
        """Capture data coming through serial port of the computer.
        Arguments include raw mode flag,
        Boolean flag to add timestamp to files,
        File formats - txt (default), csv, json,
        Decoder used to convert bytes to string - utf-8 is default

        and all the keyword arguments of serial.Serial class as below

        port: str | None = None,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: float = 1,
        timeout: float | None = None,
        xonxoff: bool = False,
        rtscts: bool = False,
        write_timeout: float | None = None,
        dsrdtr: bool = False,
        inter_byte_timeout: float | None = None,
        exclusive: float | None = None

        Initialize comm port object. If a "port" is given, then the port will be opened immediately. Otherwise a Serial port object in closed state is returned.
        """

        self.mod_logger.info("Capturing")
        self.mod_logger.debug(
            f"Log mode={self.log},{raw_mode},{timestamp},{format_ext},{decoder},{kwargs}"
        )
        # self.mod_logger.debug(f"{self.__dict__}")
        try:
            self.serial_object = self.init_serial_object(**kwargs)

            while self.log:
                self.mod_logger.debug(self.serial_object)

                if raw_mode:
                    self.mod_logger.debug("Calling Read function")
                    line = self.serial_object.read(self.serial_object.in_waiting)
                else:
                    self.mod_logger.debug("Calling Readline function")
                    line = self.serial_object.readline()

                self.mod_logger.debug(f"Decoding line with decoder : {decoder}")
                line = line.decode(decoder)

                # Skip if line is empty
                if line == "":
                    self.mod_logger.debug(f"Skipping line since it is empty")
                    continue

                self.out_format_select[format_ext](string=line, timestamp=timestamp)

                # self.mod_logger.debug(f"{self.__dict__}")

        # Catch exception, print the error and stop logging
        except Exception as error:
            self.mod_logger.error(f"Error: {str(error)}")
            self.log = False  # Set flag to false to stop logging
            self.mod_logger.debug(self._format_error_trace(error))

    def save_capture(self, result_file: TextIOWrapper):
        """Save captured data to a desired file.
        Parameter: result_file - full path to save file"""
        try:

            self.stop_capture()  # Stop logging before saving file

            self.mod_logger.debug(
                f"Copying the contents of the temp file {self.full_file_name} to result file {result_file}"
            )
            with open(self.full_file_name, "rb") as file1:
                with open(result_file, "wb") as file2:  # type: ignore
                    for line in file1:
                        file2.write(line)

            self.file_name = result_file.name
            self.mod_logger.info(f"File {self.file_name} saved")

            self.file_name = f"Log-{self._get_time(file=True)}.txt"
            self.mod_logger.debug(
                f"Opened a new temp file {self.file_name} since old one is closed"
            )
           

        except Exception as error:
            self.mod_logger.error(
                f"{error}. Temp file name: {self.full_file_name}. Output file name: {result_file}"
            )
            self.mod_logger.debug(self._format_error_trace(error))

    def stop_capture(self):
        """Stop execution of serial logger. Sets internal log flag to False"""

        self.mod_logger.info("Stopping. All data while paused is not logged")
        self.log = False  # Set flag to false to stop logging
        time.sleep(1)

        try:
            self.mod_logger.debug(f"Checking if serial connection is open")
            if self.serial_object.is_open:
                self.serial_object.close()
                self.mod_logger.debug(f"Serial connection closed")

        except Exception as error:
            self.mod_logger.error(f"Error while saving file at stop: {str(error)}")
            self.mod_logger.debug(self._format_error_trace(error))

    def new_file(self):
        """Create a new file object with new file name"""
        prev_log_state = self.log
        self.mod_logger.debug(f"Previous log state: {prev_log_state}")
        self.stop_capture()

        self.file_name = f"Log-{self._get_time(file=True)}"
        self.mod_logger.debug(f"New file name generated {self.file_name}")

        self.file_names = {
            "txt": f"{self.file_name}.txt",
            "csv": f"{self.file_name}.csv",
            "json": f"{self.file_name}.json",
        }
        self.mod_logger.debug(f"New file names generated {self.file_names}")

        self.mod_logger.info(
            "New file name generated. Start capturing to save to new file"
        )
        self.log = prev_log_state
        self.mod_logger.debug(f"Previous log state: {prev_log_state}, Current log state {self.log}")
