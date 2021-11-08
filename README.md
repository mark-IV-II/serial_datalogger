# Serial Datalogger

## Summary
This project helps in reading and saving data from a serial port (or USB) connected to an arduino or other similar  boards. The GUI is build using Python's tkinter module. An executable version for Windows Operating System is also added in the releases page

Note: The drivers required for the device connected must be installed seperately.

Screen shot

![image](https://user-images.githubusercontent.com/58716239/140685682-5c6af2dd-8583-4318-b377-0355dfd820d5.png)


<!-- markdownlint-disable -->

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `Serial Datalogger API`


---

## <kbd>class</kbd> `logger`
Serial data Logger  class. 

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(log=True, save_dir=None)
```

Initialise class variables. Accepted arguments are log - a flag to set whether to start logging save_dir - directory or location to which log files are saved 




---

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `capture`

```python
capture(
    port_name,
    baud_rate=9600,
    timestamp=0,
    raw_mode=0,
    format_ext='txt',
    decoder='utf-8'
)
```

Capture data coming through serial port of the computer. Parameters include port number, baud rate, Integer flag to add timestamp to files, File formats - .txt (default), .csv, .json, Decoder - default utf-8 

---

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `find_all_ports`

```python
find_all_ports()
```

Return a list of port names found. OS independent in nature. Unsupported OS raises OSError exception. Linux & MacOS experimental 

---

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L255"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `save_capture`

```python
save_capture(result_file: TextIOWrapper)
```

Save captured data to desired file. Parameter: result_file - full path to save file 

---

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `set_out_path`

```python
set_out_path(new_path)
```

Set the output path for saving files. Arguments - new_path 

---

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/v3.0.0/serlogger.py#L274"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `stop_capture`

```python
stop_capture()
```

Stop execution of serial logger. Sets internal log flag to False 




---

_The documentation was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._