import pyvisa as visa
from pyvisa import constants
import time
from datetime import datetime
import pandas as pd
import matplotlib
import numpy as np
import random
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.rcParams['animation.html'] = 'jshtml'
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib import style
LARGE_FONT = ('Verdana', 12)
style.use('ggplot')
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk
import threading
import multiprocessing as mp
from csv import writer
import re
import os

#Check if everything connected properly
rm = visa.ResourceManager()
list_of_devices = rm.list_resources()

temp = rm.open_resource('ASRL3::INSTR', baud_rate = 115200, 
                        data_bits = 8, parity = constants.VI_ASRL_PAR_NONE,
                        stop_bits = constants.VI_ASRL_STOP_ONE, 
                        flow_control = constants.VI_ASRL_FLOW_NONE,
                        write_termination = '\r', read_termination = '\r')


#Write command to a device and get it's output
def get(device, command):
    #return np.round(np.random.random(1), 1)
    return device.query(command)

print(get(temp, 'IDN?'))

print(rm.list_resources(), '\n')

def var2str(var, vars_data = locals()):
    return [var_name for var_name in vars_data if id(var) == id(vars_data[var_name])][0]

#assigning variables for sweeping

device_to_sweep1 = 'Time'
device_to_sweep2 = 'Time'
device_to_sweep3 = 'Time'
parameter_to_sweep1 = ''
parameter_to_sweep2 = ''
parameter_to_sweep3 = ''
min_sweep1 = 0 
max_sweep1 = 0 
ratio_sweep1 = 1
delay_factor1 = 0
min_sweep2 = 0 
max_sweep2 = 0 
ratio_sweep2 = 1
delay_factor2 = 0
min_sweep3 = 0 
max_sweep3 = 0 
ratio_sweep3 = 1
delay_factor3 = 0
filename_sweep =  r'C:\NUS\Transport lab\Test\data_files\sweep' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv'
sweeper_flag1 = False
sweeper_flag2 = False
sweeper_flag3 = False

manual_sweep_flags = [0]
manual_filenames = [r'C:\NUS\Transport lab\Test\data_files\manual' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv']
columns = []

#variables for plotting

x1 = []
x1_status = 0
y1 = []
y1_status = 0
x2 = []
x2_status = 0
y2 = []
y2_status = 0
x3 = []
x3_status = 0
y3 = []
y3_status = 0
x4 = []
x4_status = 0
y4 = []
y4_status = 0
z4 = [[]]
z4_status = 0

class lock_in():
    
    def __init__(self, adress = 'GPIB0::3::INSTR'):
        
        self.sr830 = rm.open_resource(adress, write_termination= '\n', read_termination='\n')
        
        self.modes_ch1_options = ['X', 'R', 'X noise', 'AUX in 1', 'AUX in 2']
        
        self.modes_ch2_options = ['Y', 'Θ', 'Y noise', 'AUX in 3', 'AUX in 4']
        
        self.sensitivity_options = ['2 nV/fA', '5 nV/fA', '10 nV/fA', 
                                    '20 nV/fA', '50 nV/fA', '100 nV/fA', 
                                    '200 nV/fA', '500 nV/fA', '1 μV/pA', 
                                    '2 μV/pA', '5 μV/pA', '10 μV/pA',
                                    '20 μV/pA', '50 μV/pA', '100 μV/pA', 
                                    '200 μV/pA', '500 μV/pA',
                                    '1 mV/nA', '2 mV/nA', '5 mV/nA', '10 mV/nA',
                                    '20 mV/nA', '50 mV/nA', '100 mV/nA',  
                                    '200 mV/nA', '500 mV/nA', '1 V/μA']
        
        self.time_constant_options = ['10 μs', '30 μs', '100 μs',
                                      '300 μs', '1 ms', '3 ms',
                                      '10 ms', '30 ms', '100 ms',
                                      '300 ms', '1 s', '3 s',
                                      '10 s', '30 s', '100 s',
                                      '300 s', '1 ks', '3 ks',
                                      '10 ks', '30 ks']
        
        self.low_pass_filter_slope_options = ['6 dB/oct', '12 dB/oct',
                                              '18 dB/oct', '24 dB/oct']
        
        self.synchronous_filter_status_options = ['On', 'Off']
        
        self.remote_status_options = ['lock', 'Unlock']
        
        self.set_options = ['amplitude', 'frequency', 'phase', 'AUX1_output', 'AUX2_output', 'AUX3_output', 'AUX4_output']
    
        self.get_options = ['x', 'y', 'r', 'Θ', 'ch1', 'ch2', 'AUX1_input', 'AUX2_input', 'AUX3_input', 'AUX4_input']
        
    def IDN(self):
        answer = get(self.sr830, '*IDN?')
        return answer
    
    def x(self):
        try:
            answer = float(get(self.sr830, 'OUTP?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?1'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?1'))
        return answer
        
    def y(self):
        try:
            answer = float(get(self.sr830, 'OUTP?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?2'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?2'))
        return answer
    
    def r(self):
        try:
            answer = float(get(self.sr830, 'OUTP?3'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?3'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?3'))
        return answer
    
    def Θ(self):
        try:
            answer = float(get(self.sr830, 'OUTP?4'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?4'))
        return answer
    
    def frequency(self):
        try:
            answer = float(get(self.sr830, 'FREQ?'))
        except ValueError:
            answer = float(get(self.sr830, 'FREQ?'))
        return answer
    
    def phase(self):
        try:
            answer = float(get(self.sr830, 'PHAS?'))
        except ValueError:
            answer = float(get(self.sr830, 'PHAS?'))
        return answer
        
    def amplitude(self):
        try:
            answer = float(get(self.sr830, 'SLVL?'))
        except ValueError:
            answer = float(get(self.sr830, 'SLVL?'))
        return answer
    
    def sensitivity(self):
        try:
            answer = float(get(self.sr830, 'SENS?'))
        except ValueError:
            answer = float(get(self.sr830, 'SENS?'))
        return answer
    
    def time_constant(self):
        try:
            answer = int(get(self.sr830, 'OFLT?'))
        except ValueError:
            answer = int(get(self.sr830, 'OFLT?'))
        return answer
    
    def low_pass_filter_slope(self):
        try:
            answer = int(get(self.sr830, 'OFSL?'))
        except ValueError:
            answer = int(get(self.sr830, 'OFSL?'))
        return answer
    
    def synchronous_filter_status(self):
        try:
            answer = int(get(self.sr830, 'SYNC?'))
        except ValueError:
            answer = int(get(self.sr830, 'SYNC?'))
        return answer
    
    def remote(self):
        try:
            answer = int(get(self.sr830, 'OVRM?'))
        except ValueError:
            answer = int(get(self.sr830, 'OVRM?'))
        return answer
    
    def ch1(self):
        try:
            answer = float(get(self.sr830, 'OUTR?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTR?1'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTR?1'))
        return answer
    
    def ch2(self):
        try:
            answer = float(get(self.sr830, 'OUTR?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTR?2'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTR?2'))
        return answer
        
    def parameter(self):
        dataframe = pd.DataFrame({'Sensitivity': [self.sensitivity()], 
                             'Time_constant': [self.time_constant()],
                             'Low_pass_filter_slope': [self.low_pass_filter_slope()], 
                             'Synchronous_filter_status': [self.synchronous_filter_status()],
                             'Remote': [self.remote()],
                             'Amplitude': [self.amplitude()], 
                             'Frequency': [self.frequency()],
                             'Phase': [self.phase()]})
        return dataframe
    
    def channels(self):
        dataframe = pd.DataFrame({'Ch1': [self.ch1()], 'Ch2': [self.ch2()]})
        return dataframe
        
    def data(self):
        try:
            return [time.process_time() - zero_time, self.x, self.y]
        except:
            pass
        #return [time.process_time() - zero_time, float(np.random.randint(10)), float(np.random.randint(10))]
    
    def AUX1_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?1'))
        return answer
    
    def AUX2_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?2'))
        return answer
    
    def AUX3_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?3'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?3'))
        return answer
    
    def AUX4_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?4'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?4'))
        return answer
    
    def set_ch1_mode(self, mode = 0):
        line = 'DDEF1,' + str(mode) + ',0'
        self.sr830.write(line)
        
    def set_ch2_mode(self, mode = 0):
        line = 'DDEF2,' + str(mode) + ',0'
        self.sr830.write(line)
        
    def set_frequency(self, value = 30.0):
        line = 'FREQ' + str(value)
        self.sr830.write(line)    
        
    def set_phase(self, value = 0.0):
        line = 'PHAS' + str(value)
        self.sr830.write(line) 
        
    def set_amplitude(self, value = 0.5):
        line = 'SLVL' + str(value)
        self.sr830.write(line) 
    
    def set_sensitivity(self, mode = 24):
        line = 'SENS' + str(mode)
        self.sr830.write(line)
        
    def set_time_constant(self, mode = 19):
        line = 'OFLT' + str(mode)
        self.sr830.write(line)
        
    def set_low_pass_filter_slope(self, mode = 3):
        line = 'OFSL' + str(mode)
        self.sr830.write(line)
        
    def set_synchronous_filter_status(self, mode = 0):
        line = 'SYNC' + str(mode)
        self.sr830.write(line)
        
    def set_remote(self, mode = 1):
        line = 'OVRM' + str(mode)
        self.sr830.write(line)
        
    def set_AUX1_output(self, value = 0):
        line = 'AUXV1,' + str(value)
        self.sr830.write(line)
        
    def set_AUX2_output(self, value = 0):
        line = 'AUXV2,' + str(value)
        self.sr830.write(line)
        
    def set_AUX3_output(self, value = 0):
        line = 'AUXV3,' + str(value)
        self.sr830.write(line)
        
    def set_AUX4_output(self, value = 0):
        line = 'AUXV4,' + str(value)
        self.sr830.write(line)
        
        
class TC300():
    
    def __init__(self, adress = 'ASRL3::INSTR'):
        self.tc = rm.open_resource(adress, baud_rate = 115200, 
                                data_bits = 8, parity = constants.VI_ASRL_PAR_NONE,
                                stop_bits = constants.VI_ASRL_STOP_ONE, 
                                flow_control = constants.VI_ASRL_FLOW_NONE,
                                write_termination = '\r', read_termination = '\r')
        
        self.set_options = ['T1', 'T2']
        
        self.get_options = ['T1', 'T2']
        
    def IDN(self):
        return(get(self.tc, 'IDN?')[2:])
         
    def T1(self):
        #Get the CH1 target temperature; returned value is the actual temperature in °C
        value_str = get(self.tc, 'TACT1?')
        value_float = re.findall(r'\d*\.\d+|\d+', value_str)
        try:
            value_float = [float(i) for i in value_float][0]
        except IndexError:
            value_str = get(self.tc, 'TACT1?')
            value_float = re.findall(r'\d*\.\d+|\d+', value_str)
            value_float = [float(i) for i in value_float][0]
        return value_float
    
    def set_T1(self, value = 20):
        #Set the CH1 target temperature to value/10 °C, the range is defined by 
        #TMIN1 and TMAX1, the setting resolution of value is 1. 
        self.tc.write('TSET1=' + str(int(value * 10)))
        self.tc.write('EN1=1')
    
    def set_T1_min(self, t1_min = 0):
        #Set the CH1 Target Temperature Min value, 
        #(Range: -200 to TMAX1°C, with a resolution of 1°C). 
        self.tc.write('TMIN1=' + str(t1_min))
        
    def set_T1_max(self, t1_max = 30):
        #Set the CH1 Target Temperature Max value, n equals value 
        #TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t1_max))
    
    def T2(self):
        #Get the CH2 target temperature; returned value is the actual temperature in °C
        value_str = get(self.tc, 'TACT2?')
        if value_str == '':
            value_str = get(self.tc, 'TACT2?')
        value_float = re.findall(r'\d*\.\d+|\d+', value_str)
        value_float = [float(i) for i in value_float]
        return(value_float[0])
    
    def set_T2(self, value = 20):
        #Set the CH2 target temperature to value/10 °C, the range is defined by 
        #TMIN1 and TMAX1, the setting resolution of value is 1. 
        self.tc.write('TSET2=' + str(int(value * 10)))
        self.tc.write('EN2=1')
    
    def set_T2_min(self, t2_min = 0):
        #Set the CH2 Target Temperature Min value, 
        #(Range: -200 to TMAX2°C, with a resolution of 1°C). 
        self.tc.write('TMIN1=' + str(t2_min))
        
    def set_T2_max(self, t2_max = 20):
        #Set the CH2 Target Temperature Max value, n equals value 
        #TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t2_max))

device_classes = (lock_in, TC300)

def devices_list():
    #queries each device IDN?
    list_of_devices = []
    types_of_devices = []
    for adress in rm.list_resources():
        try:
            try:
                name = get(rm.open_resource(adress, read_termination = '\r'), 'IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                list_of_devices.append(name)
                if name == '':
                    raise UserWarning        
            except UserWarning:
                name = get(rm.open_resource(adress, read_termination = '\n'), 'IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                list_of_devices.append(name)
        except visa.errors.VisaIOError: 
            try:
                name = get(rm.open_resource(adress, read_termination = '\n'), '*IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                list_of_devices.append(name)
                if name == '':
                    raise UserWarning  
            except UserWarning:
                name = get(rm.open_resource(adress, read_termination = '\r'), '*IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                list_of_devices.append(name)
                
        for class_of_device in device_classes:
            if globals()[var2str(class_of_device)]().IDN() == name:
                types_of_devices.append(var2str(class_of_device))
        if len(types_of_devices) != len(list_of_devices):
            types_of_devices.append('Not a class')
            
    return list_of_devices, types_of_devices

names_of_devices, types_of_devices = devices_list()

print(names_of_devices, types_of_devices)

parameters_to_read = []

for device_type in types_of_devices:
    if device_type == 'Not a class':
        pass
    else:
        adress = list_of_devices[types_of_devices.index(device_type)]
        get_options = getattr(globals()[device_type](adress = adress), 'get_options')
        for option in get_options:
            parameters_to_read.append(adress + '.' + option)

zero_time = time.process_time()

config_parameters_filename = r'C:\NUS\Transport lab\App\config\parameters_' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv' '.csv'

config_parameters = pd.DataFrame(columns = ['Sensitivity', 'Time_constant', 
                                 'Low_pass_filter_slope', 'Synchronous_filter_status',
                                 'Remote', 'Amplitude', 'Frequency', 
                                 'Phase'])

config_parameters.to_csv(config_parameters_filename, index = False)

config_channels_filename = r'C:\NUS\Transport lab\App\config\channels_' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv' '.csv'

config_channels = pd.DataFrame(columns = ['Ch1', 'Ch2'])

config_channels.to_csv(config_channels_filename, index = False)

class write_config_parameters(threading.Thread):

    def __init__(self, adress = 'GPIB0::3::INSTR'):
        threading.Thread.__init__(self)
        self.adress = adress
        self.daemon = True
        self.start()

    def run(self):
        while True:
            dataframe_parameters = lock_in(adress = self.adress).parameter()
            with open(config_parameters_filename, 'a') as f_object:
                try:
                    # Pass this file object to csv.writer()
                    # and get a writer object
                    writer_object = writer(f_object)
      
                    # Pass the list as an argument into
                    # the writerow()
                    writer_object.writerow(*dataframe_parameters.values)
                    time.sleep(5)
                  
                    #Close the file object
                    f_object.close()
                except KeyboardInterrupt():
                    f_object.close()
                    
class write_config_channels(threading.Thread):

    def __init__(self, adress = 'GPIB0::3::INSTR'):
        threading.Thread.__init__(self)
        self.adress = adress
        self.daemon = True
        self.start()

    def run(self):
        while True:
            dataframe_channels = lock_in(adress = self.adress).channels()
            with open(config_channels_filename, 'a') as f_object:
                try:
                    writer_object = writer(f_object)
                    writer_object.writerow(*dataframe_channels.values)
                    time.sleep(0.3)
                  
                    #Close the file object
                    f_object.close()
                except:
                    f_object.close()

zero_time = time.process_time()

class Universal_frontend(tk.Tk):
    
    def __init__(self, classes, start, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.iconbitmap(self)
        tk.Tk.wm_title(self, 'Lock in test')
        
        container = tk.Frame(self)
        container.pack(side = 'top', fill = 'both', expand = 'True')
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}
        
        for F in classes:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')
        
        self.show_frame(start)
        
        tk.Tk.quit(self)
        tk.Tk.mainloop(self)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = 'Start Page', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        lock_in_settings_button = ttk.Button(self, text = "Lock in settings", command = lambda: controller.show_frame(Lock_in_settings))
        lock_in_settings_button.place(relx = 0.1, rely = 0.1)
        
        sweeper1d_button = ttk.Button(self, text = '1D - sweeper', command = lambda: controller.show_frame(Sweeper1d))
        sweeper1d_button.place(relx = 0.1, rely = 0.4)
        
        sweeper2d_button = ttk.Button(self, text = '2D - sweeper', command = lambda: controller.show_frame(Sweeper2d))
        sweeper2d_button.place(relx = 0.2, rely = 0.4)
        
        sweeper3d_button = ttk.Button(self, text = '3D - sweeper', command = lambda: controller.show_frame(Sweeper3d))
        sweeper3d_button.place(relx = 0.3, rely = 0.4)
        
class Lock_in_settings(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text = 'Lock in settings', font = LARGE_FONT)
        label.place(relx = 0.485, rely = 0.02)
        
        label_time_constant = tk.Label(self, text = 'Time constant')
        label_time_constant.place(relx = 0.02, rely = 0.015)
        
        self.combo_time_constant = ttk.Combobox(self,
                                        value = lock_in().time_constant_options)
        self.combo_time_constant.current(8)
        self.combo_time_constant.bind("<<ComboboxSelected>>", self.set_time_constant)
        self.combo_time_constant.place(relx = 0.02, rely = 0.05)
        
        self.value_time_constant = tk.StringVar(value = '0.0')
        self.label_value_time_constant = tk.Label(self, text = (self.value_time_constant.get()))
        self.label_value_time_constant.place(relx = 0.02, rely = 0.085)
        
        label_low_pass_filter_slope = tk.Label(self, text = 'Low pass filter slope')
        label_low_pass_filter_slope.place(relx = 0.02, rely = 0.125)
        
        self.combo_low_pass_filter_slope = ttk.Combobox(self, 
                                        value = lock_in().low_pass_filter_slope_options)
        self.combo_low_pass_filter_slope.current(1)
        self.combo_low_pass_filter_slope.bind("<<ComboboxSelected>>", self.set_low_pass_filter_slope)
        self.combo_low_pass_filter_slope.place(relx = 0.02, rely = 0.160)
        
        self.value_low_pass_filter_slope = tk.StringVar(value = '0.0')
        self.label_value_low_pass_filter_slope = tk.Label(self, text = (self.value_low_pass_filter_slope.get()))
        self.label_value_low_pass_filter_slope.place(relx = 0.02, rely = 0.195)
        
        label_synchronous_filter_status = tk.Label(self, text = 'Synchronous filter status')
        label_synchronous_filter_status.place(relx = 0.02, rely = 0.235)        
        
        self.combo_synchronous_filter_status = ttk.Combobox(self, 
                                        value = lock_in().synchronous_filter_status_options)
        self.combo_synchronous_filter_status.current(0)
        self.combo_synchronous_filter_status.bind("<<ComboboxSelected>>", self.set_synchronous_filter_status)
        self.combo_synchronous_filter_status.place(relx = 0.02, rely = 0.270)
        
        self.value_synchronous_filter_status = tk.StringVar(value = '0.0')
        self.label_value_synchronous_filter_status = tk.Label(self, text = (self.value_synchronous_filter_status.get()))
        self.label_value_synchronous_filter_status.place(relx = 0.02, rely = 0.305)
        
        label_aux_rule = tk.Label(self, text = 'AUX output voltage \n -10.5 < V < 10.5')
        label_aux_rule.place(relx = 0.02, rely = 0.4)
        
        label_aux1_voltage = tk.Label(self, text = 'AUX1 output')
        label_aux1_voltage.place(relx = 0.02, rely = 0.45)
        
        self.aux1_initial = tk.StringVar(value = '0')
        
        entry_aux1_voltage = tk.Entry(self, textvariable = self.aux1_initial)
        entry_aux1_voltage.place(relx = 0.02, rely = 0.485)
        
        label_aux2_voltage = tk.Label(self, text = 'AUX2 output')
        label_aux2_voltage.place(relx = 0.02, rely = 0.515)
        
        self.aux2_initial = tk.StringVar(value = '0')
        
        entry_aux2_voltage = tk.Entry(self, textvariable = self.aux2_initial)
        entry_aux2_voltage.place(relx = 0.02, rely = 0.550)
        
        label_aux3_voltage = tk.Label(self, text = 'AUX3 output')
        label_aux3_voltage.place(relx = 0.02, rely = 0.580)
        
        self.aux3_initial = tk.StringVar(value = '0')
        
        entry_aux3_voltage = tk.Entry(self, textvariable = self.aux3_initial)
        entry_aux3_voltage.place(relx = 0.02, rely = 0.615)
        
        label_aux4_voltage = tk.Label(self, text = 'AUX4 output')
        label_aux4_voltage.place(relx = 0.02, rely = 0.645)
        
        self.aux4_initial = tk.StringVar(value = '0')
        
        entry_aux4_voltage = tk.Entry(self, textvariable = self.aux4_initial)
        entry_aux4_voltage.place(relx = 0.02, rely = 0.680)
        
        button_aux_voltage = ttk.Button(self, text = 'Set AUX voltage', 
                                        command = self.aux_button_clicked)
        button_aux_voltage.place(relx = 0.15, rely = 0.675)
        
        label_sensitivity = tk.Label(self, text = 'Sensitivity')
        label_sensitivity.place(relx = 0.15, rely = 0.015)
        
        self.combo_sensitivity = ttk.Combobox(self, value = lock_in().sensitivity_options)
        self.combo_sensitivity.current(15)
        self.combo_sensitivity.bind("<<ComboboxSelected>>", self.set_sensitivity)
        self.combo_sensitivity.place(relx = 0.15, rely = 0.05)
        
        self.value_sensitivity = tk.StringVar(value = '0.0')
        self.label_value_sensitivity = tk.Label(self, text = (self.value_sensitivity.get()))
        self.label_value_sensitivity.place(relx = 0.15, rely = 0.085)
        
        label_remote = tk.Label(self, text = 'Display locking')
        label_remote.place(relx = 0.15, rely = 0.125)        

        self.combo_remote = ttk.Combobox(self, value = lock_in().remote_status_options)
        self.combo_remote.current(1)
        self.combo_remote.bind("<<ComboboxSelected>>", self.set_remote)
        self.combo_remote.place(relx = 0.15, rely = 0.160)
        
        self.value_remote = tk.StringVar(value = '0.0')
        self.label_value_remote = tk.Label(self, text = (self.value_remote.get()))
        self.label_value_remote.place(relx = 0.15, rely = 0.195)
        
        self.value_ch1 = tk.StringVar(value = '0.0')
        self.label_value_ch1 = tk.Label(self, text = ('\n' + self.value_ch1.get()), font = ('Arial', 16))
        self.label_value_ch1.place(relx = 0.15, rely = 0.3)
        
        self.combo_ch1 = ttk.Combobox(self, value = lock_in().modes_ch1_options)
        self.combo_ch1.current(0)
        self.combo_ch1.bind("<<ComboboxSelected>>", self.set_ch1_mode)
        self.combo_ch1.place(relx = 0.15, rely = 0.4)
         
        self.value_ch2 = tk.StringVar(value = '0.0')
        self.label_value_ch2 = tk.Label(self, text = ('\n' + self.value_ch1.get()), font = ('Arial', 16))
        self.label_value_ch2.place(relx = 0.3, rely = 0.3)
        
        self.combo_ch2 = ttk.Combobox(self, value = lock_in().modes_ch2_options)
        self.combo_ch2.current(0)
        self.combo_ch2.bind("<<ComboboxSelected>>", self.set_ch2_mode)
        self.combo_ch2.place(relx = 0.3, rely = 0.4)
        
        label_amplitude = tk.Label(self, text = 'Amplitude of SIN output, V. \n 0.004 < V < 5.000')
        label_amplitude.place(relx = 0.485, rely = 0.315)
        
        self.amplitude_initial = tk.StringVar(value = '0.5')
        
        entry_amplitude = tk.Entry(self, textvariable = self.amplitude_initial)
        entry_amplitude.place(relx = 0.5, rely = 0.4)
        
        self.value_amplitude = tk.StringVar(value = '0.0')
        self.label_value_amplitude = tk.Label(self, text = (self.value_amplitude.get()))
        self.label_value_amplitude.place(relx = 0.5, rely = 0.435)
        
        label_frequency = tk.Label(self, text = 'Frequency, Hz. \n 0.001 < Hz < 102000')
        label_frequency.place(relx = 0.65, rely = 0.315)
        
        self.frequency_initial = tk.StringVar(value = '30.0')
        
        entry_frequency = tk.Entry(self, textvariable = self.frequency_initial)
        entry_frequency.place(relx = 0.65, rely = 0.4)
        
        self.value_frequency = tk.StringVar(value = '0.0')
        self.label_value_frequency = tk.Label(self, text = (self.value_frequency.get()))
        self.label_value_frequency.place(relx = 0.65, rely = 0.435)
        
        label_phase = tk.Label(self, text = 'Phase shift, deg. \n -360.00 < deg < 729.99')
        label_phase.place(relx = 0.8, rely = 0.315)
        
        self.phase_initial = tk.StringVar(value = '0.0')
        
        entry_phase = tk.Entry(self, textvariable = self.phase_initial)
        entry_phase.place(relx = 0.8, rely = 0.4)
        
        self.value_phase = tk.StringVar(value = '0.0')
        self.label_value_phase = tk.Label(self, text = (self.value_phase.get()))
        self.label_value_phase.place(relx = 0.8, rely = 0.435)
        
        button_reference = ttk.Button(self, text = 'Set reference parameters', 
                                        command = self.reference_button_clicked)
        button_reference.place(relx = 0.8, rely = 0.485)
        
        '''
        units = tk.StringVar()
        units.set(r'X Y R Θ CH1 CH2 AUX1 AUX2 AUX3 AUX4')
        label_listbox = tk.Label(self, textvariable = 'Units to collect \n in datafile')
        label_listbox.place(relx = 0.5, rely = 0.5)
        lstbox = tk.Listbox(self, listvariable = units, 
                            selectmode = 'multiple', width=20, height=10)
        lstbox.place(relx = 0.5, rely = 0.55)
        def select():
            reslist = list()
            seleccion = lstbox.curselection()
            for i in seleccion:
                entrada = lstbox.get(i)
                reslist.append(entrada)
            for val in reslist:
                print(val)
        button_listbox = ttk.Button(self, text = "Collect data", command = select)
        button_listbox.place(relx = 0.615, rely = 0.665)
        '''
        thread_update_sensitivity = threading.Thread(target = self.update_sensitivity())
        thread_update_time_constant = threading.Thread(target = self.update_time_constant())
        thread_update_low_pass_filter_slope = threading.Thread(target = self.update_low_pass_filter_slope())
        thread_update_synchronous_filter_status = threading.Thread(target = self.update_synchronous_filter_status())
        thread_update_remote = threading.Thread(target = self.update_remote())
        thread_update_amplitude = threading.Thread(target = self.update_amplitude())
        thread_update_phase = threading.Thread(target = self.update_phase())
        thread_update_frequency = threading.Thread(target = self.update_frequency())
        thread_update_ch1 = threading.Thread(target = self.update_value_ch1())
        thread_update_ch2 = threading.Thread(target = self.update_value_ch2())
        
        thread_update_sensitivity.start()
        thread_update_time_constant.start() 
        thread_update_low_pass_filter_slope.start()
        thread_update_synchronous_filter_status.start() 
        thread_update_remote.start()
        thread_update_amplitude.start()
        thread_update_phase.start() 
        thread_update_frequency.start() 
        thread_update_ch1.start()
        thread_update_ch2.start()
        
        thread_update_sensitivity.join()
        thread_update_time_constant.join() 
        thread_update_low_pass_filter_slope.join()
        thread_update_synchronous_filter_status.join() 
        thread_update_remote.join()
        thread_update_amplitude.join()
        thread_update_phase.join() 
        thread_update_frequency.join() 
        thread_update_ch1.join()
        thread_update_ch2.join()
        
        button_back_home  = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button_back_home.place(relx = 0.85, rely = 0.85)
        
    def set_sensitivity(self, event):
        lock_in().set_sensitivity(mode = int(self.combo_sensitivity.current()))
        
    def set_time_constant(self, event):
        lock_in().set_time_constant(mode = int(self.combo_time_constant.current()))
        
    def set_low_pass_filter_slope(self, event):
        lock_in().set_low_pass_filter_slope(
            mode = int(self.combo_low_pass_filter_slope.current()))
    
    def set_synchronous_filter_status(self, event):
        lock_in().set_synchronous_filter_status(
            mode = int(self.combo_synchronous_filter_status.current()))
     
    def set_ch1_mode(self, event):
        lock_in().set_ch1_mode(mode = int(self.combo_ch1.current()))
    
    def set_ch2_mode(self, event):
        lock_in().set_ch2_mode(mode = int(self.combo_ch2.current()))
    
    def set_remote(self, event):
        lock_in().set_remote(mode = int(self.combo_remote.current()))
        
    def aux_button_clicked(self):
        lock_in().set_AUX1_output(value = float(self.aux1_initial.get()))
        lock_in().set_AUX2_output(value = float(self.aux2_initial.get()))
        lock_in().set_AUX3_output(value = float(self.aux3_initial.get()))
        lock_in().set_AUX4_output(value = float(self.aux4_initial.get()))
        
    def reference_button_clicked(self):
        lock_in().set_frequency(value = float(self.frequency_initial.get()))
        lock_in().set_phase(value = float(self.phase_initial.get()))
        lock_in().set_amplitude(value = float(self.amplitude_initial.get()))
        
    def update_time_constant(self, interval = 2987):     
        
        try:
            value = pd.read_csv(config_parameters_filename)['Time_constant'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_time_constant['text'] = str(lock_in().time_constant_options[int(value)])
        self.label_value_time_constant.after(interval, self.update_time_constant)
       
    def update_sensitivity(self, interval = 2989):
    
        try:
            value = pd.read_csv(config_parameters_filename)['Sensitivity'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_sensitivity['text'] = str(lock_in().sensitivity_options[int(value)])
        self.label_value_sensitivity.after(interval, self.update_sensitivity)
        
    def update_low_pass_filter_slope(self, interval = 2991):
        
        try:
            value = pd.read_csv(config_parameters_filename)['Low_pass_filter_slope'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_low_pass_filter_slope['text'] = str(lock_in().low_pass_filter_slope_options[int(value)])
        self.label_value_low_pass_filter_slope.after(interval, self.update_low_pass_filter_slope)
        
    def update_synchronous_filter_status(self, interval = 2993):
        
        try:
            value = pd.read_csv(config_parameters_filename)['Synchronous_filter_status'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_synchronous_filter_status['text'] = str(lock_in().synchronous_filter_status_options[int(value)])
        self.label_value_synchronous_filter_status.after(interval, self.update_synchronous_filter_status)
        
    def update_remote(self, interval = 2995): 

        try:
            value = pd.read_csv(config_parameters_filename)['Remote'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_remote['text'] = str(lock_in().remote_status_options[int(value)])
        self.label_value_remote.after(interval, self.update_remote)
        
    def update_amplitude(self, interval = 2997):
     
        try:
            value = pd.read_csv(config_parameters_filename)['Amplitude'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_amplitude['text'] = str(value)
        self.label_value_amplitude.after(interval, self.update_amplitude)
        
    def update_phase(self, interval = 2999):
        
        try:
            value = pd.read_csv(config_parameters_filename)['Phase'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_phase['text'] = str(value)
        self.label_value_phase.after(interval, self.update_phase)
     
    def update_frequency(self, interval = 3001):   
     
        try:
            value = pd.read_csv(config_parameters_filename)['Frequency'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_frequency['text'] = str(value)
        self.label_value_frequency.after(interval, self.update_frequency)
      
    def update_value_ch1(self, interval = 307):
      
        try:
            value = pd.read_csv(config_channels_filename)['Ch1'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_ch1['text'] = '\n' + str(value)
        self.label_value_ch1.after(interval, self.update_value_ch1)
       
    def update_value_ch2(self, interval = 311): 
       
        try:
            value = pd.read_csv(config_channels_filename)['Ch2'].values[-1] 
        except IndexError:
            value = 0.0
        self.label_value_ch2['text'] = '\n' + str(value)
        self.label_value_ch2.after(interval, self.update_value_ch2)
        
class Sweeper1d(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
    
        label = tk.Label(self, text = '1dSweeper', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button_home = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button_home.pack()
        
        label_to_sweep = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep.place(relx = 0.15, rely = 0.12)
        
        label_to_read = tk.Label(self, text = 'To read:', font = LARGE_FONT)
        label_to_read.place(relx = 0.3, rely = 0.12)
        
        self.combo_to_sweep = ttk.Combobox(self, value = ['Time', *list_of_devices])
        self.combo_to_sweep.current(0)
        self.combo_to_sweep.bind("<<ComboboxSelected>>", self.update_sweep_parameters)
        self.combo_to_sweep.place(relx = 0.15, rely = 0.16)
        
        devices = tk.StringVar()
        devices.set(value = parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable = devices, 
                            selectmode = 'multiple', width=20, 
                            height = len(parameters_to_read) * 2)
        self.lstbox_to_read.place(relx = 0.3, rely = 0.16)
        
        self.sweep_options = ttk.Combobox(self)
        self.sweep_options.place(relx = 0.15, rely = 0.2)
        
        label_min = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min.place(relx = 0.12, rely = 0.24)
        
        label_max = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max.place(relx = 0.12, rely = 0.28)
        
        label_step = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step.place(relx = 0.12, rely = 0.32)
        
        self.entry_min = tk.Entry(self)
        self.entry_min.place(relx = 0.17, rely = 0.24)
        
        self.entry_max = tk.Entry(self)
        self.entry_max.place(relx = 0.17, rely = 0.28)
        
        self.entry_ratio = tk.Entry(self)
        self.entry_ratio.place(relx = 0.17, rely = 0.32)
        
        label_delay_factor = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor.place(relx = 0.12, rely = 0.4)
        
        self.entry_delay_factor = tk.Entry(self)
        self.entry_delay_factor.place(relx = 0.12, rely = 0.46)
        
        #section of manual sweep points selection
        self.status_manual = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            filename = filename_sweep[:index_sweep] + 'manual' + filename_sweep[index_sweep + 5:]
        else:
            filename[:-4] + '_manual' + '.csv'
        
        #icons
        save = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\save.png')
        explore = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\explore.png')
        create = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\create.png')
        #initials
        manual_sweep_flags = [0]
        manual_filenames = ['']
            
        checkbox_manual = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status())
        checkbox_manual.place(relx = 0.12, rely = 0.52)
        
        button_new_manual = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename))
        button_new_manual.place(relx = 0.17, rely = 0.52)
        
        button_explore_manual = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files())
        button_explore_manual.place(relx = 0.25, rely = 0.52)
        
        button_filename = ttk.Button(self, text = 'Filename', command = lambda: self.set_filename_sweep())
        button_filename.place(relx = 0.7, rely = 0.6)
        
        button_start_sweeping = ttk.Button(self, text = "Start sweeping", command = lambda: self.start_sweeping())
        button_start_sweeping.place(relx = 0.7, rely = 0.7)
        
        graph_button = ttk.Button(self, text = 'Graph', command = lambda: Universal_frontend(classes = (Graph,), start = Graph))
        graph_button.place(relx = 0.7, rely = 0.8)
        
    def update_sweep_parameters(self, event, interval = 1000):
        if self.combo_to_sweep.current() == 0:
            self.sweep_options['value'] = ['']
            self.sweep_options.current(0)
            self.sweep_options.after(interval)
            pass
        else:
            class_of_sweeper_device = types_of_devices[self.combo_to_sweep.current() - 1]
            if class_of_sweeper_device != 'Not a class':
                self.sweep_options['value'] = getattr(globals()[class_of_sweeper_device](), 'set_options')
                self.sweep_options.after(interval)
                    
    def save_manual_status(self):
        global manual_sweep_flags
        if manual_sweep_flags[0] != self.status_manual.get():
            manual_sweep_flags[0] = self.status_manual.get()
                
    def open_blank(self, filename):
        global manual_filenames
        global manual_sweep_flags
        with open(filename, 'w') as _:
            pass
        manual_filenames[0] = filename
        os.startfile(filename)
        
    def explore_files(self):
        global manual_sweep_flags
        global manual_filenames
        filename = tk.filedialog.askopenfilename(initialdir = r'C:\NUS\Transport lab\Test',
                                      title = 'Select a manual sweeper',
                                      filetypes = (('CSV files', '*.csv*'),
                                                   ('all files', '*.*')))
        manual_filenames[0] = filename
        
    def set_filename_sweep(self):
        global filename_sweep
        
        filename_sweep = tk.filedialog.asksaveasfilename(title = 'Save the file', 
                                                     initialfile = r'C:\NUS\Transport lab\Test\data_files\sweep' + datetime.today().strftime(
                                                                                     '%H_%M_%d_%m_%Y'),
                                                     defaultextension = '.csv')
                
    def start_sweeping(self):
        
        global device_to_sweep1
        global parameter_to_sweep1
        global min_sweep1 
        global max_sweep1 
        global ratio_sweep1
        global delay_factor1
        global parameters_to_read 
        global filename_sweep 
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global columns
        
        #asking multichoise to get parameters to read
        self.list_to_read = list()
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(entrada)
        parameters_to_read = self.list_to_read
        
        #creating columns
        if self.combo_to_sweep.current() == 0:
            columns = ['Time']
        else:
            device_to_sweep1 = self.combo_to_sweep['value'][self.combo_to_sweep.current()]
            parameter_to_sweep1 = self.sweep_options['value'][self.sweep_options.current()]
            columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1]   
        for option in parameters_to_read:
            columns.append(option)
        
        #fixing sweeper parmeters
        min_sweep1 = self.entry_min.get()
        max_sweep1 = self.entry_max.get()
        ratio_sweep1 = self.entry_ratio.get()
        delay_factor1 = self.entry_delay_factor.get()
        sweeper_flag1 = True
        sweeper_flag2 = False
        sweeper_flag3 = False
        
        Sweeper_write()
        
class Sweeper2d(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = '2dSweeper', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button_home = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button_home.pack()
        
        label_to_sweep1 = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep1.place(relx = 0.15, rely = 0.12)
        
        label_to_sweep2 = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep2.place(relx = 0.3, rely = 0.12)
        
        label_to_read = tk.Label(self, text = 'To read:', font = LARGE_FONT)
        label_to_read.place(relx = 0.45, rely = 0.12)
        
        self.combo_to_sweep1 = ttk.Combobox(self, value = list_of_devices)
        self.combo_to_sweep1.current(0)
        self.combo_to_sweep1.bind("<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx = 0.15, rely = 0.16)
        
        self.combo_to_sweep2 = ttk.Combobox(self, value = list_of_devices)
        self.combo_to_sweep2.current(0)
        self.combo_to_sweep2.bind("<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx = 0.3, rely = 0.16)
        
        devices = tk.StringVar()
        devices.set(value = parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable = devices, 
                            selectmode = 'multiple', width=20, 
                            height = len(parameters_to_read) * 2)
        self.lstbox_to_read.place(relx = 0.45, rely = 0.16)
        
        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx = 0.15, rely = 0.2)
        
        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx = 0.3, rely = 0.2)
        
        label_min1 = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min1.place(relx = 0.12, rely = 0.24)
        
        label_max1 = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max1.place(relx = 0.12, rely = 0.28)
        
        label_step1 = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step1.place(relx = 0.12, rely = 0.32)
        
        self.entry_min1 = tk.Entry(self)
        self.entry_min1.place(relx = 0.17, rely = 0.24)
        
        self.entry_max1 = tk.Entry(self)
        self.entry_max1.place(relx = 0.17, rely = 0.28)
        
        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.place(relx = 0.17, rely = 0.32)
        
        label_delay_factor1 = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor1.place(relx = 0.12, rely = 0.4)
        
        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.place(relx = 0.12, rely = 0.46)
        
        label_min2 = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min2.place(relx = 0.27, rely = 0.24)
        
        label_max2 = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max2.place(relx = 0.27, rely = 0.28)
        
        label_step2 = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step2.place(relx = 0.27, rely = 0.32)
        
        self.entry_min2 = tk.Entry(self)
        self.entry_min2.place(relx = 0.32, rely = 0.24)
        
        self.entry_max2 = tk.Entry(self)
        self.entry_max2.place(relx = 0.32, rely = 0.28)
        
        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.place(relx = 0.32, rely = 0.32)
        
        label_delay_factor2 = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor2.place(relx = 0.27, rely = 0.4)
        
        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.place(relx = 0.27, rely = 0.46)
        
        #section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            filename = filename_sweep[:index_sweep] + 'manual' + filename_sweep[index_sweep + 5:]
        else:
            filename[:-4] + '_manual' + '.csv'
        
        #icons
        save = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\save.png')
        explore = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\explore.png')
        create = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\create.png')
        #initials
        manual_sweep_flags = [0, 0]
        manual_filenames = ['', '']
            
        checkbox_manual1 = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual1, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status(i = 0))
        checkbox_manual1.place(relx = 0.12, rely = 0.52)
        
        button_new_manual1 = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename, i = 0))
        button_new_manual1.place(relx = 0.17, rely = 0.52)
        
        button_explore_manual1 = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files(i = 0))
        button_explore_manual1.place(relx = 0.17, rely = 0.6)
        
        checkbox_manual2 = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual2, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status(i = 1))
        checkbox_manual2.place(relx = 0.32, rely = 0.52)
        
        button_new_manual2 = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename, i = 1))
        button_new_manual2.place(relx = 0.37, rely = 0.52)
        
        button_explore_manual2 = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files(i = 1))
        button_explore_manual2.place(relx = 0.37, rely = 0.6)
        
        button_filename = ttk.Button(self, text = 'Filename', command = lambda: self.set_filename_sweep())
        button_filename.place(relx = 0.7, rely = 0.6)
        
        button_start_sweeping = ttk.Button(self, text = "Start sweeping", command = lambda: self.start_sweeping())
        button_start_sweeping.place(relx = 0.7, rely = 0.7)
        
        graph_button = ttk.Button(self, text = 'Graph', command = lambda: Universal_frontend(classes = (Graph,), start = Graph))
        graph_button.place(relx = 0.7, rely = 0.8)
        
    def update_sweep_parameters1(self, event, interval = 1000):
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current()]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)

    def update_sweep_parameters2(self, event, interval = 1000):
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current()]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)
            
    def save_manual_status(self, i):
        global manual_sweep_flags
        if manual_sweep_flags[i] != globals()['self.status_manual' + str(i)].get():
            manual_sweep_flags[i] = globals()['self.status_manual' + str(i)].get()
                
    def open_blank(self, filename, i):
        global manual_filenames
        global manual_sweep_flags
        with open(filename, 'w') as _:
            pass
        manual_filenames[i] = filename
        os.startfile(filename)
        
    def explore_files(self, i):
        global manual_sweep_flags
        global manual_filenames
        filename = tk.filedialog.askopenfilename(initialdir = r'C:\NUS\Transport lab\Test',
                                      title = 'Select a manual sweeper',
                                      filetypes = (('CSV files', '*.csv*'),
                                                   ('all files', '*.*')))
        manual_filenames[i] = filename

        
    def set_filename_sweep(self):
        global filename_sweep
        
        filename_sweep = tk.filedialog.asksaveasfilename(title = 'Save the file', 
                                                     initialfile = r'C:\NUS\Transport lab\Test\data_files\sweep' + datetime.today().strftime(
                                                                                     '%H_%M_%d_%m_%Y'),
                                                     defaultextension = '.csv')
                    
    def start_sweeping(self):
        
        global device_to_sweep1
        global device_to_sweep2
        global parameter_to_sweep1
        global parameter_to_sweep2
        global min_sweep1 
        global max_sweep1 
        global ratio_sweep1
        global delay_factor1
        global min_sweep2 
        global max_sweep2 
        global ratio_sweep2
        global delay_factor2
        global parameters_to_read 
        global filename_sweep 
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global columns
        
        #asking multichoise to get parameters to read
        self.list_to_read = list()
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(entrada)
        parameters_to_read = self.list_to_read
        
        #creating columns
        device_to_sweep1 = self.combo_to_sweep1['value'][self.combo_to_sweep1.current()]
        parameter_to_sweep1 = self.sweep_options1['value'][self.sweep_options1.current()]
        device_to_sweep2 = self.combo_to_sweep2['value'][self.combo_to_sweep2.current()]
        parameter_to_sweep2 = self.sweep_options2['value'][self.sweep_options2.current()]
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1, device_to_sweep2 + '.' + parameter_to_sweep2]   
        for option in parameters_to_read:
            columns.append(option)
        
        #fixing sweeper parmeters
        min_sweep1 = self.entry_min1.get()
        max_sweep1 = self.entry_max1.get()
        ratio_sweep1 = self.entry_ratio1.get()
        delay_factor1 = self.entry_delay_factor1.get()
        min_sweep2 = self.entry_min2.get()
        max_sweep2 = self.entry_max2.get()
        ratio_sweep2 = self.entry_ratio2.get()
        delay_factor2 = self.entry_delay_factor2.get()
        sweeper_flag1 = False
        sweeper_flag2 = True
        sweeper_flag3 = False
        
        Sweeper_write()
        
class Sweeper3d(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = '3dSweeper', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button_home = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button_home.pack()
        
        label_to_sweep1 = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep1.place(relx = 0.15, rely = 0.12)
        
        label_to_sweep2 = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep2.place(relx = 0.3, rely = 0.12)
        
        label_to_sweep3 = tk.Label(self, text = 'To sweep:', font = LARGE_FONT)
        label_to_sweep3.place(relx = 0.3, rely = 0.12)
        
        label_to_read = tk.Label(self, text = 'To read:', font = LARGE_FONT)
        label_to_read.place(relx = 0.6, rely = 0.12)
        
        self.combo_to_sweep1 = ttk.Combobox(self, value = list_of_devices)
        self.combo_to_sweep1.current(0)
        self.combo_to_sweep1.bind("<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx = 0.15, rely = 0.16)
        
        self.combo_to_sweep2 = ttk.Combobox(self, value = list_of_devices)
        self.combo_to_sweep2.current(0)
        self.combo_to_sweep2.bind("<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx = 0.3, rely = 0.16)
        
        self.combo_to_sweep3 = ttk.Combobox(self, value = list_of_devices)
        self.combo_to_sweep3.current(0)
        self.combo_to_sweep3.bind("<<ComboboxSelected>>", self.update_sweep_parameters3)
        self.combo_to_sweep3.place(relx = 0.45, rely = 0.16)
        
        devices = tk.StringVar()
        devices.set(value = parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable = devices, 
                            selectmode = 'multiple', width=20, 
                            height = len(parameters_to_read) * 2)
        self.lstbox_to_read.place(relx = 0.6, rely = 0.16)
        
        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx = 0.15, rely = 0.2)
        
        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx = 0.3, rely = 0.2)
        
        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx = 0.45, rely = 0.2)
        
        label_min1 = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min1.place(relx = 0.12, rely = 0.24)
        
        label_max1 = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max1.place(relx = 0.12, rely = 0.28)
        
        label_step1 = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step1.place(relx = 0.12, rely = 0.32)
        
        self.entry_min1 = tk.Entry(self)
        self.entry_min1.place(relx = 0.17, rely = 0.24)
        
        self.entry_max1 = tk.Entry(self)
        self.entry_max1.place(relx = 0.17, rely = 0.28)
        
        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.place(relx = 0.17, rely = 0.32)
        
        label_delay_factor1 = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor1.place(relx = 0.12, rely = 0.4)
        
        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.place(relx = 0.12, rely = 0.46)
        
        label_min2 = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min2.place(relx = 0.27, rely = 0.24)
        
        label_max2 = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max2.place(relx = 0.27, rely = 0.28)
        
        label_step2 = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step2.place(relx = 0.27, rely = 0.32)
        
        self.entry_min2 = tk.Entry(self)
        self.entry_min2.place(relx = 0.32, rely = 0.24)
        
        self.entry_max2 = tk.Entry(self)
        self.entry_max2.place(relx = 0.32, rely = 0.28)
        
        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.place(relx = 0.32, rely = 0.32)
        
        label_delay_factor2 = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor2.place(relx = 0.27, rely = 0.4)
        
        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.place(relx = 0.27, rely = 0.46)
        
        label_min3 = tk.Label(self, text = 'MIN', font = LARGE_FONT)
        label_min3.place(relx = 0.42, rely = 0.24)
        
        label_max3 = tk.Label(self, text = 'MAX', font = LARGE_FONT)
        label_max3.place(relx = 0.42, rely = 0.28)
        
        label_step3 = tk.Label(self, text = 'Ratio, \n Δ/s', font = LARGE_FONT)
        label_step3.place(relx = 0.42, rely = 0.32)
        
        self.entry_min3 = tk.Entry(self)
        self.entry_min3.place(relx = 0.47, rely = 0.24)
        
        self.entry_max3 = tk.Entry(self)
        self.entry_max3.place(relx = 0.47, rely = 0.28)
        
        self.entry_ratio3 = tk.Entry(self)
        self.entry_ratio3.place(relx = 0.47, rely = 0.32)
        
        label_delay_factor3 = tk.Label(self, text = 'Delay factor, s', justify=tk.LEFT, font = LARGE_FONT)
        label_delay_factor3.place(relx = 0.42, rely = 0.4)
        
        self.entry_delay_factor3 = tk.Entry(self)
        self.entry_delay_factor3.place(relx = 0.42, rely = 0.46)
        
        #section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        self.status_manual3 = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            filename = filename_sweep[:index_sweep] + 'manual' + filename_sweep[index_sweep + 5:]
        else:
            filename[:-4] + '_manual' + '.csv'
        
        #icons
        save = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\save.png')
        explore = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\explore.png')
        create = tk.PhotoImage(file = r'C:\NUS\Transport lab\App\create.png')
        #initials
        manual_sweep_flags = [0, 0, 0]
        manual_filenames = ['', '', '']
            
        checkbox_manual1 = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual1, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status(i = 0))
        checkbox_manual1.place(relx = 0.12, rely = 0.52)
        
        button_new_manual1 = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename, i = 0))
        button_new_manual1.place(relx = 0.17, rely = 0.52)
        
        button_explore_manual1 = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files(i = 0))
        button_explore_manual1.place(relx = 0.17, rely = 0.6)
        
        checkbox_manual2 = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual2, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status(i = 1))
        checkbox_manual2.place(relx = 0.32, rely = 0.52)
        
        button_new_manual2 = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename, i = 1))
        button_new_manual2.place(relx = 0.37, rely = 0.52)
        
        button_explore_manual2 = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files(i = 1))
        button_explore_manual2.place(relx = 0.37, rely = 0.6)
        
        checkbox_manual3 = ttk.Checkbutton(self, text = 'Maunal sweep select', 
                                          variable = self.status_manual3, onvalue = 1,
                                          offvalue = 0, command = lambda: self.save_manual_status(i = 2))
        checkbox_manual3.place(relx = 0.52, rely = 0.52)
        
        button_new_manual3 = ttk.Button(self, text = 'New', command = lambda: self.open_blank(filename = filename, i = 2))
        button_new_manual3.place(relx = 0.57, rely = 0.52)
        
        button_explore_manual3 = ttk.Button(self, text = 'Explore', command = lambda: self.explore_files(i = 2))
        button_explore_manual3.place(relx = 0.57, rely = 0.6)
        
        button_filename = ttk.Button(self, text = 'Filename', command = lambda: self.set_filename_sweep())
        button_filename.place(relx = 0.7, rely = 0.6)
        
        button_start_sweeping = ttk.Button(self, text = "Start sweeping", command = lambda: self.start_sweeping())
        button_start_sweeping.place(relx = 0.75, rely = 0.7)
        
        graph_button = ttk.Button(self, text = 'Graph', command = lambda: Universal_frontend(classes = (Graph,), start = Graph))
        graph_button.place(relx = 0.7, rely = 0.8)
        
    def update_sweep_parameters1(self, event, interval = 1000):
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current()]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)

    def update_sweep_parameters2(self, event, interval = 1000):
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current()]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)
            
    def update_sweep_parameters3(self, event, interval = 1000):       
        class_of_sweeper_device3 = types_of_devices[self.combo_to_sweep3.current()]
        if class_of_sweeper_device3 != 'Not a class':
            self.sweep_options3['value'] = getattr(globals()[class_of_sweeper_device3](), 'set_options')
            self.sweep_options3.after(interval)
        else:
            self.sweep_options3['value'] = ['']
            self.sweep_options3.current(0)
            self.sweep_options3.after(interval)
                    
    def save_manual_status(self, i):
        global manual_sweep_flags
        if manual_sweep_flags[i] != globals()['self.status_manual' + str(i)].get():
            manual_sweep_flags[i] = globals()['self.status_manual' + str(i)].get()
                
    def open_blank(self, filename, i):
        global manual_filenames
        global manual_sweep_flags
        with open(filename, 'w') as _:
            pass
        manual_filenames[i] = filename
        os.startfile(filename)
        
    def explore_files(self, i):
        global manual_sweep_flags
        global manual_filenames
        filename = tk.filedialog.askopenfilename(initialdir = r'C:\NUS\Transport lab\Test',
                                      title = 'Select a manual sweeper',
                                      filetypes = (('CSV files', '*.csv*'),
                                                   ('all files', '*.*')))
        manual_filenames[i] = filename
        
    def set_filename_sweep(self):
        global filename_sweep
        
        filename_sweep = tk.filedialog.asksaveasfilename(title = 'Save the file', 
                                                     initialfile = r'C:\NUS\Transport lab\Test\data_files\sweep' + datetime.today().strftime(
                                                                                     '%H_%M_%d_%m_%Y'),
                                                     defaultextension = '.csv')
            
    def start_sweeping(self):
        
        global device_to_sweep1
        global device_to_sweep2
        global device_to_sweep3
        global parameter_to_sweep1
        global parameter_to_sweep2
        global parameter_to_sweep3
        global min_sweep1 
        global max_sweep1 
        global ratio_sweep1
        global delay_factor1
        global min_sweep2 
        global max_sweep2 
        global ratio_sweep2
        global delay_factor2
        global min_sweep3
        global max_sweep3
        global ratio_sweep3
        global delay_factor3
        global parameters_to_read 
        global filename_sweep 
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global columns
        
        #asking multichoise to get parameters to read
        self.list_to_read = list()
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(entrada)
        parameters_to_read = self.list_to_read
        
        #creating columns
        device_to_sweep1 = self.combo_to_sweep1['value'][self.combo_to_sweep1.current()]
        parameter_to_sweep1 = self.sweep_options1['value'][self.sweep_options1.current()]
        device_to_sweep2 = self.combo_to_sweep2['value'][self.combo_to_sweep2.current()]
        parameter_to_sweep2 = self.sweep_options2['value'][self.sweep_options2.current()]
        device_to_sweep3 = self.combo_to_sweep3['value'][self.combo_to_sweep3.current()]
        parameter_to_sweep3 = self.sweep_options3['value'][self.sweep_options3.current()]
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1, 
                   device_to_sweep2 + '.' + parameter_to_sweep2, 
                   device_to_sweep3 + '.' + parameter_to_sweep3]   
        for option in parameters_to_read:
            columns.append(option)
        
        #fixing sweeper parmeters
        min_sweep1 = self.entry_min1.get()
        max_sweep1 = self.entry_max1.get()
        ratio_sweep1 = self.entry_ratio1.get()
        delay_factor1 = self.entry_delay_factor1.get()
        min_sweep2 = self.entry_min2.get()
        max_sweep2 = self.entry_max2.get()
        ratio_sweep2 = self.entry_ratio2.get()
        delay_factor2 = self.entry_delay_factor2.get()
        min_sweep3 = self.entry_min3.get()
        max_sweep3 = self.entry_max3.get()
        ratio_sweep3 = self.entry_ratio3.get()
        delay_factor3 = self.entry_delay_factor3.get()
        sweeper_flag1 = False
        sweeper_flag2 = False
        sweeper_flag3 = True
        
        Sweeper_write()
        
class Sweeper_write(threading.Thread):
     
    def __init__(self):
    
        threading.Thread.__init__(self)
        self.device_to_sweep1 = device_to_sweep1
        self.device_to_sweep2 = device_to_sweep2
        self.device_to_sweep3 = device_to_sweep3
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.parameter_to_sweep3 = parameter_to_sweep3
        self.min_sweep1 = float(min_sweep1) 
        self.max_sweep1 = float(max_sweep1)
        self.ratio_sweep1 = float(ratio_sweep1)
        self.delay_factor1 = float(delay_factor1)
        self.min_sweep2 = float(min_sweep2) 
        self.max_sweep2 = float(max_sweep2)
        self.ratio_sweep2 = float(ratio_sweep2)
        self.delay_factor2 = float(delay_factor2)
        self.min_sweep3 = float(min_sweep3) 
        self.max_sweep3 = float(max_sweep3)
        self.ratio_sweep3 = float(ratio_sweep3)
        self.delay_factor3 = float(delay_factor3)
        self.parameters_to_read = parameters_to_read
        self.filename_sweep = filename_sweep
        self.value1 = float(min_sweep1)
        self.value2 = float(min_sweep2)
        self.value3 = float(min_sweep3)
        self.columns = columns
        self.sweeper_flag1 = sweeper_flag1
        self.sweeper_flag2 = sweeper_flag2
        self.sweeper_flag3 = sweeper_flag3
        self.step1 = float(delay_factor1) * float(ratio_sweep1)
        self.step2 = float(delay_factor2) * float(ratio_sweep2)
        self.step3 = float(delay_factor3) * float(ratio_sweep3)
        self.time1 = (float(min_sweep1) - float(max_sweep1)) / float(ratio_sweep1)
        self.time2 = (float(min_sweep2) - float(max_sweep2)) / float(ratio_sweep2)
        self.time3 = (float(min_sweep3) - float(max_sweep3)) / float(ratio_sweep3)
        '''
        try:
            self.nstep1 = (float(max_sweep1) - float(min_sweep1)) / self.ratio_sweep1 / self.delay_factor1
        except ValueError:
            self.nstep1 = 1
        try:
            self.nstep2 = (float(max_sweep2) - float(min_sweep2)) / self.ratio_sweep2 / self.delay_factor2
        except ValueError:
            self.nstep2 = 1
        try:
            self.nstep3 = (float(max_sweep3) - float(min_sweep3)) / self.ratio_sweep3 / self.delay_factor3
        except ValueError:
            self.nstep3 = 1
        '''
        try:
            threading.Thread.__init__(self)
            self.daemon = True
            self.start()
        except NameError:
            pass
        
    def transposition(self, a, b):
        #changes device_a and device_b order
        a = str(a)
        b = str(b)
        globals()['self.device_to_sweep' + a] = globals()['device_to_sweep' + b]
        globals()['self.device_to_sweep' + b] = globals()['device_to_sweep' + a]
        globals()['self.parameter_to_sweep' + a] = globals()['parameter_to_sweep' + b]
        globals()['self.parameter_to_sweep' + b] = globals()['parameter_to_sweep' + a]
        globals()['self.min_sweep' + a] = float(globals()['min_sweep' + b]) 
        globals()['self.max_sweep' + a] = float(globals()['max_sweep' + b])
        globals()['self.ratio_sweep' + a] = float(globals()['ratio_sweep' + b]) 
        globals()['self.delay_factor' + a] = float(globals()['delay_factor' + b])
        globals()['self.min_sweep' + b] = float(globals()['min_sweep' + a]) 
        globals()['self.max_sweep' + b] = float(globals()['max_sweep' + a])
        globals()['self.ratio_sweep' + b] = float(globals()['ratio_sweep' + a]) 
        globals()['self.delay_factor' + b] = float(globals()['delay_factor' + a])
        globals()['self.step' + a] = float(globals()['delay_factor' + b]) * float(globals()['ratio_sweep' + b])
        globals()['self.step' + b] = float(globals()['delay_factor' + a]) * float(globals()['ratio_sweep' + a])
        globals()['self.value' + a] = float(globals()['min_sweep' + b])
        globals()['self.value' + b] = float(globals()['min_sweep' + a])
        globals()['self.time' + a] = (float(globals()['min_sweep' + b]) - float(globals()['max_sweep' + b])) / float(globals()['ratio_sweep' + b])
        globals()['self.time' + b] = (float(globals()['min_sweep' + a]) - float(globals()['max_sweep' + a])) / float(globals()['ratio_sweep' + a])
        
    def run(self):
        if self.sweeper_flag1 == True:
            dataframe = pd.DataFrame(columns = self.columns)
            dataframe.to_csv(self.filename_sweep, index = False)
            while self.value1 <= self.max_sweep1:
                if self.device_to_sweep1 == 'Time':
                    dataframe = [time.process_time() - zero_time]
                else:
                    dataframe = [time.process_time() - zero_time]
                    #sweep process here
                    ###################
                    #set 'parameter_to_sweep' to 'value'
                    getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep1)]](adress = self.device_to_sweep1), 'set_' + str(self.parameter_to_sweep1))(value = self.value1)
                    self.value1 += self.step1
                    time.sleep(self.delay_factor1)
                    ###################
                    dataframe.append(self.value1)
                for parameter in self.parameters_to_read:
                    index_dot = parameter.find('.')
                    adress = parameter[:index_dot]
                    option = parameter[index_dot + 1:]
                    dataframe.append(getattr(globals()[types_of_devices[list_of_devices.index(str(adress))]](adress = adress), option)()) 
            
                with open(self.filename_sweep, 'a') as f_object:
                    try:
                        writer_object = writer(f_object)
                        writer_object.writerow(dataframe)
                        f_object.close()
                    except KeyboardInterrupt():
                        f_object.close()
                    finally:
                        f_object.close()
            self.sweeper_flag1 = False
                        
        if self.sweeper_flag2 == True:
            dataframe = pd.DataFrame(columns = self.columns)
            dataframe.to_csv(self.filename_sweep, index = False)

            if self.time1 > self.time2:
                self.transposition(1, 2)
            
            while self.value1 <= self.max_sweep1:
                dataframe = [time.process_time() - zero_time]
                #sweep process 1 here
                ###################
                #set 'parameter_to_sweep1' to 'value1'
                getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep1)]](adress = self.device_to_sweep1), 'set_' + str(self.parameter_to_sweep1))(value = self.value1)
                self.value1 += self.step1
                time.sleep(self.delay_factor1)
                ###################
                dataframe.append(self.value1)
                dataframe_after = [*dataframe]
                while self.value2 <= self.max_sweep2:
                    #sweep process 2 here
                    ###################
                    #set 'parameter_to_sweep2' to 'value2'
                    dataframe = [*dataframe_after]
                    dataframe[0] = time.process_time() - zero_time
                    getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep2)]](adress = self.device_to_sweep2), 'set_' + str(self.parameter_to_sweep2))(value = self.value2)
                    self.value2 += self.step2
                    time.sleep(self.delay_factor2)
                    ###################
                    dataframe.append(self.value2)
                    for parameter in self.parameters_to_read:
                        index_dot = parameter.find('.')
                        adress = parameter[:index_dot]
                        option = parameter[index_dot + 1:]
                        dataframe.append(getattr(globals()[types_of_devices[list_of_devices.index(str(adress))]](adress = adress), option)()) 
        
                    with open(self.filename_sweep, 'a') as f_object:
                        try:
                            writer_object = writer(f_object)
                            writer_object.writerow(dataframe)
                            f_object.close()
                        except KeyboardInterrupt():
                            f_object.close()
                        finally:
                            f_object.close()
                self.value2 = self.min_sweep2
            self.sweeper_flag2 == False

        if self.sweeper_flag3 == True:
            dataframe = pd.DataFrame(columns = self.columns)
            dataframe.to_csv(self.filename_sweep, index = False)

            if self.time1 > self.time2:             
                self.transposition(1, 2)
            if self.time1 > self.time3:
                self.transposition(1, 3)
            if self.time2 > self.time3:
                self.transposition(2, 3)
                
            while self.value1 <= self.max_sweep1:
                dataframe = [time.process_time() - zero_time]
                #sweep process 1 here
                ###################
                #set 'parameter_to_sweep1' to 'value1'
                getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep1)]](adress = self.device_to_sweep1), 'set_' + str(self.parameter_to_sweep1))(value = self.value1)
                self.value1 += self.step1
                time.sleep(self.delay_factor1)
                ###################
                dataframe.append(self.value1)
                dataframe_after = [*dataframe]
                while self.value2 <= self.max_sweep2:
                    #sweep process 2 here
                    ###################
                    #set 'parameter_to_sweep2' to 'value2'
                    dataframe = [*dataframe_after]
                    dataframe[0] = time.process_time() - zero_time
                    getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep2)]](adress = self.device_to_sweep2), 'set_' + str(self.parameter_to_sweep2))(value = self.value2)
                    self.value2 += self.step2
                    time.sleep(self.delay_factor2)
                    ###################
                    dataframe.append(self.value2)
                    dataframe_after_after = [*dataframe]
                    while self.value3 <= self.max_sweep3:
                        #sweep process 3 here
                        ###################
                        #set 'parameter_to_sweep3' to 'value3'
                        dataframe = [*dataframe_after_after]
                        dataframe[0] = time.process_time() - zero_time
                        getattr(globals()[types_of_devices[list_of_devices.index(self.device_to_sweep3)]](adress = self.device_to_sweep3), 'set_' + str(self.parameter_to_sweep3))(value = self.value3)
                        self.value3 += self.step3
                        time.sleep(self.delay_factor3)
                        ###################
                        dataframe.append(self.value3)
                        for parameter in self.parameters_to_read:
                            index_dot = parameter.find('.')
                            adress = parameter[:index_dot]
                            option = parameter[index_dot + 1:]
                            dataframe.append(getattr(globals()[types_of_devices[list_of_devices.index(str(adress))]](adress = adress), option)()) 
            
                        with open(self.filename_sweep, 'a') as f_object:
                            try:
                                writer_object = writer(f_object)
                                writer_object.writerow(dataframe)
                                f_object.close()
                            except KeyboardInterrupt():
                                f_object.close()
                            finally:
                                f_object.close()
                    self.value3 = self.min_sweep3
                self.value2 = self.min_sweep3
            self.sweeper_flag3 == False


class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
   def __init__(self, canvas, window):
      super().__init__(canvas, window, pack_toolbar=False)

   # override _Button() to re-pack the toolbar button in vertical direction
   def _Button(self, text, image_file, toggle, command):
      b = super()._Button(text, image_file, toggle, command)
      b.pack(side=tk.TOP) # re-pack button in vertical direction
      return b

   # override _Spacer() to create vertical separator
   def _Spacer(self):
      s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
      s.pack(side=tk.TOP, pady=5) # pack in vertical direction
      return s

   # disable showing mouse position in toolbar
   def set_message(self, s):
      pass
        
class Graph(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        label_x1 = tk.Label(self, text = 'x', font = LARGE_FONT)
        label_x1.place(relx = 0.02, rely = 0.455)
        
        label_y1 = tk.Label(self, text = 'y', font = LARGE_FONT)
        label_y1.place(relx = 0.15, rely = 0.455)
        
        self.combo_x1 = ttk.Combobox(self, values = columns)
        self.combo_x1.bind("<<ComboboxSelected>>", self.x1_update)
        self.combo_x1.place(relx = 0.035, rely = 0.46)
        
        self.combo_y1 = ttk.Combobox(self, values = columns)
        self.combo_y1.bind("<<ComboboxSelected>>", self.y1_update)
        self.combo_y1.place(relx = 0.165, rely = 0.46)
        
        label_x2 = tk.Label(self, text = 'x', font = LARGE_FONT)
        label_x2.place(relx = 0.52, rely = 0.455)
        
        label_y2 = tk.Label(self, text = 'y', font = LARGE_FONT)
        label_y2.place(relx = 0.65, rely = 0.455)
        
        self.combo_x2 = ttk.Combobox(self, values = columns)
        self.combo_x2.bind("<<ComboboxSelected>>", self.x2_update)
        self.combo_x2.place(relx = 0.535, rely = 0.46)
        
        self.combo_y2 = ttk.Combobox(self, values = columns)
        self.combo_y2.bind("<<ComboboxSelected>>", self.y2_update)
        self.combo_y2.place(relx = 0.665, rely = 0.46)
        
        label_x3 = tk.Label(self, text = 'x', font = LARGE_FONT)
        label_x3.place(relx = 0.02, rely = 0.955)
        
        label_y3 = tk.Label(self, text = 'y', font = LARGE_FONT)
        label_y3.place(relx = 0.15, rely = 0.955)
        
        self.combo_x3 = ttk.Combobox(self, values = columns)
        self.combo_x3.bind("<<ComboboxSelected>>", self.x3_update)
        self.combo_x3.place(relx = 0.035, rely = 0.96)
        
        self.combo_y3 = ttk.Combobox(self, values = columns)
        self.combo_y3.bind("<<ComboboxSelected>>", self.y3_update)
        self.combo_y3.place(relx = 0.165, rely = 0.96)
        
        '''
        label_x4 = tk.Label(self, text = 'x', font = LARGE_FONT)
        label_x4.place(relx = 0.52, rely = 0.955)
        
        label_y4 = tk.Label(self, text = 'y', font = LARGE_FONT)
        label_y4.place(relx = 0.65, rely = 0.955)
        
        label_z4 = tk.Label(self, text = 'z', font = LARGE_FONT)
        label_z4.place(relx = 0.78, rely = 0.955)
        
        self.combo_x4 = ttk.Combobox(self, values = columns)
        try:
            self.combo_x4.current(0)
        except tk.TclError:
            pass
        self.combo_x4.bind("<<ComboboxSelected>>")
        self.combo_x4.place(relx = 0.535, rely = 0.96)
        
        self.combo_y4 = ttk.Combobox(self, values = columns)
        try:
            self.combo_y4.current(0)
        except tk.TclError:
            pass
        self.combo_y4.bind("<<ComboboxSelected>>")
        self.combo_y4.place(relx = 0.665, rely = 0.96)
    
        self.combo_z4 = ttk.Combobox(self, values = columns)
        try:
            self.combo_z4.current(0)
        except tk.TclError:
            pass
        self.combo_z4.bind("<<ComboboxSelected>>")
        self.combo_z4.place(relx = 0.795, rely = 0.96)   
        '''
        if sweeper_flag1 == True:
            self.combo_x1.current(0)
            x1_status = 0
            self.combo_y1.current(2)
            y1_status = 2
            self.combo_x2.current(0)
            x2_status = 0
            self.combo_y2.current(2)
            y2_status = 2
            self.combo_x3.current(0)
            x3_status = 0
            self.combo_y3.current(2)
            y3_status = 2
        if sweeper_flag2 == True:
            self.combo_x1.current(0)
            x1_status = 0
            self.combo_y1.current(3)
            y1_status = 3
            self.combo_x2.current(0)
            x2_status = 0
            self.combo_y2.current(3)
            y2_status = 3
            self.combo_x3.current(0)
            x3_status = 0
            self.combo_y3.current(3)
            y3_status = 3
        if sweeper_flag3 == True:
            self.combo_x1.current(0)
            x1_status = 0
            self.combo_y1.current(4)
            y1_status = 4
            self.combo_x2.current(0)
            x2_status = 0
            self.combo_y2.current(4)
            y2_status = 4
            self.combo_x3.current(0)
            x3_status = 0
            self.combo_y3.current(4)
            y3_status = 4
            
        #defining plots initial parameters
        labelsize = 4
        pad = 1

        self.fig221 = Figure(figsize = (1.8, 1), dpi = 300)
        self.ax1 = self.fig221.add_subplot(111)
        self.ax1.tick_params(axis='both', which='major', pad=pad, labelsize = labelsize)

        self.fig222 = Figure(figsize = (1.8, 1), dpi = 300)
        self.ax2 = self.fig222.add_subplot(111)
        self.ax2.tick_params(axis='both', which='major', pad=pad, labelsize = labelsize)

        self.fig223 = Figure(figsize = (1.8, 1), dpi = 300)
        self.ax3 = self.fig223.add_subplot(111)
        self.ax3.tick_params(axis='both', which='major', pad=pad, labelsize = labelsize)

        self.fig224 = Figure(figsize = (1.8, 1), dpi = 300)
        self.ax4 = self.fig224.add_subplot(111)
        self.ax4.tick_params(axis='both', which='major', pad=pad, labelsize = labelsize)    
            
        self.ani221 = animation.FuncAnimation(self.fig221, self.animate221, interval = interval, fargs = self)
        
        plot221 = FigureCanvasTkAgg(self.fig221, self)
        plot221.draw()
        plot221.get_tk_widget().place(relx = 0.02, rely = 0)
        
        toolbar221 = VerticalNavigationToolbar2Tk(plot221, self)
        toolbar221.update()
        toolbar221.place(relx = 0.45, rely = 0)
        plot221._tkcanvas.place(relx = 0.02, rely = 0)
        
        self.ani222 = animation.FuncAnimation(self.fig222, self.animate222, interval = interval, fargs = self)
    
        plot222 = FigureCanvasTkAgg(self.fig222, self)
        plot222.draw()
        plot222.get_tk_widget().place(relx = 0.52, rely = 0)
        
        toolbar222 = VerticalNavigationToolbar2Tk(plot222, self)
        toolbar222.update()
        toolbar222.place(relx = 0.95, rely = 0)
        plot222._tkcanvas.place(relx = 0.52, rely = 0)
        
        self.ani223 = animation.FuncAnimation(self.fig223, self.animate223, interval = interval, fargs = self)
        
        plot223 = FigureCanvasTkAgg(self.fig223, self)
        plot223.draw()
        plot223.get_tk_widget().place(relx = 0.02, rely = 0.50)
        
        toolbar223 = VerticalNavigationToolbar2Tk(plot223, self)
        toolbar223.update()
        toolbar223.place(relx = 0.45, rely = 0.5)
        plot223._tkcanvas.place(relx = 0.02, rely = 0.5)
        
        '''
        self.ani224 = animation.FuncAnimation(self.fig224, self.animate224, interval = 3 * interval, fargs = self)
        plot224 = FigureCanvasTkAgg(self.fig224, self)
        plot224.draw()
        plot224.get_tk_widget().place(relx = 0.52, rely = 0.5)
        
        toolbar224 = VerticalNavigationToolbar2Tk(plot224, self)
        toolbar224.update()
        toolbar224.place(relx = 0.95, rely = 0.5)
        plot224._tkcanvas.place(relx = 0.52, rely = 0.5)
        '''
        
    def animate221(i, self):
    #function to animate graph on each step    
        global x1
        global y1
        global x1_status
        global y1_status
        global columns
        global filename_sweep
        
        try:
            data = pd.read_csv(filename_sweep)
            x1 = data[columns[x1_status]].values
            y1 = data[columns[y1_status]].values
            self.ax1.clear()
            self.ax1.plot(x1, y1, '-', lw = 1, color = 'darkblue')
            print(x1, y1)
        except FileNotFoundError:
            self.ax1.clear()
            self.ax1.plot(x1, y1, '-', lw = 1, color = 'darkblue')
            
        
    def animate222(i, self):
    #function to animate graph on each step    
        global x2
        global y2
        global x2_status
        global y2_status
        global columns
        global filename_sweep
        
        try:
            data = pd.read_csv(filename_sweep)
            x2 = data[columns[x2_status + 1]].values
            y2 = data[columns[y2_status + 1]].values 
            self.ax2.clear()
            self.ax2.plot(x2, y2, '-', lw = 1, color = 'crimson')
        except FileNotFoundError:
            self.ax1.clear()
            self.ax1.plot(x1, y1, '-', lw = 1, color = 'darkblue')
        
    def animate223(i, self):
    #function to animate graph on each step    
        global x3
        global y3
        global x3_status
        global y3_status
        global columns
        global filename_sweep
        
        try:
            data = pd.read_csv(filename_sweep)
            x3 = data[columns[x3_status + 1]].values
            y3 = data[columns[y3_status + 1]].values 
            self.ax3.clear()
            self.ax3.plot(x3, y3, '-', lw = 1, color = 'darkgreen')
        except FileNotFoundError:
            self.ax1.clear()
            self.ax1.plot(x1, y1, '-', lw = 1, color = 'darkblue')

    '''
    def animate224(i, self):
    #function to animate graph on each step    
        global x4
        global y4
        global z4
        try:   
            self.ax4.clear()
            colorbar = self.ax4.imshow(z4, interpolation ='nearest')
            self.ax4.colorbar(colorbar)
            try:
                self.ax4.yticks(np.arange(x4.shape[0], step = x4.shape[0] // 10), 
                              round(x4[::x4.shape[0] // 10], 2))
                self.ax4.xticks(np.arange(y4.shape[0], step = y4.shape[0] // 10), 
                              round(y4[::y4.shape[0] // 10], 2))
            except ZeroDivisionError or ValueError:
                pass
        except:
            pass
    '''
        
    def x1_update(self, event):
        global x1_status
        x1_status = self.combo_x1.current()
        
    def y1_update(self, event):
        global y1_status
        y1_status = self.combo_y1.current()
        
    def x2_update(self, event):
        global x2_status
        x2_status = self.combo_x2.current()
        
    def y2_update(self, event):
        global y2_status
        y2_status = self.combo_y2.current()
        
    def x3_update(self, event):
        global x3_status
        x3_status = self.combo_x3.current()
        
    def y3_update(self, event):
        global y3_status
        y3_status = self.combo_y3.current()
        
interval = 100

def main():
    write_config_parameters()
    write_config_channels()
    Universal_frontend(classes = (StartPage, Lock_in_settings, Sweeper1d, Sweeper2d, Sweeper3d),
                             start = StartPage)
    while True:
        pass
    
if __name__ == '__main__':
    main()