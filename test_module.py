import os
from serlogger import logger
from datetime import datetime
import json

save_dir = "."
logger = logger(save_dir=save_dir)


def get_time(file=True):
    return "2021-09-11 07-00-00"


def test_get_time():
    assert logger._get_time(file=False) == datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    assert logger._get_time(file=True) == datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def test_new_file():
    logger._get_time = get_time
    logger.new_file()
    assert logger.file_names == {
        "txt": "Log-2021-09-11 07-00-00.txt",
        "csv": "Log-2021-09-11 07-00-00.csv",
        "json": "Log-2021-09-11 07-00-00.json",
    }


def test_write_txt():
    logger._get_time = get_time
    logger.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.txt")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger._write_to_txt(test_line)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[0] == test_line

    logger._write_to_txt(test_line, timestamp=1)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[1] == f"{get_time()}: {test_line}"

    os.remove(filename)


def test_write_csv():
    logger._get_time = get_time
    logger.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.csv")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger._write_to_csv(test_line)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[0] == test_line

    logger._write_to_csv(test_line, timestamp=1)
    with open(filename, "r") as testfile:
        assert testfile.readlines()[1] == f"{get_time()},{test_line}"

    os.remove(filename)


def test_write_json():
    logger._get_time = get_time
    logger.new_file()
    filename = os.path.join(save_dir, "Log-2021-09-11 07-00-00.json")
    test_line = "Lorum ipsum salt\n"

    if os.path.isfile(filename):
        os.remove(filename)

    logger._write_to_json(test_line)
    res = json.load(open(filename, "r"))
    assert res[0]["2021-09-11 07-00-00"] == test_line
    os.remove(filename)


def test_stop_capture():
    logger.log = True
    logger.stop_capture()
    assert not logger.log
