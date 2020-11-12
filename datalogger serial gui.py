import tkinter
from tkinter import Tk, ttk, messagebox, Menu
from tkinter.filedialog import asksaveasfile
from serlogger import logger

VERSION='v2.1.0-beta'
TITLE='Serial Datalogger '+VERSION


#Function to capture data. Mapped to start_button
def start(event=None):
    
    try:
        
        #Obtain port number and baud rate info from UI
        port_name=serial_port_selection.get()
        baud_rate=baud_rate_entry.get()        

        #Raise exception for empty or invalid inputs
        if not port_name: #Check if string is empty or not.If empty raise exception
            raise ValueError('Port name is empty')        
        baud_rate = int(baud_rate) #Exception automatically raised if conversion fails

        #Check whether timstamp option is enabled
        if timestamp.get() == 1:
            slogger.capture(port_name, baud_rate, timestamp=1)
        
        else:
            slogger.capture( port_name, baud_rate, timestamp=0)

        #Set up loop in tkinter
        if slogger.log:
            root.after(0, start)
        
        slogger.log=True #Set flag to true for starting after its was stopped once

    except Exception as e:
        error_message = 'Please check whether you have entered correct port number or baud rate. '+str(e)
        messagebox.showerror(
            'Error ', error_message)
        print(e)


#Function to pause running of the logger. All data while paused is not logged. Mapped to stop button
def pause():

    print('Pausing')
    slogger.log=False #Set flag to false to stop logging temporarily
    print('All data while paused is not logged')

#Function to obtain or refresh available port info
def get_ports():

    global port_list
    port_list=slogger.find_all_ports()
    root.update()


#Function to stop the logging. Sets log flag to false. Mapped to quit menu
def wquit():

    slogger.stop() #Stop logging
    root.destroy() #Quit root tkinter window


#Function to save data to desired file. Mapped to save in File menu
def save():

    result_file = asksaveasfile(filetypes=[(
        'Text Document', '*.txt'), ('All files', '*.*')], defaultextension=('Text Document', '*.txt')) #Select file name and location through GUI

    slogger.save_capture(result_file)

    messagebox.showinfo("File Saved"," The file has been saved")

    clear_all_entries()


#Function to clear all existing enteries in Entry boxes
def clear_all_entries():

    serial_port_selection.delete(0, 'end')
    baud_rate_entry.delete(0, 'end')

#Show help window
def help_window():

    window=tkinter.Toplevel()
    window.title('Help & About')
    window.configure(background="#FFFFFF")

    try:
        p2 = tkinter.PhotoImage(file = 'help.png')
        window.iconphoto(True, p2)
    except: None


    about_line = "Thank you for using Serial Data logger v"+VERSION+"\n(C) 2020 Aditya Anand under MIT License "
    help_line = "The drivers required for the device connected must be installed seperately.\nPress enter key to start.\nTimestamp feature is disabled by default.\nFor further queries please connect via my github page."
    source_line = "Source code : https://github.com/mark-IV-II/serial_datalogger"


    # Layout properties with weights for responsive UI 
    window.columnconfigure(0, weight=1, minsize=50)
    window.rowconfigure([0, 1, 2], weight=1, minsize=50)

    #Labels layout
    about_label = ttk.Label(window, text=about_line, background="#FFFFFF")
    about_label.config(font=('Arial 10'))
    about_label.grid(row=0,column=0,padx=10,pady=10)

    help_label = ttk.Label(window, text=help_line, background="#FFFFFF")
    help_label.config(font=('Arial 9'))
    help_label.grid(row=1,column=0,padx=15,pady=15)
    
    source_label = ttk.Label(window, text=source_line, background="#FFFFFF")
    source_label.config(font=('Arial 9'))
    source_label.grid(row=2,column=0,padx=10,pady=10)



slogger=logger(log=True) #Intiliaze logger

#Tkinter window properties
root = Tk()
root.title(TITLE)
try:
    root.iconphoto(False, tkinter.PhotoImage(file = 'icon.png'))
except: None

#Theme properties
root.configure(background='#FFFFFF')
ttk.Style().theme_use('clam')


timestamp = tkinter.IntVar() #Tkinter Integer variable to set timestamp checkbox in menu
get_ports() #Find all serial ports available in the computer


#Create menubar to display menu and its options
menubar=Menu(root) 
root.config(menu=menubar)

#Keyboard shortcuts for easy operation
root.bind('<Return>',start) #Mapping Enter key to start function


#Layout properties with weights for responsive UI
root.columnconfigure(0, weight=3, minsize=400)
root.rowconfigure(0, weight=2,minsize=80)
root.rowconfigure([1,2,5,7,8], weight=1, minsize=50)
root.rowconfigure([3,4,6], weight=1, minsize=35)

#Dropdown menu with port names
serial_port_selection = ttk.Combobox(root, values=port_list, font=('Verdana', 10))
serial_port_selection.grid(row=2,column=0)

#Label layout properties
heading_label = ttk.Label(
    text='Fill the below details and click start', font=('Verdana', 13), background='#FFFFFF')
heading_label.grid(row=0,column=0)

serialport_name_label = ttk.Label(
    text='Select or Type Serial (or USB) Port name',  font=('Verdana', 11), background='#FFFFFF')
serialport_name_label.grid(row=1,column=0)

baud_rate_label = ttk.Label(text='Enter Baud rate:', font=('Verdana', 11), background='#FFFFFF')
baud_rate_label.grid(row=4,column=0)

#Text Entry box layout properties
baud_rate_entry = ttk.Entry(justify='left', width=8)
baud_rate_entry.grid(row=5,column=0)

#Button layout properties
start_button = ttk.Button(width=18, text='Start', command=start)
start_button.grid(row=7,column=0)
stop_button = ttk.Button(width=10, text='Stop', command=pause)
stop_button.grid(row=8,column=0)

# File menu 
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label='Save', command=save)
filemenu.add_command(label='Clear', command=clear_all_entries)
filemenu.add_command(label='Quit', command=wquit)
menubar.add_cascade(label='File', menu=filemenu)

#Options Menu
options = Menu(menubar, tearoff = 0)
options.add_checkbutton(label='Timestamp', variable=timestamp)
options.add_command(label='Refreh port list', command=slogger.find_all_ports)
options.add_command(label='Help', command=help_window)
menubar.add_cascade(label='Options', menu=options)

root.protocol("WM_DELETE_WINDOW", wquit) #Map close window button to custom quit function to prevent errors while closing
root.mainloop()