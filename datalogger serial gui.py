__author__ = 'mark-IV-II'
__version__ = '3.0.0-beta'

import tkinter
import os
import json
import webbrowser
import logging
from logging import INFO, WARN
# from icecream import ic
from datetime import datetime
from tkinter import Tk, ttk, messagebox, Menu, PhotoImage, IntVar, StringVar
from tkinter.filedialog import asksaveasfile, askdirectory
from threading import Thread
from serlogger import logger

log_flag = False


class app_class(object):
    def __init__(self, root):

        self.log_level = WARN
        self.logger = self._set_log(self.log_level)

        self.root = root
        self.window = tkinter.Toplevel
        self.button = ttk.Button
        self.label = ttk.Label
        self.combobox = ttk.Combobox
        self.entry = ttk.Entry
        self.dropdown = ttk.OptionMenu

        self.version = f'v{__version__}'
        self.title = 'Serial Datalogger ' + self.version
        try:
            self.icon = PhotoImage(file='icon.png')
        except Exception as e:
            self.logger.warn(f'Error loading logo. {e}')

        self.bgcolour = "#FFFFFF"
        ttk.Style().theme_use('clam')

        self.def_location = self.default_location(self)
        self.help = self.help_window(self)
        self.output_dir = self.def_location.get_location()

        self.slogger = logger(log=True, save_dir=self.output_dir)
        self.main_window = self.main_window(self)

        # for future implementation of scrollable license window
        # self.frame = tkinter.Frame
        # self.scrollbar = ttk.Scrollbar

    def _get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _set_log(self, log_level=INFO):
        global log_flag

        if log_flag:

            self.logger(
                'Logging is already enabled, skipping logger initialisation'
            )

        else:

            ui_logger = logging.getLogger('GUI logger')
            ui_logger.setLevel(log_level)

            fh = logging.FileHandler(filename='ui_error.log', mode='a')
            fh.setLevel(log_level)
            ch = logging.StreamHandler()
            ch.setLevel(log_level)

            formatter1 = logging.Formatter(
                '%(asctime)s: %(name)s - %(levelname)s - %(message)s')
            formatter2 = logging.Formatter(
                '%(name)s: - %(levelname)s - %(message)s')

            # Add formatters
            fh.setFormatter(formatter1)
            ch.setFormatter(formatter2)

            # add the handlers to the logger
            ui_logger.addHandler(fh)
            ui_logger.addHandler(ch)

            log_flag = True

        return ui_logger

    class main_window(object):
        def __init__(self, app_class):

            self.app = app_class
            self.root = self.app.root
            self.bgcolour = self.app.bgcolour
            self.title = self.app.title
            self.icon = self.app.icon
            self.combobox = self.app.combobox
            self.label = self.app.label
            self.button = self.app.button
            self.dropdown = self.app.dropdown
            self.logger = self.app.logger
            self.slogger = self.app.slogger
            # If is_temp is true, explicit saving required
            self.unsaved = self.slogger.is_temp
            self.root.title(self.title)

            try:
                self.root.iconphoto(False, self.icon)
            except Exception as e:
                self.logger.warn(f'{self.get_time()}: Error loading logo. {e}')
            self.root.configure(background=self.bgcolour)

            # Tkinter Integer variable to set timestamp checkbox in menu
            self.timestamp = IntVar()
            # Tkinter Integer variable to set raw mode checkbox in menu
            self.raw_mode_flag = IntVar()
            # Tkinter String variable to set file format
            self.ext = StringVar()

            self.ext_dict = {
                'Text File (.txt)': 'txt',
                'Comma Seperated Values (.csv)': 'csv',
                'JavaScript Object Notation (.json)': 'json'
            }
            self.exts = [*self.ext_dict]

            self.serial_port_selection = None
            self.baud_rate_selection = None
            self.baud_rates = (300, 1200, 2400, 4800, 9600, 19200, 38400,
                               57600, 74880, 115200, 230400)
            self.ports_list = ['No serial ports found']

            self.get_ports()
            self.draw_elements()

            # Mapping Enter key to start function
            self.root.bind('<Return>', self.start)
            # Map close button to quit function to prevent errors while closing
            self.root.protocol("WM_DELETE_WINDOW", self.wquit)

        def draw_elements(self):

            self.set_menubar()

            # Layout properties with weights for responsive UI
            self.root.columnconfigure(0, weight=3, minsize=350)
            self.root.columnconfigure(1, weight=3, minsize=250)
            self.root.rowconfigure(0, weight=2, minsize=80)
            self.root.rowconfigure([1, 2, 5, 7], weight=1, minsize=50)
            self.root.rowconfigure([3, 4, 6], weight=1, minsize=35)

            self.logger.debug(self.ports_list)

            # Label layout properties
            heading_label = self.label(
                text='Fill the below details and click start',
                font=('Verdana', 13),
                background=self.bgcolour)
            heading_label.grid(row=0, columnspan=2)

            format_select_label = self.label(text='Select output file format',
                                             font=('Verdana', 11),
                                             background=self.bgcolour)
            format_select_label.grid(row=1, column=0)

            format_select = self.dropdown(self.root, self.ext, self.exts[0],
                                          *self.exts)
            format_select.grid(row=1, column=1)

            serialport_name_label = self.label(
                text='Select or Enter Serial (or USB) Port name',
                font=('Verdana', 11),
                background=self.bgcolour)
            serialport_name_label.grid(row=2, column=0)

            # Dropdown menu with port names
            self.serial_port_selection = self.combobox(self.root,
                                                       values=self.ports_list,
                                                       font=('Verdana', 10))
            self.serial_port_selection.grid(row=2, column=1)

            baud_rate_label = self.label(text='Select or Enter Baud rate:',
                                         font=('Verdana', 11),
                                         background=self.bgcolour)
            baud_rate_label.grid(row=4, column=0)

            # Text Entry box layout properties
            self.baud_rate_selection = self.combobox(self.root,
                                                     values=self.baud_rates,
                                                     font=('Verdana', 10))
            self.baud_rate_selection.grid(row=4, column=1)

            # Button layout properties
            start_button = self.button(width=18,
                                       text='Start',
                                       command=self.start)
            start_button.grid(row=6, column=1)
            stop_button = self.button(width=10,
                                      text='Stop',
                                      command=self.pause)
            stop_button.grid(row=6, column=0)

        def set_menubar(self):

            # Create menubar to display menu and its options
            menubar = Menu(self.root)
            self.root.config(menu=menubar)

            # File menu
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label='Save As', command=self.save)
            filemenu.add_command(label='Clear', command=self.clear_all_entries)
            filemenu.add_command(label='Quit', command=self.wquit)
            menubar.add_cascade(label='File', menu=filemenu)

            # Options Menu
            options = Menu(menubar, tearoff=0)
            options.add_checkbutton(
                label='Timestamp', variable=self.timestamp
            )
            options.add_checkbutton(
                label="Raw Mode", variable=self.raw_mode_flag
            )
            options.add_command(
                label='Refresh port list', command=self.get_ports
            )
            options.add_command(
                label='Default location',
                command=self.app.def_location.show_window
            )
            options.add_command(label='Help', command=self.app.help.show)
            menubar.add_cascade(label='Options', menu=options)

        def start(self, event=None):

            try:

                # Obtain port number and baud rate info from UI
                port_name = self.serial_port_selection.get()
                baud_rate = self.baud_rate_selection.get()

                # Raise exception for empty or invalid inputs
                if not port_name:
                    raise ValueError('Port name is empty')
                # Exception automatically raised if conversion fails
                baud_rate = int(baud_rate)

                timestamp_status = self.timestamp.get()
                raw_mode = self.raw_mode_flag.get()
                selected_ext = self.ext_dict[self.ext.get()]

                # Set flag to true for starting after its was stopped once
                self.slogger.log = True
                t1 = Thread(
                    target=self.slogger.capture, args=(
                        port_name,
                        baud_rate,
                        timestamp_status,
                        raw_mode,
                        selected_ext
                    )
                )

                if self.slogger.log:
                    t1.start()
                else:
                    t1.join()

            except Exception as e:

                error_message = f'''Please check whether you have entered correct port number or baud rate. {str(e)}'''
                messagebox.showerror('Error ', error_message)
                self.logger.error(error_message)

        # Function to pause running of the logger. Mapped to stop button

        def pause(self):

            self.logger.info('Pausing')
            self.slogger.stop_capture()  # Stop logging
            self.logger.info('All data while paused is not logged')

        # Function to obtain or refresh available port info
        def get_ports(self):

            self.ports_list = self.slogger.find_all_ports()
            self.draw_elements()

        # Function to stop the logging. Sets log flag to false.
        # Mapped to quit menu in menu bar

        def wquit(self):

            self.slogger.stop_capture()  # Stop logging
            if self.unsaved:
                res = messagebox.askyesno(
                    "Log not saved",
                    """The current log is not saved.
                    Would you like to save it before closing?"""
                )
                if res:
                    self.save()
            self.root.destroy()  # Quit self.root tkinter window

        # Function to save data to desired file. Mapped to save in File menu

        def save(self):

            self.pause()

            result_file = asksaveasfile(
                filetypes=[('Text Document', '*.txt'),
                           ('Comma Seperated Values', '*.csv'),
                           ('JavaScript Object Notation', '*.json'),
                           ('All files', '*.*')],
                defaultextension=(
                    'Text Document',
                    '*.txt'))  # Select file name and location through GUI

            self.slogger.save_capture(result_file)

            messagebox.showinfo(
                "File Saved", f"The file has been saved in {result_file.name}")

            self.unsaved = False

            self.clear_all_entries()

        # Function to clear all existing enteries in Entry boxes

        def clear_all_entries(self):

            self.serial_port_selection.delete(0, 'end')
            self.baud_rate_selection.delete(0, 'end')

    class help_window(object):
        def __init__(self, app_class):

            self.app = app_class
            self.root = self.app.root
            self.bgcolour = self.app.bgcolour
            self.title = self.app.title
            self.icon = self.app.icon
            self.label = self.app.label
            self.logger = self.app.logger
            self.window = self.app.window

            lic_lines = [
                f'''Thank you for using Serial Data logger {self.app.version}.
                (C) 2020-2021 mark-IV-II under MIT License'''
            ]

            try:
                with open("LICENSE", "r") as lic_file:
                    lic_lines = lic_file.readlines()
            except Exception as e:
                self.logger.warn(f'{self.get_time()}: Error loading logo. {e}')

            self.about_line = ''.join(lic_lines)
            lines = [
                "The connected device driver must be installed seperately",
                "Press enter key to start",
                "Timestamp feature is disabled by default",
                "For further queries please connect via my github page"
            ]
            self.help_line = ''.join(f'{i}.\n' for i in lines)
            self.source_line = "Source code on Github"
            self.attr_line = "Icons from Thoseicons.com under CC BY 3.0"

        def callback(self, url):

            webbrowser.open_new(url)

        def show(self):

            window = self.window(self.root)
            window.title('Help & About')
            window.configure(background=self.bgcolour)

            try:
                window.iconphoto(True, tkinter.PhotoImage(file='help.png'))
            except Exception as e:
                self.logger.warn(f'Error loading logo. {e}')

            # Layout properties with weights for responsive UI
            window.columnconfigure([0, 1], weight=1, minsize=50)
            window.rowconfigure([0, 1, 2], weight=1, minsize=50)

            # Labels layout
            about_label = self.label(master=window,
                                     text=self.about_line,
                                     background=self.bgcolour,
                                     relief='raised',
                                     font=('Arial 10'))
            about_label.grid(row=0, columnspan=2, padx=15, pady=15)
            # about_label.pack(side=LEFT, fill=X)

            help_label = self.label(window,
                                    text=self.help_line,
                                    background=self.bgcolour,
                                    font=('Arial 11'))
            help_label.grid(row=1, columnspan=2, padx=5, pady=5)

            source_label = self.label(window,
                                      text=self.source_line,
                                      foreground="blue",
                                      cursor="hand2",
                                      background=self.bgcolour,
                                      font=('Arial 11'))
            source_label.bind(
                '<Button-1>', lambda e: self.callback(
                    'https://github.com/mark-IV-II/serial_datalogger'))
            source_label.grid(row=2, column=0, padx=2, pady=2)

            attr_label = self.label(window,
                                    text=self.attr_line,
                                    foreground="blue",
                                    cursor="hand2",
                                    background=self.bgcolour,
                                    font=('Arial 11'))
            attr_label.bind(
                '<Button-1>',
                lambda e: self.callback('https://thoseicons.com/freebies/'))
            attr_label.grid(row=2, column=1, padx=2, pady=2)

    class default_location(object):
        def __init__(self, app_class):

            # self.output_dir = self.get_location()
            self.app = app_class
            self.root = self.app.root
            self.bgcolour = self.app.bgcolour
            self.title = self.app.title
            self.icon = self.app.icon
            self.l_window = None
            self.loc_entry = None
            self.current_loc_label = None
            self.entry = self.app.entry
            self.label = self.app.label
            self.button = self.app.button
            self.logger = self.app.logger

        def select_directory(self):

            self.app.output_dir = askdirectory(initialdir=os.getcwd())
            self.app.slogger.set_out_path(self.app.output_dir)
            self.clear_window()
            self.draw_elements()

        def show_window(self):

            self.l_window = self.app.window(self.root)
            window = self.l_window

            window.title('Set default directory to save')
            window.configure(background=self.bgcolour)
            try:
                window.iconphoto(True, self.icon)
            except Exception as e:
                self.logger.warn(f"Error loading logo: {str(e)}")
            # self.window=window
            self.draw_elements()

        def draw_elements(self):

            window = self.l_window
            # Layout properties with weights for responsive UI
            window.columnconfigure(0, weight=2, minsize=600)
            window.columnconfigure(1, weight=1, minsize=50)
            window.rowconfigure([0, 1, 2], weight=1, minsize=50)

            self.loc_entry = self.entry(master=window, justify='left')
            self.logger.debug(self.app.output_dir)
            self.loc_entry.insert(0, self.app.output_dir)
            self.loc_entry.grid(row=1, column=0)

            get_loc_btn = self.button(master=window,
                                      text='Browse',
                                      command=self.select_directory)
            get_loc_btn.grid(row=1, column=1, padx=15)

            current_loc = f"Current location is {self.app.output_dir}"
            self.current_loc_label = self.label(master=window,
                                                text=current_loc,
                                                font=('Arial', 10),
                                                background=self.bgcolour)
            self.current_loc_label.grid(row=2, column=0)

            ok_btn = self.button(master=window,
                                 text='Save',
                                 command=self.set_location)
            ok_btn.grid(row=2, column=1)

        def get_location(self):

            loc = ''

            try:
                with open('config.json', 'r') as config_file:
                    config = json.load(config_file)
                    loc = config['Default location']
            except Exception as e:
                self.logger.warn(
                    f'Error finding config file: {e}. Using temp folder')

            return loc

        def set_location(self):

            try:
                with open('config.json', 'w') as config_file:
                    config = {'Default location': self.app.output_dir}
                    json.dump(config, config_file)
            except Exception as e:
                self.logger.error(
                    f'Error writing config: {e}. Default location not set')

            finally:
                self.clear_window()
                self.draw_elements()

        def clear_window(self):

            self.loc_entry.delete(0, 'end')
            self.current_loc_label.destroy()


window = Tk()
app = app_class(window).main_window
window.mainloop()
