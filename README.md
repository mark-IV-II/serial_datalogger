# Serial Datalogger

## Summary
This project helps in reading and saving data from a serial port (or USB) connected to an arduino or other similar  boards. The GUI is build using PySide6 module.

Note: The drivers required for the device connected must be installed seperately.

### Screenshots

#### Default theme applied

![Default](https://user-images.githubusercontent.com/58716239/140868950-b121a30a-2ba2-45ac-9881-6bb466733035.png)

#### Custom theme applied
![Custom](https://user-images.githubusercontent.com/58716239/205505993-00e030a3-f67c-421a-a21b-6fd684785143.png)

## Features

* ### Output Console is inside the main window

* ### Output file formats

    Supports three different file formats.
    * Text file - extension `.txt`
    * Comma Seperated Value - extension `.csv`
    * JavaScript Object Notation - extension `.json`

* ### File Menu

    * New file - Save log to a new file. Stops current run. Requires logging to be started again.
    * Save - Save current log file as desired
    * Quit - Quit the app nicely. Will prompt to save file if unsaved.

* ### Options Menu

    * Refresh port list - Refresh and show the serial ports recognised by the OS

* ### Help
    * Help - General help, about and credits regarding the application

* ### Operating System
    * Supports Windows, Linux and MacOSX. Linux and MacOSX support is experimental

* ### Supports different material UI themes
    * Check out <a href='https://material.io/resources/color/#!/?view.left=0&view.right=0'>Theme Editor</a> for custom themes

_[Icons from Thoseicons.com under CC BY 3.0](https://thoseicons.com/freebies/)_

<!-- markdownlint-disable -->

<a href="https://github.com/mark-IV-II/serial_datalogger/blob/tkinter/serlogger.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `Serial Datalogger Module`


---

## <kbd>class</kbd> `logger`
Serial data Logger  class. Variable: log, save_dir. Functions: find_all_ports, capture, save_capture, stop_capture, . 

### <kbd>function</kbd> `__init__`

```python
__init__(log=True, save_dir=None)
```








---

### <kbd>function</kbd> `capture`

```python
capture(
    port_name,
    baud_rate=9600,
    raw_mode=False,
    format_ext='txt',
    timestamp=False,
    decoder='utf-8'
)
```

Capture data coming through serial port of the computer. Arguments include port name, baud rate, raw mode flag, Boolean flag to add timestamp to files, File formats - .txt (default), .csv, .json, Decoder - default utf-8 

---

### <kbd>function</kbd> `find_all_ports`

```python
find_all_ports()
```

Return a list of port names found. OS independent in nature. Unsupported OS raises OSError exception. Support for Linux & MacOS is experimental 

---

### <kbd>function</kbd> `get_default_baud_rates`

```python
get_default_baud_rates() → tuple
```

Return a tuple of predefined baud rates 

---

### <kbd>function</kbd> `get_supported_file_formats`

```python
get_supported_file_formats() → dict
```

Return a dict of supported file types and their extensions 

---

### <kbd>function</kbd> `new_file`

```python
new_file()
```

Create a new file object with new file name 

---

### <kbd>function</kbd> `save_capture`

```python
save_capture(result_file: TextIOWrapper)
```

Save captured data to a desired file. Parameter: result_file - full path to save file 

---

### <kbd>function</kbd> `set_out_path`

```python
set_out_path(new_path: str)
```

Set the output path for saving files. Arguments - new_path 

---

### <kbd>function</kbd> `stop_capture`

```python
stop_capture()
```

Stop execution of serial logger. Sets internal log flag to False 




---

_This part of the documentation was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
