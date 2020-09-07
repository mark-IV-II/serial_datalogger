import os #For writing to temp file
import serial #pip install pyserial
import datetime #to save timestamp
from tempfile import TemporaryDirectory

class logger:
    '''Serial data Logger  class. Variable: log. Functions: capture, save_capture. '''

    #Initialise class parameters
    def __init__(self,log=True):
        self.log=True
        self.tmpdir = TemporaryDirectory()
        self.tmpfle = open(os.path.join(self.tmpdir.name, 'temp.txt'), 'a+') #OS independent file opening


    #Main function that saves the data
    def capture(self, port_num=1, baud_rate=8600, timestamp=1):
        '''Capture data coming through serial port of the computer. The function does not loop itself. Setting up loop in here breaks GUI windows
         Parameters include port number, baud rate and an integer flag to add timestamp to files'''

        #Check whether log in enabled
        if self.log:
            try:

                #Intialise function parameters
                port = 'COM'+str(port_num)
                baud_rate = int(baud_rate)
                data = serial.Serial(port, baud_rate, timeout=.1)

                # print('logging') -- can be used for debugging
                line = data.readline()
                line = line.decode("utf-8")

                #check if data needs to be timestamped
                if timestamp == 1:
                    self.tmpfle.write(str(str(datetime.datetime.now())+': '))

                self.tmpfle.write(line)
                self.tmpfle.write('\n')

                print(line)
                
            #Catch exception, print the error and stop logging
            except Exception as e:

                print('Error'+ str(e))
                self.log=False#Set flag to false to stop logging


    #Function to save the data to a file
    def save_capture(self, result_file):
        '''Save captured data to desired file. Parameter: result_file'''

        self.stop() #Stop logging before saving file

        #Copy the contents of the temp file to result file
        with open(self.tmpfle.name) as f:
            with open(result_file.name, "w") as f1:
                for line in f:
                    f1.write(line)

        print('File '+result_file.name+' saved')
        self.tmpfle = open(os.path.join(self.tmpdir.name, 'temp.txt'), 'w+') #Open a new temp file since old one is closed


    #Function to stop the logging. Sets log flag to false.
    def stop(self):
        '''Stop execution of logger. Temp file closed when called'''

        print('stopping')
        self.log=False #Set flag to false to stop logging
        self.tmpfle.close() #Close the temperory file 


