__author__ = "mark-IV-II"
__version__ = "1.1.0"
__name__ = "Serial Datalogger Module Tester"

import os
import json
from time import sleep
from serlogger import logger
from datetime import datetime
from threading import Thread

import pytest
from pytest_mock import mocker

save_dir = "."


class MockSerial:
    def __init__(self, **kwargs):
        self.in_waiting = True
        self.is_open = True

    def read(self, *args, **kwargs):
        self.in_waiting = False
        return "Hello".encode("UTF-8")

    def readline(self, *args, **kwargs):
        line = "World!\n"
        line_received = self.read().decode("utf-8")
        return f"{line_received} {line}".encode("utf-8")

    def close(self):
        self.is_open = False


@pytest.fixture
def logger_fixture():

    mock_serial_object = MockSerial()
    logger_fix = logger(save_dir=save_dir)
    # Enable logging
    logger_fix.log = True
    logger_fix._get_time = get_time
    logger_fix.serial_object = mock_serial_object
    logger_fix.init_serial_object = init_mock_serial  # type: ignore

    return logger_fix


def init_mock_serial(**kwargs):
    return MockSerial(**kwargs)


def get_time(file=True):
    return "2021-09-11 07-00-00"

def test_get_time():
    logger_fix = logger(save_dir=save_dir)
    # Enable logging
    logger_fix.log = True

    assert logger_fix._get_time(file=False) == datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert logger_fix._get_time(file=True) == datetime.now().strftime(
        "%Y-%m-%d %H-%M-%S"
    )


def test_new_file(logger_fixture):
    logger_fixture.new_file()
    assert logger_fixture.file_names == {
        "txt": "Log-2021-09-11 07-00-00.txt",
        "csv": "Log-2021-09-11 07-00-00.csv",
        "json": "Log-2021-09-11 07-00-00.json",
    }


def test_write_txt(logger_fixture):
    logger_fixture.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.txt")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger_fixture._write_to_txt(test_line)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[0] == test_line

    logger_fixture._write_to_txt(test_line, timestamp=True)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[1] == f"{get_time()}: {test_line}"

    os.remove(filename)


def test_write_csv(logger_fixture):
    logger_fixture.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.csv")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger_fixture._write_to_csv(test_line)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[0] == test_line

    logger_fixture._write_to_csv(test_line, timestamp=True)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[1] == f"{get_time()},{test_line}"

    os.remove(filename)


def test_write_json(logger_fixture):
    logger_fixture.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.json")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger_fixture._write_to_json(test_line)
    res = json.load(open(filename, "r"))
    assert res[0]["2021-09-11 07-00-00"] == test_line
    os.remove(filename)


def test_stop_capture(logger_fixture):
    logger_fixture.stop_capture()
    assert not logger_fixture.log

def test_save_capture(logger_fixture):
    
    test_line = "Lorum ipsum salt\n"
    log_filename = "Log-2021-09-11 07-00-00.txt"
    result_filename = "Final_log.txt"

    if os.path.isfile(log_filename):
        os.remove(log_filename)

    if os.path.isfile(result_filename):
        os.remove(result_filename)

    logger_fixture.new_file()
    logger_fixture._write_to_txt(test_line)
    logger_fixture.save_capture(result_filename)

    with open(result_filename, "r") as testfile:
        assert testfile.readlines()[0] == test_line

    os.remove(log_filename)
    os.remove(result_filename) 

def test_capture_with_mock_serial(logger_fixture):
    raw_mode_flag = True
    timestamp_status = False
    format_ext = "txt"
    port_name = "COM1"
    baud_rate = 9600

    # This done so that filenames are updated with the local get_time method instead of the class's method
    logger_fixture.new_file()

    t1 = Thread(
        target=logger_fixture.capture,
        kwargs={
            "raw_mode": raw_mode_flag,
            "timestamp": timestamp_status,
            "format_ext": format_ext,
            "decoder": "UTF-8",
            "port": port_name,
            "baudrate": baud_rate,
        },
    )

    t1.start()
    sleep(0.1)
    logger_fixture.stop_capture()
    t1.join()

    with open(logger_fixture.full_file_name, "r") as logfile:
        assert "Hello" in logfile.read()

    os.remove(logger_fixture.full_file_name)

    # Re-enable logging
    logger_fixture.log = True

    raw_mode_flag = False

    t2 = Thread(
        target=logger_fixture.capture,
        kwargs={
            "raw_mode": raw_mode_flag,
            "timestamp": timestamp_status,
            "format_ext": format_ext,
            "decoder": "UTF-8",
            "port": port_name,
            "baudrate": baud_rate,
        },
    )

    t2.start()
    sleep(0.1)
    logger_fixture.stop_capture()
    t2.join()

    with open(logger_fixture.full_file_name, "r") as logfile:
        assert "Hello World!\n" in logfile.readlines()

    os.remove(logger_fixture.full_file_name)
