import os
import sys
import serial
import datetime
import tkinter
from tkinter import ttk, messagebox
from tempfile import TemporaryDirectory
from tkinter.filedialog import asksaveasfile


log = True
tmpdir = TemporaryDirectory()
tmpfle = open(os.path.join(tmpdir.name, 'temp.txt'), 'a+')


def start_capture(event=None):

    global log

    try:

        port = 'COM'+str(serialport_number_entry.get())
        baud_rate = int(baud_rate_entry.get())
        data = serial.Serial(port, baud_rate, timeout=.1)

        if log:

            print('logging')
            line = data.readline()
            line = line.decode("utf-8")

            if timestamp.get() == 1:
                tmpfle.write(str(str(datetime.datetime.now())+': '))

            tmpfle.write(line)
            tmpfle.write('\n')

            print(line)
            root.after(0, start_capture)
        log = True

    except:

        messagebox.showerror(
            'Error', 'Please check whether you have entered correct port number or baud rate')


def stop_capture():

    global log
    log = False
    print('stopped')


def save_capture():

    stop_capture()
    tmpfle.close()

    result_file = asksaveasfile(filetypes=[(
        'Text Document', '*.txt'), ('All files', '*.*')], defaultextension=('Text Document', '*.txt'))

    with open(tmpfle.name) as f:
        with open(result_file.name, "w") as f1:
            for line in f:
                f1.write(line)

    sys.exit()


def clear_all_entries():

    serialport_number_entry.delete(0, 'end')
    baud_rate_entry.delete(0, 'end')


root = tkinter.Tk()
timestamp = tkinter.IntVar()
root.title('Serial Datalogger')
app_canvas = tkinter.Canvas(root, width=400, height=300)
app_canvas.pack()

heading_label = ttk.Label(
    text='Fill the below details and click start', font=('Verdana', 14))

serialport_number_label = ttk.Label(
    text='Serial (or USB) Port number - COM:', justify='left')
baud_rate_label = ttk.Label(text='Enter Baud rate:')

serialport_number_entry = ttk.Entry(justify='left', width=5)
baud_rate_entry = ttk.Entry(justify='left', width=10)

timestamp_checkbox = ttk.Checkbutton(
    root, text='Include timestamp', variable=timestamp)

start_button = ttk.Button(width=18, text='Start', command=start_capture)
stop_button = ttk.Button(width=10, text='Stop', command=stop_capture)
stop_save_button = ttk.Button(
    width=15, text='Save and Quit', command=save_capture)
clear_button = ttk.Button(width=10, text='Clear', command=clear_all_entries)

timestamp.set(1)

app_canvas.create_window(200, 50, window=heading_label)
app_canvas.create_window(200, 100, window=serialport_number_label)
app_canvas.create_window(200, 125, window=serialport_number_entry)
app_canvas.create_window(200, 175, window=baud_rate_label)
app_canvas.create_window(200, 200, window=baud_rate_entry)
app_canvas.create_window(200, 225, window=timestamp_checkbox)
app_canvas.create_window(255, 275, window=start_button)
app_canvas.create_window(145, 275, window=stop_button)
app_canvas.create_window(60, 275, window=stop_save_button)
app_canvas.create_window(350, 275, window=clear_button)


root.mainloop()
