__version__ = "3.2.0-qt"
__author__ = "mark-IV-II"
__appname__ = "Serial Datalogger"

import json
import os
import shutil
import subprocess
from threading import Thread
import traceback
from datetime import datetime

# from PySide6 import QtGui
from serlogger import logger
from queue import Queue
import sys
from PySide6 import QtCore
from PySide6.QtGui import QAction, QFont, QIcon, QTextCursor, QWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from qt_material import apply_stylesheet, QtStyleTools

# from PySide6.QtCore import QFile
# from newui import Ui_MainWindow


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         self.ui = Ui_MainWindow()
#         # layout = QGridLayout()
#         self.ui.setupUi(self)
#         # self.setLayout(layout)


class ConsoleTextEdit(QTextEdit):  # QTextEdit):
    def __init__(self, parent):
        super(ConsoleTextEdit, self).__init__()
        self.setParent(parent)
        self.setReadOnly(True)
        self.flag = False

    @QtCore.Slot(str)
    def append_text(self, text: str):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)


class ThreadConsoleTextQueueReceiver(QtCore.QObject):
    queue_element_received_signal = QtCore.Signal(str)

    def __init__(self, q: Queue, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.queue = q

    @QtCore.Slot()
    def run(self):
        self.queue_element_received_signal.emit(
            f"\t***{__appname__} v{__version__} console started***\n"
        )
        while True:
            text = self.queue.get()
            self.queue_element_received_signal.emit(text)

    @QtCore.Slot()
    def finished(self):
        self.queue_element_received_signal.emit(
            "\t***Serial Datalogger console stopped***\n"
        )


class WriteStream(object):
    def __init__(self, q: Queue):
        self.queue = q

    def write(self, text):
        """
        Redirection of stream to the given queue
        """
        self.queue.put(text)

    def flush(self):
        """
        Stream flush implementation
        """
        # self.thread_queue_listener.stop()
        pass


class appWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self._startup = True
        try:
            self.setWindowIcon(QIcon("icon.png"))
        except FileNotFoundError as file_error:
            print("Icon file not found")
        except Exception as error:
            print(error)
        self._createMenuBar()
        # self._createToolBar()
        self._createStatusBar()
        # create console text queue
        self.queue_console_text = Queue()
        # redirect stdout to the queue
        output_stream = WriteStream(self.queue_console_text)
        sys.stdout = output_stream
        sys.stderr = output_stream

        self.center = QtCore.Qt.AlignCenter
        self.setWindowTitle(f"{__appname__} {__version__}")
        self.resize(800, 450)
        # self.mod_thread = Thread

        self.console_text_edit = ConsoleTextEdit(self)

        self.thread_initialize = QtCore.QThread()

        # create console text read thread + receiver object
        self.thread_queue_listener = QtCore.QThread(parent=self)
        self.console_text_receiver = ThreadConsoleTextQueueReceiver(
            self.queue_console_text
        )
        # connect receiver object to widget for text update
        self.console_text_receiver.queue_element_received_signal.connect(
            self.console_text_edit.append_text
        )
        # attach console text receiver to console text thread
        self.console_text_receiver.moveToThread(self.thread_queue_listener)
        # attach to start / stop methods
        self.thread_queue_listener.started.connect(
            self.console_text_receiver.run)
        self.thread_queue_listener.finished.connect(
            self.console_text_receiver.finished)
        self.thread_queue_listener.start()

        self.slogger = logger()
        self.file_format_dict = self.slogger.get_supported_file_formats()
        self._baud_rates = self.slogger.get_default_baud_rates()
        self.ports_list = self.slogger.find_all_ports()
        self._raw_mode_flag = False
        self._timestamp_flag = False
        self._running = False

        # self.centralwidget = QWidget(MainWindow)
        # self.centralwidget = QWidget(MainWindow)
        # self.centralwidget.setObjectName(u"centralwidget")
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        #  = QWidget(self.centralwidget)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.heading = QLabel()
        self.heading.setObjectName("heading")
        self.gridLayout.addWidget(self.heading, 0, 0, 1, 3)

        self.port_label = QLabel()
        self.port_label.setObjectName("port_label")
        self.gridLayout.addWidget(self.port_label, 1, 0, 1, 1)

        self.baud_label = QLabel()
        self.baud_label.setObjectName("baud_label")
        self.gridLayout.addWidget(self.baud_label, 1, 1, 1, 1)

        self.file_format_label = QLabel()
        self.file_format_label.setObjectName("file_format_label")
        self.gridLayout.addWidget(self.file_format_label, 1, 2, 1, 1)

        self.port_list = QComboBox()
        self.port_list.setObjectName("port_list")
        self.gridLayout.addWidget(self.port_list, 2, 0, 1, 1)
        self.port_list.setEditable(True)
        self.port_list.addItems(self.ports_list)

        self.baud_list = QComboBox()
        self.baud_list.setObjectName("baud_list")
        self.gridLayout.addWidget(self.baud_list, 2, 1, 1, 1)
        self.baud_list.setEditable(True)
        self.baud_list.addItems(self._baud_rates)

        self.file_format_list = QComboBox()
        self.file_format_list.setObjectName("file_format_list")
        self.gridLayout.addWidget(self.file_format_list, 2, 2, 1, 1)
        self.file_format_list.addItems(self.file_format_dict)

        self.stop_btn = QPushButton()
        self.stop_btn.setObjectName("stop_btn")
        self.gridLayout.addWidget(self.stop_btn, 3, 0, 1, 1)
        self.stop_btn.clicked.connect(self.pause)

        self.start_btn = QPushButton()
        self.start_btn.setObjectName("start_btn")
        self.gridLayout.addWidget(self.start_btn, 3, 2, 1, 1)
        self.start_btn.clicked.connect(self.start)

        self.raw_mode_btn = QPushButton()
        self.raw_mode_btn.setObjectName("raw_mode_btn")
        self.gridLayout.addWidget(self.raw_mode_btn, 5, 2, 1, 1)
        self.raw_mode_btn.clicked.connect(self.set_raw_mode)

        self.set_timestamp_btn = QPushButton()
        self.set_timestamp_btn.setObjectName("set_timestamp_btn")
        self.gridLayout.addWidget(self.set_timestamp_btn, 5, 0, 1, 1)
        self.set_timestamp_btn.clicked.connect(self.set_timestamp)

        # self.textEdit = QTextEdit()
        # self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.console_text_edit, 4, 0, 1, 3)

        # self.gridLayout.setColumnMinimumWidth(0, 200)
        # self.gridLayout.setColumnMinimumWidth(1, 200)
        # self.gridLayout.setColumnMinimumWidth(2, 200)

        # self.gridLayout.setRowMinimumHeight(0, 20)
        # self.gridLayout.setRowMinimumHeight(1, 20)
        # self.gridLayout.setRowMinimumHeight(2, 20)
        # self.gridLayout.setRowMinimumHeight(3, 20)
        # self.gridLayout.setRowMinimumHeight(4, 400)

        self.gridLayout.setColumnStretch(0, 10)
        self.gridLayout.setColumnStretch(1, 10)
        self.gridLayout.setColumnStretch(2, 10)

        self.gridLayout.setRowStretch(0, 15)
        self.gridLayout.setRowStretch(1, 15)
        self.gridLayout.setRowStretch(2, 15)
        self.gridLayout.setRowStretch(3, 15)
        self.gridLayout.setRowStretch(4, 300)
        self.gridLayout.setRowStretch(5, 15)

        self.heading.setText("Enter details below and press start")
        self.port_label.setText("Select Serial Port")
        self.baud_label.setText("Enter Baud Rate")
        self.file_format_label.setText("Select output file format")
        self.stop_btn.setText("Stop")
        self.start_btn.setText("Start")
        self.raw_mode_btn.setText("Enable Raw mode")
        self.set_timestamp_btn.setText("Enable Timestamp")

        self.heading.setAlignment(self.center)
        self.port_label.setAlignment(self.center)
        self.baud_label.setAlignment(self.center)
        self.file_format_label.setAlignment(self.center)

        hfont = QFont()
        hfont.setBold(True)
        hfont.setPointSize(16)
        self.heading.setFont(hfont)
        # raise Exception("Testing app try-except")
        self._centralWidget.setLayout(self.gridLayout)

    def _create_new_file(self):

        self.slogger.stop_capture()
        self.slogger.new_file()

        if self._running:
            self.start()

    def _save_file(self):

        result_file = QFileDialog.getSaveFileName(
            self,
            "Save File",
            os.getcwd(),
            """Text Document, (*.txt);;
            Comma Seperated Values, (*.csv);;
            JavaScript Object Notation, (*.json);;
            All files, (*.*)")""",
        )
        # print(result_file)
        self.slogger.save_capture(result_file[0])

    def _exit_app(self):

        # TODO(Fix "QThread: Destroyed while thread is still running" error)
        # tlog = open("thread.log", "a+")
        # print("exiting threads", file=tlog)
        # self.thread_queue_listener.exit()
        # self.thread_initialize.exit()
        # print("quiting threads", file=tlog)
        # self.thread_queue_listener.quit()
        # self.thread_initialize.quit()
        # print("waiting for threads to quit", file=tlog)
        # self.thread_queue_listener.wait()
        # self.thread_initialize.wait()
        # # sleep(2)
        # print("Done waiting, closing app", file=tlog)

        self.thread_initialize.exit()
        self.thread_queue_listener.exit()
        sys.exit()

    def _set_timestamp(self):
        pass

    def _refresh_ports(self):
        self.ports_list = self.slogger.find_all_ports()
        self.port_list.repaint()

    def _show_help(self):
        self._help_window = helpWindow()
        self._help_window.show()

    def _show_config(self):
        self._config_window = configWindow()
        self._config_window.show()

    def _createMenuBar(self):
        menuBar = self.menuBar()

        self.newAction = QAction("&New File", self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.setStatusTip("Create a new file")
        self.newAction.triggered.connect(self._create_new_file)

        self.saveAction = QAction("&Save As", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip("Save the output to a specified file")
        self.saveAction.triggered.connect(self._save_file)

        self.exitAction = QAction("&Quit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip("Quit the app")
        self.exitAction.triggered.connect(self._exit_app)

        self.refreshPortsAction = QAction("&Refresh Ports", self)
        self.refreshPortsAction.setShortcut("Ctrl+R")
        self.refreshPortsAction.setStatusTip("Refresh the list of ports shown")
        self.refreshPortsAction.triggered.connect(self._refresh_ports)

        self.viewConfigAction = QAction("&Settings", self)
        self.viewConfigAction.setShortcut("Ctrl+I")
        self.viewConfigAction.setStatusTip(
            "Change different Settings of the application")
        self.viewConfigAction.triggered.connect(self._show_config)

        self.helpAction = QAction("&Help", self)
        self.helpAction.setShortcut("Ctrl+H")
        self.helpAction.setStatusTip("Learn about the app and its features")
        self.helpAction.triggered.connect(self._show_help)

        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        optionsMenu = menuBar.addMenu("&Options")
        optionsMenu.addAction(self.refreshPortsAction)
        optionsMenu.addAction(self.viewConfigAction)

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpAction)

    def _createStatusBar(self):

        self.status = QStatusBar()
        self.status.showMessage("Click on Help to know more about the app")
        self.setStatusBar(self.status)

    def restart_app(self):
        '''Call a bat/ps1 file to restart the app'''
        # TODO (kill, then start or self exit, then start)
        # subprocess.Popen("")
        pass

    def pause(self):

        self.slogger.stop_capture()  # Stop logging
        self._running = False

    def start(self):

        self._running = True
        port_name = self.port_list.currentText()
        baud_rate = self.baud_list.currentText()
        format_ext = self.file_format_dict[self.file_format_list.currentText()]
        timestamp_status = 0
        raw_mode = self._raw_mode_flag

        self.slogger.log = True

        t1 = Thread(
            target=self.slogger.capture,
            args=(port_name, baud_rate, raw_mode,
                  format_ext, timestamp_status),
        )
        if self.slogger.log:
            t1.start()
        else:
            t1.join()

    def set_raw_mode(self):

        self.slogger.stop_capture()

        if self._raw_mode_flag:
            self._raw_mode_flag = False
            self.raw_mode_btn.setText("Enable Raw Mode")
            self.status.showMessage("Raw mode is disabled")
        else:
            self._raw_mode_flag = True
            self.raw_mode_btn.setText("Disable Raw Mode")
            self.status.showMessage(
                """Raw mode is enabled. This will create formatting issues. Please use text file without timestamps for a clean output"""
            )

        if self._running:
            self.start()

    def set_timestamp(self):

        self.slogger.stop_capture()

        if self._timestamp_flag:
            self.set_timestamp_btn.setText("Enable Timestamp")
            self._timestamp_flag = False
            self.status.showMessage("Timestamps in output file is disabled")
        else:
            self.set_timestamp_btn.setText("Disable Timestamp")
            self._timestamp_flag = True
            self.status.showMessage("Timestamps in output file is enabled")

        if self._running:
            self.start()


class helpWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Help")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)

        try:
            self.setWindowIcon(QIcon("help.png"))
        except FileNotFoundError as file_error:
            print(file_error)
        except Exception as error:
            print(error)

        about_line = QLabel(
            f"""Thank you for using Serial Data logger v{__version__}\n(C) 2020-2022 mark-IV-II under MIT License""")
        hfont = QFont()
        hfont.setBold(True)
        hfont.setPointSize(14)
        about_line.setFont(hfont)
        about_line.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(about_line)

        self.layout.addWidget(
            QLabel("The connected device driver must be installed seperately")
        )
        self.layout.addWidget(
            QLabel("Supports three different file formats (.txt, .csv, .json)")
        )
        self.layout.addWidget(
            QLabel(
                "New file - Save log to a new file. Stops current run. Requires logging to be started again"
            )
        )
        self.layout.addWidget(
            QLabel("Save - Save current log file as desired"))
        self.layout.addWidget(
            QLabel("Clear - Clear all existing entries in the window")
        )
        self.layout.addWidget(
            QLabel("Quit - Quit the app. Will prompt to save file if unsaved")
        )
        self.layout.addWidget(
            QLabel(
                "Timestamp - Add a timestamp to the left of each line being saved. This is off by default"
            )
        )
        self.layout.addWidget(
            QLabel(
                "Raw mode - Read all the bytes from the port without formatting.\nImproves the logging speed, but formatting won't be clean.\nPlease use text file without timestamps for a clean output"
            )
        )
        self.layout.addWidget(
            QLabel(
                "Refresh port list - Refresh and show the serial ports recognised by the OS"
            )
        )
        # self.layout.addWidget(QLabel("Default location - Set the location where all log files will be saved.\nLocation is remembered even if app is closed once set"))
        self.layout.addWidget(
            QLabel("Please feel free raise an issue or pull request on the github")
        )

        source_code_label = QLabel(
            "<a href='https://github.com/mark-IV-II/serial_datalogger/'>Source Code on Github</a>")
        source_code_label.setOpenExternalLinks(True)

        icons_credit_label = QLabel(
            "<a href='https://thoseicons.com/freebies'>Icons from ThoseIcons.com under CC BY 3.0</a>")
        source_code_label.setOpenExternalLinks(True)

        self.layout.addWidget(source_code_label)
        self.layout.addWidget(icons_credit_label)
        self.setLayout(self.layout)

# TODO (Complete configuration page)


class configWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.config_dict = read_config_file()

        self.setWindowTitle("Settings")
        self.hfont = QFont()
        self.hfont.setBold(True)
        self.hfont.setPointSize(14)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.heading = QLabel()
        self.heading.setObjectName("heading")
        self.gridLayout.addWidget(self.heading, 0, 0, 1, 1)
        self.heading.setText("Restart app to apply new theme")

        self.feature_req = QLabel(
            "<a href='https://github.com/mark-IV-II/serial_datalogger/discussions/new?category=ideas'>New Ideas/Features Request</a>")
        self.feature_req.setOpenExternalLinks(True)
        self.gridLayout.addWidget(self.feature_req, 0, 1, 1, 1)

        self.themes_list = QComboBox()
        self.themes_list.setObjectName("theme_list")
        self.gridLayout.addWidget(self.themes_list, 1, 0, 1, 1)
        self.themes_list.setEditable(False)
        self.themes_list.currentIndexChanged.connect(self._update_theme)
        # self.themes_list.addItems(self.themes)

        self.editor_link = QLabel(
            "<a href='https://material.io/resources/color/#!/?view.left=0&view.right=0'>Theme Editor Online</a>")
        self.editor_link.setOpenExternalLinks(True)
        self.gridLayout.addWidget(self.editor_link, 2, 0, 1, 2)

        self.select_custom_theme_btn = QPushButton()
        self.select_custom_theme_btn.setObjectName("select_custom_theme")
        self.gridLayout.addWidget(self.select_custom_theme_btn, 1, 1, 1, 1)
        self.select_custom_theme_btn.clicked.connect(self._select_custom_theme)
        self.select_custom_theme_btn.setText("Select Custom Theme")

        self.save_config_btn = QPushButton()
        self.save_config_btn.setObjectName("save_configuration")
        self.gridLayout.addWidget(self.save_config_btn, 3, 1, 1, 1)
        self.save_config_btn.clicked.connect(self._save_config)
        self.save_config_btn.setText("Save")

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("close_configuration")
        self.gridLayout.addWidget(self.close_btn, 3, 0, 1, 1)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setText("Close")

        self.setLayout(self.gridLayout)
        self._refresh_themes()

    def _select_custom_theme(self):
        '''Load a new theme file to Themes directory'''

        file_name = QFileDialog.getOpenFileName(
            self, 'Select theme file', os.getcwd(), "Theme XML files (*.xml)")
        src_file = file_name[0]

        shutil.copy2(src_file, "./themes/")
        self._refresh_themes()
        print(f"Custom theme {src_file} loaded")

    def _refresh_themes(self):
        '''Retrieve and display available themes'''

        # Select only the name of the file from list of files in the theme directory with XML file extension
        themes = [_.split(".xml")[0] for _ in os.listdir(
            r"./themes/") if _.endswith(r".xml")]
        self.themes_list.clear()
        self.themes_list.addItems(themes)
        self.themes_list.setCurrentText(self.config_dict['theme'])

    def _update_theme(self):

        self.config_dict["theme"] = self.themes_list.currentText()
        

    def _save_config(self):
        '''Save configuration to json or ini file'''
        with open('app_config.json', 'w', encoding='UTF-8') as config_file:
            json.dump(self.config_dict, config_file)

        save_msg = '''\n--/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\--\n\nNew Settings saved successfully\n\n--/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\--\n'''
        print(save_msg)
        self.close()

# class RuntimeStylesheets(QMainWindow, QtStyleTools): TODO(Change theme on runtime)
#     def __init__(self):
#         super().__init__()
#         self.main = QUiLoader().load("main_window.ui", self)


#         self.add_menu_theme(self.main, self.main.menuStyles)

def read_config_file():
    '''Read the app_config.json file, returns default values if not found'''

    config_dict = {"def_dir": '', "theme": 'Default'}
    try:
        with open("app_config.json", "r", encoding="UTF-8") as config_file:
            config_dict = json.load(config_file)

    except FileNotFoundError as file_error:
        print(file_error)

    except Exception as gen_error:
        print(gen_error)

    return config_dict

if __name__ == "__main__":

    log_file_name = f"{__appname__}_v{__version__}.log"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_name, "a+") as log_file:
        print(f"Starting application v{__version__} at {now}", file=log_file)
    
    config = read_config_file()
    theme_path = os.path.join(os.getcwd(),"themes",f"{config['theme']}.xml")


    try:
        app = QApplication(sys.argv)

        window = appWindow()
        apply_stylesheet(app, theme=theme_path,
                         invert_secondary=False)
        window.show()

        sys.exit(app.exec())

    except Exception as error:

        error_trace = "".join(
            traceback.format_exception(None, error, error.__traceback__)
        )
        with open(log_file_name, "a+") as log_file:
            print(f"Error starting application: {error_trace}", file=log_file)

        msg_box = QMessageBox()
        msg_box.setWindowTitle(__appname__)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Error")
        msg_box.setInformativeText(str(error))
        # msg_box.setDetailedText(str(error))

        # layout = QVBoxLayout()
        # message = QLabel("There was an error launching the application")
        # error_message = QLabel(error)
        # msg_box.setWindowModality(QtGui.Qt.ApplicationModal)
        # msg_box.
        # msg_box.resize(400, 200)
        # msg_box.setLayout(layout)
        # layout.addWidget(message)
        # layout.addWidget(error_message)
        # layout.addWidget(QDialogButtonBox.Ok)

        msg_box.exec()
        sys.exit(f"App launch error {error}")
