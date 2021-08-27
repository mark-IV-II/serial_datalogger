# Serial Datalogger

## Summary
This project helps in reading and saving data from a serial port (or USB) connected to an arduino or other similar  boards. The GUI is build using Python's tkinter module. An executable version for Windows Operating System is also added in the releases page

Note: The drivers required for the device connected must be installed seperately. Timestamp feature is disabled by default

Screen shot

![image](https://user-images.githubusercontent.com/58716239/92870856-ecabc680-f421-11ea-8fa2-1cd9b97038f1.png)


## Backend Functions

1. find_all_ports - Return a list of port names found. OS independent in nature. Unsupported OS raises OSError exception.

2. capture - Capture data coming through serial port of the computer. The function does not loop itself. Setting up loop in here breaks GUI windows. Parameters include port number, baud rate and an integer flag to add timestamp to files

3. save_capture - Save captured data to desired file. Parameter: result_file

4. stop - Stop execution of logger. Temp file closed when called