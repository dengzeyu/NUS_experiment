import os
from os.path import exists
cur_dir = os.getcwd() 
import re
import json
from csv import writer
import threading
from tkinter import ttk
import tkinter as tk
from ToolTip import CreateToolTip
import blit_animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                               NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib import style
import pyvisa as visa
from pyvisa import constants
import time
from datetime import datetime
import pandas as pd
import matplotlib
import numpy as np
#import random

matplotlib.use("TkAgg")
plt.rcParams['animation.html'] = 'jshtml'
LARGE_FONT = ('Verdana', 12)
SUPER_LARGE = ('Verdana', 16)
style.use('ggplot')

# Check if everything connected properly
rm = visa.ResourceManager()
list_of_devices = list(rm.list_resources())

'''
temp = rm.open_resource('ASRL3::INSTR', baud_rate=115200,
                        data_bits=8, parity=constants.VI_ASRL_PAR_NONE,
                        stop_bits=constants.VI_ASRL_STOP_ONE,
                        flow_control=constants.VI_ASRL_FLOW_NONE,
                        write_termination='\r', read_termination='\r')
'''

# Write command to a device and get it's output
def get(device, command):
    # return np.round(np.random.random(1), 1)
    return device.query(command)


#print(get(temp, 'IDN?'))

print(rm.list_resources(), '\n')


def var2str(var, vars_data=locals()):
    return [var_name for var_name in vars_data if id(var) == id(vars_data[var_name])][0]

# assigning variables for sweeping

device_to_sweep1 = 'Time'
device_to_sweep2 = 'Time'
device_to_sweep3 = 'Time'
parameter_to_sweep1 = ''
parameter_to_sweep2 = ''
parameter_to_sweep3 = ''
from_sweep1 = float
to_sweep1 = float
ratio_sweep1 = float
delay_factor1 = float
from_sweep2 = float
to_sweep2 = float
ratio_sweep2 = float
delay_factor2 = float
from_sweep3 = float
to_sweep3 = float
ratio_sweep3 = float
delay_factor3 = float

month_dictionary = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', 
                    '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
DAY = datetime.today().strftime('%d')
MONTH = month_dictionary[datetime.today().strftime('%m')]
YEAR = datetime.today().strftime('%Y')[-2:]

filename_sweep = cur_dir + f'\data_files\{DAY}{MONTH}{YEAR}.csv'

settings_flag = False

sweeper_flag1 = False
sweeper_flag2 = False
sweeper_flag3 = False

pause_flag = False
stop_flag = False
tozero_flag = False

condition = ''

manual_sweep_flags = [0]
manual_filenames = [cur_dir + '\data_files\manual' + datetime.today().strftime(
    '%H_%M_%d_%m_%Y') + '.csv']

master_lock = False

back_and_forth_master = 1
back_and_forth_slave = 1
back_and_forth_slave_slave = 1

columns = []

# variables for plotting

cur_animation_num = 1

#creating config files if they were deleted

adress_dictionary_path = cur_dir + '//config//adress_dictionary.txt'
if not exists(adress_dictionary_path):
    with open(adress_dictionary_path, 'w') as file:
        try:
            file.write('{}')
            file.close()
        except:
            file.close()
        finally:
            file.close()  
            
def create_preset(dimension):
    global cur_dir
    dimension = str(dimension)
    globals()['sweeper' + dimension + 'd_path'] = cur_dir + '//config//sweeper' + dimension + 'd_preset.csv'
    if not exists(globals()['sweeper' + dimension + 'd_path']):
        dic = {}
        for i in range(int(dimension)):
             dic['combo_to_sweep' + str(i+1)] = [0]
             dic['sweep_options' + str(i+1)] = [0]
             dic['from' + str(i+1)] = ['']
             dic['to' + str(i+1)] = ['']
             dic['ratio' + str(i+1)] = ['']
             dic['delay_factor' + str(i+1)] = ['']
        dataframe = pd.DataFrame(dic)
        dataframe.to_csv(globals()['sweeper' + dimension + 'd_path'], index = False)

for i in range(3):
    create_preset(i+1)
    
class Time():
    
    def __init__(self, adress = None):
        
        self.set_options = ['Time']
        self.get_options = []
        
    def set_Time(self, value = None):
        print(value)
        pass

class lock_in():

    def __init__(self, adress='GPIB0::3::INSTR'):

        self.sr830 = rm.open_resource(
            adress, write_termination='\n', read_termination='\n')

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

        self.get_options = ['x', 'y', 'r', 'Θ', 'ch1', 'ch2',
                            'AUX1_input', 'AUX2_input', 'AUX3_input', 'AUX4_input']

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
            return [time.perf_counter() - zero_time, self.x, self.y]
        except:
            pass
        # return [time.perf_counter() - zero_time, float(np.random.randint(10)), float(np.random.randint(10))]

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

    def set_ch1_mode(self, mode=0):
        line = 'DDEF1,' + str(mode) + ',0'
        self.sr830.write(line)

    def set_ch2_mode(self, mode=0):
        line = 'DDEF2,' + str(mode) + ',0'
        self.sr830.write(line)

    def set_frequency(self, value=30.0):
        if value < 1e-3:
            value = 1e-3
        line = 'FREQ' + str(value)
        self.sr830.write(line)

    def set_phase(self, value=0.0):
        line = 'PHAS' + str(value)
        self.sr830.write(line)

    def set_amplitude(self, value=0.5):
        if value < 4e-3:
            value = 4e-3
        line = 'SLVL' + str(value)
        self.sr830.write(line)

    def set_sensitivity(self, mode=24):
        line = 'SENS' + str(mode)
        self.sr830.write(line)

    def set_time_constant(self, mode=19):
        line = 'OFLT' + str(mode)
        self.sr830.write(line)

    def set_low_pass_filter_slope(self, mode=3):
        line = 'OFSL' + str(mode)
        self.sr830.write(line)

    def set_synchronous_filter_status(self, mode=0):
        line = 'SYNC' + str(mode)
        self.sr830.write(line)

    def set_remote(self, mode=1):
        line = 'OVRM' + str(mode)
        self.sr830.write(line)

    def set_AUX1_output(self, value=0):
        line = 'AUXV1,' + str(value)
        self.sr830.write(line)

    def set_AUX2_output(self, value=0):
        line = 'AUXV2,' + str(value)
        self.sr830.write(line)

    def set_AUX3_output(self, value=0):
        line = 'AUXV3,' + str(value)
        self.sr830.write(line)

    def set_AUX4_output(self, value=0):
        line = 'AUXV4,' + str(value)
        self.sr830.write(line)

class SourceMeter():
    
    def __init__(self, adress = 'GPIB0::4::INSTR'):
        self.sm = rm.open_resource(
            adress, write_termination='\n', read_termination='\n')
        
        self.sm.write(':SOUR:CLE:AUTO OFF') # auto on/off
        
        self.set_options = {'V', 'I'}
        
        self.get_options = {'v', 'i', 'r'}
        
    def IDN(self):
        return get(self.sm, '*IDN?')
    
    def v(self):
        try:
            answer = get(self.sm, ':MEAS:VOLT?').split(',')[0]
        except ValueError:
            answer = get(self.sm, ':MEAS:VOLT?').split(',')[0]
        return answer
        
    def i(self):
        try:
            answer = get(self.sm, ':MEAS:CURR?').split(',')[1]
        except ValueError:
            answer = get(self.sm, ':MEAS:CURR?').split(',')[1]
        return answer
        
    def r(self):
        try:
            answer = get(self.sm, ':MEAS:RES?').split(',')[2]
        except ValueError:
            answer = get(self.sm, ':MEAS:RES?').split(',')[2]
        return answer
    
    def set_I(self, value = 0):
        self.sm.write(':SOUR:CURR ' + str(value))
        
    def set_V(self, value = 0):
        self.sm.write(':SOUR:VOLT ' + str(value))

class TC300():

    def __init__(self, adress='ASRL3::INSTR'):
        self.tc = rm.open_resource(adress, baud_rate=115200,
                                   data_bits=8, parity=constants.VI_ASRL_PAR_NONE,
                                   stop_bits=constants.VI_ASRL_STOP_ONE,
                                   flow_control=constants.VI_ASRL_FLOW_NONE,
                                   write_termination='\r', read_termination='\r')

        self.set_options = {'T1', 'T2'}

        self.get_options = {'t1', 't2'}
        
    def IDN(self):
        return(get(self.tc, 'IDN?')[2:])

    def t1(self):
        # Get the CH1 target temperature; returned value is the actual temperature in °C
        value_str = get(self.tc, 'TACT1?')
        value_float = re.findall(r'\d*\.\d+|\d+', value_str)
        try:
            value_float = [float(i) for i in value_float][0]
        except IndexError:
            try:
                value_str = get(self.tc, 'TACT1?')
                value_float = re.findall(r'\d*\.\d+|\d+', value_str)
                value_float = [float(i) for i in value_float][0]
            except IndexError:
                value_float = np.nan
        return value_float

    def set_T1(self, value=20):
        # Set the CH1 target temperature to value/10 °C, the range is defined by
        # TMIN1 and TMAX1, the setting resolution of value is 1.
        self.tc.write('EN1=1')
        self.tc.write('TSET1=' + str(int(value * 10)))

    def set_T1_from(self, t1_from=0):
        # Set the CH1 Target Temperature Min value,
        # (Range: -200 to TMAX1°C, with a resolution of 1°C).
        self.tc.write('TMIN1=' + str(t1_from))

    def set_T1_to(self, t1_to=30):
        # Set the CH1 Target Temperature Max value, n equals value
        # TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t1_to))

    def t2(self):
        # Get the CH2 target temperature; returned value is the actual temperature in °C
        value_str = get(self.tc, 'TACT2?')
        if value_str == '':
            value_str = get(self.tc, 'TACT2?')
        value_float = re.findall(r'\d*\.\d+|\d+', value_str)
        value_float = [float(i) for i in value_float]
        return(value_float[0])

    def set_T2(self, value=20):
        # Set the CH2 target temperature to value/10 °C, the range is defined by
        # TMIN1 and TMAX1, the setting resolution of value is 1.
        self.tc.write('EN2=1')
        self.tc.write('TSET2=' + str(int(value * 10)))

    def set_T2_from(self, t2_from=0):
        # Set the CH2 Target Temperature Min value,
        # (Range: -200 to TMAX2°C, with a resolution of 1°C).
        self.tc.write('TMIN1=' + str(t2_from))

    def set_T2_to(self, t2_to=20):
        # Set the CH2 Target Temperature Max value, n equals value
        # TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t2_to))


device_classes = (lock_in, TC300, SourceMeter)


def devices_list():
    # queries each device IDN?
    list_of_devices = []
    types_of_devices = []
    for adress in rm.list_resources():
        try:
            try:
                name = get(rm.open_resource(
                    adress, read_termination='\r'), 'IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                if name == '':
                    raise UserWarning
            except UserWarning:
                name = get(rm.open_resource(
                    adress, read_termination='\n'), 'IDN?')
                if name.startswith('\n'):
                    name = name[2:]
        except visa.errors.VisaIOError:
            try:
                name = get(rm.open_resource(
                    adress, read_termination='\n'), '*IDN?')
                if name.startswith('\n'):
                    name = name[2:]
                if name == '':
                    raise UserWarning
            except UserWarning:
                name = get(rm.open_resource(
                    adress, read_termination='\r'), '*IDN?')
                if name.startswith('\n'):
                    name = name[2:]
        list_of_devices.append(name)

        for class_of_device in device_classes:
            if globals()[var2str(class_of_device)]().IDN() == name:
                types_of_devices.append(var2str(class_of_device))
        if len(types_of_devices) != len(list_of_devices):
            types_of_devices.append('Not a class')

    return list_of_devices, types_of_devices

if len(list_of_devices) == 0:
    list_of_devices = ['']
    
try:
    names_of_devices, types_of_devices = devices_list()
    print(names_of_devices, types_of_devices)
except:
    types_of_devices = []
    for i in range (len(list_of_devices)):
        types_of_devices.append('Not a class')
        
list_of_devices.insert(0, 'Time')
types_of_devices.insert(0, 'Time')
        
with open(cur_dir + '\\config\\adress_dictionary.txt', 'r') as file:
    adress_dict = file.read()
adress_dict = json.loads(adress_dict)
    
for ind_, type_ in enumerate(types_of_devices):
    if type_ == 'Not a class':
        if list_of_devices[ind_] in list(adress_dict.keys()):
            types_of_devices[ind_] = adress_dict[list_of_devices[ind_]]
        

def new_parameters_to_read(types_of_devices = types_of_devices):
    global list_of_devices
    parameters_to_read = []
    for device_type in types_of_devices:
        if device_type == 'Not a class':
            pass
        else:
            adress = list_of_devices[types_of_devices.index(device_type)]
            get_options = getattr(globals()[device_type](
                adress=adress), 'get_options')
            for option in get_options:
                parameters_to_read.append(adress + '.' + option)
    return parameters_to_read
                
parameters_to_read = new_parameters_to_read()

zero_time = time.perf_counter()

def my_animate_initial(n):
    # function to animate graph on first step
    ax = globals()[f'ax{n}']
    line, = ax.plot([0], [0])
    line.set_data([0], [0])
    return line,

def my_animate(i, n):
    # function to animate graph on each step
    
    global columns
    global filename_sweep
    global x_transformation
    global y_transformation
    
    if n%3 == 1:
        color = 'darkblue'
    elif n%3 == 2:
        color = 'darkgreen'
    elif n%3 == 0:
        color = 'crimson'
    else:
        color = 'black'

    data = pd.read_csv(filename_sweep)
    globals()[f'x{n}'] = data[columns[globals()[f'x{n}_status']]].values
    globals()[f'y{n}'] = data[columns[globals()[f'y{n}_status']]].values
    x = globals()[f'x{n}']
    y = globals()[f'y{n}']
    
    try:
        x = eval(globals()[f'x_transformation{n}'], locals())
    except:
        pass
    
    try:
        y = eval(globals()[f'y_transformation{n}'], locals())
    except:
        pass
    
    ax = globals()[f'ax{n}']
    
    xscale_status = ax.get_xscale()
    yscale_status = ax.get_yscale()
    xlabel = ax.get_xlabel()
    ylabel = ax.get_ylabel()
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    ax.clear()
    ax.set_xscale(xscale_status)
    ax.set_yscale(yscale_status)
    getattr(Graph, 'axes_settings')(i, n)
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.autoscale(enable = globals()[f'x{n}_autoscale'], axis = 'x')
    ax.autoscale(enable = globals()[f'y{n}_autoscale'], axis = 'y')
    
    ax.plot(x, y, '-', lw=1, color=color)
    
    globals()[f'graph_object{globals()["cur_animation_num"] - 3}'].update()
    globals()[f'graph_object{globals()["cur_animation_num"] - 3}'].update_idletasks()
    return [ax]

zero_time = time.perf_counter()

class Universal_frontend(tk.Tk):

    def __init__(self, classes, start, size = '1920x1080', title = 'Lock in test', *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self)
        tk.Tk.geometry(self, newGeometry = size)
        tk.Tk.wm_title(self, title)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand='True')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in classes:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(start)

    def show_frame(self, cont):
        global settings_flag
        frame = self.frames[cont]
        frame.tkraise()
        if settings_flag == True:
            globals()['Sweeper_object'] = frame
            settings_flag = False

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text='Start Page', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        sweeper1d_button = tk.Button(
            self, text='1D - sweeper', command=lambda: self.sweeper1d_show())
        sweeper1d_button.place(relx=0.1, rely=0.4)

        sweeper2d_button = tk.Button(
            self, text='2D - sweeper', command=lambda: self.sweeper2d_show())
        sweeper2d_button.place(relx=0.2, rely=0.4)

        sweeper3d_button = tk.Button(
            self, text='3D - sweeper', command=lambda: self.sweeper3d_show())
        sweeper3d_button.place(relx=0.3, rely=0.4)
    
    def sweeper1d_show(self):
        global settings_flag
        settings_flag = True
        self.controller.show_frame(Sweeper1d)
        
    def sweeper2d_show(self):
        global settings_flag
        settings_flag = True
        self.controller.show_frame(Sweeper2d)
        
    def sweeper3d_show(self):
        global settings_flag
        settings_flag = True
        self.controller.show_frame(Sweeper3d)

class Sweeper1d(tk.Frame):

    def __init__(self, parent, controller):       

        tk.Frame.__init__(self, parent)
        
        self.preset = pd.read_csv(globals()['sweeper1d_path'], sep = ',')
        self.preset = self.preset.fillna('')
        self.combo_to_sweep1_current = int(self.preset['combo_to_sweep1'].values[0])
        self.sweep_options1_current = int(self.preset['sweep_options1'].values[0])
        self.from1_init = self.preset['from1'].values[0]
        self.to1_init = self.preset['to1'].values[0]
        self.ratio1_init = self.preset['ratio1'].values[0]
        self.delay_factor1_init = self.preset['delay_factor1'].values[0]
        

        label = tk.Label(self, text='1dSweeper', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button_home = tk.Button(self, text='Back to Home',
                                 command=lambda: controller.show_frame(StartPage))
        button_home.pack()

        label_to_sweep = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep.place(relx=0.15, rely=0.12)

        label_to_read = tk.Label(self, text='To read:', font=LARGE_FONT)
        label_to_read.place(relx=0.3, rely=0.12)

        label_devices = tk.Label(self, text = 'Devices:', font = LARGE_FONT)
        label_devices.place(relx = 0.05, rely = 0.16)

        self.combo_to_sweep1 = ttk.Combobox(
            self, value=list_of_devices)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters)
        self.combo_to_sweep1.place(relx=0.15, rely=0.16)

        self.status_back_and_forth_master = tk.IntVar(value = 0)
        
        global back_and_forth_master
        
        back_and_forth_master = 1
        
        self.back_and_forth_master_count = 2
    
        self.checkbox_back_and_forth_master = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_master, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_master_status())
        self.checkbox_back_and_forth_master.place(relx=0.23, rely=0.56)
        
        label_back_and_forth_master = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_master.place(relx = 0.2435, rely = 0.55)
        CreateToolTip(label_back_and_forth_master, 'Back and forth sweep\nfor this axis')

        self.devices = tk.StringVar()
        self.devices.set(value=parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable = self.devices,
                                         selectmode='multiple', width=20,
                                         height=len(parameters_to_read) * 1)
        self.lstbox_to_read.place(relx=0.3, rely=0.16)
        
        self.dict_lstbox = {}
        
        for parameter in parameters_to_read:
            self.dict_lstbox[parameter] = parameter
            
        lstbox_height = len(parameters_to_read) / 47
        
        button_update_sweep = tk.Button(self, text = 'Update sweep', command = lambda: self.update_sweep_configuration())
        button_update_sweep.place(relx = 0.3, rely = 0.21 + lstbox_height)

        self.button_pause = tk.Button(self, text = '⏸️', font = LARGE_FONT, command = lambda: self.pause())
        self.button_pause.place(relx = 0.3, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_pause, 'Pause\continue sweep')
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.3375, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_stop, 'Stop sweep')
        
        button_start_sweeping = tk.Button(
            self, text="▶", command=lambda: self.start_sweeping(), font = LARGE_FONT)
        button_start_sweeping.place(relx=0.375, rely=0.21, height= 90, width=30)
        CreateToolTip(button_start_sweeping, 'Start sweeping')
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.3, rely = 0.3 + lstbox_height)

        label_options = tk.Label(self, text = 'Options:', font = LARGE_FONT)
        label_options.place(relx = 0.05, rely = 0.2)
        

        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.2)
        
        try:
            self.combo_to_sweep1.current(self.combo_to_sweep1_current)
            self.update_sweep_parameters(event = None)
        except:
            self.combo_to_sweep1.current(0)
            if self.combo_to_sweep1['values'][0] != '':
                self.update_sweep_parameters(event = None)

        label_from = tk.Label(self, text='From', font=LARGE_FONT)
        label_from.place(relx=0.12, rely=0.24)

        label_to = tk.Label(self, text='To', font=LARGE_FONT)
        label_to.place(relx=0.12, rely=0.28)

        label_step = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step.place(relx=0.12, rely=0.32)
        CreateToolTip(label_step, 'Speed of 1d-sweep')

        self.entry_from = tk.Entry(self)
        self.entry_from.insert(0, self.from1_init)
        self.entry_from.place(relx=0.17, rely=0.24)

        self.entry_to = tk.Entry(self)
        self.entry_to.insert(0, self.to1_init)
        self.entry_to.place(relx=0.17, rely=0.28)

        self.entry_ratio = tk.Entry(self)
        self.entry_ratio.insert(0, self.ratio1_init)
        self.entry_ratio.place(relx=0.17, rely=0.32)

        label_delay_factor = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor.place(relx=0.12, rely=0.4)
        CreateToolTip(label_delay_factor, 'Sleep time per 1 point')

        self.entry_delay_factor = tk.Entry(self)
        self.entry_delay_factor.insert(0, self.delay_factor1_init)
        self.entry_delay_factor.place(relx=0.12, rely=0.46)

        # section of manual sweep points selection
        self.status_manual = tk.IntVar()
        self.filename = filename_sweep[:-4] + '_manual' + '.csv'
            
        # initials
        self.manual_sweep_flags = [0]
        self.manual_filenames = [self.filename]

        self.checkbox_manual1 = ttk.Checkbutton(self, text='Maunal sweep select',
                                          variable=self.status_manual, onvalue=1,
                                          offvalue=0, command=lambda: self.save_manual_status())
        self.checkbox_manual1.place(relx=0.12, rely=0.52)

        button_new_manual = tk.Button(self, text = '🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0]))
        button_new_manual.place(relx=0.12, rely=0.56)
        CreateToolTip(button_new_manual, 'Create new sweep instruction')

        button_explore_manual = tk.Button(
            self, text = '🔎', font = LARGE_FONT, command=lambda: self.explore_files())
        button_explore_manual.place(relx=0.15, rely=0.56)
        CreateToolTip(button_explore_manual, 'Explore existing sweep instruction')

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        self.script = ''

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)
        CreateToolTip(button_settings, 'Settings')

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.7, rely=0.76)
        CreateToolTip(graph_button, 'Graph')

    def update_sweep_parameters(self, event, interval=100):
        global types_of_devices
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current()]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(
                globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.current(self.sweep_options1_current)
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)
            
        if self.combo_to_sweep1.current() != self.combo_to_sweep1_current:
            self.preset.loc[0, 'combo_to_sweep1'] = self.combo_to_sweep1.current()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
            
    def update_sweep_options(self):
        if self.sweep_options1.current() != self.sweep_options1_current:
            self.preset.loc[0, 'sweep_options1'] = self.sweep_options1.current()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
            
    def rewrite_preset(self):
        if self.entry_from.get() != self.from1_init:
            self.preset.loc[0, 'from1'] = self.entry_from.get()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
        if self.entry_to.get() != self.to1_init:
            self.preset.loc[0, 'to1'] = self.entry_to.get()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
        if self.entry_ratio.get() != self.ratio1_init:
            self.preset.loc[0, 'ratio1'] = self.entry_ratio.get()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
        if self.entry_delay_factor.get() != self.delay_factor1_init:
            self.preset.loc[0, 'delay_factor1'] = self.entry_delay_factor.get()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)

    def update_sweep_configuration(self):
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        
        try:
            from_sweep1 = float(self.entry_from.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_to.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep1 = float(self.entry_ratio.get())
        except ValueError:
            pass
        
        try:
            delay_factor1 = float(self.entry_delay_factor.get())
        except ValueError:
            pass
        
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
            
        self.rewrite_preset()
    
    def save_manual_status(self):
        if self.manual_sweep_flags[0] != self.status_manual.get():
            self.manual_sweep_flags[0] = self.status_manual.get()

    def save_back_and_forth_master_status(self):
        global back_and_forth_master
        
        if self.status_back_and_forth_master == 0:
            back_and_forth_master = 1
        else:
            back_and_forth_master = self.back_and_forth_master_count

    def open_blank(self, filename):
        df = pd.DataFrame(columns=['steps'])
        df.to_csv(filename, index=False)
        self.manual_filenames[0] = filename
        os.startfile(filename)

    def explore_files(self):
        self.manual_filenames[0] = tk.filedialog.askopenfilename(initialdir=cur_dir + '',
                                                                 title='Select a manual sweeper',
                                                                 filetypes=(('CSV files', '*.csv*'),
                                                                            ('all files', '*.*')))

    def set_filename_sweep(self):
        global filename_sweep

        filename_sweep = tk.filedialog.asksaveasfilename(title='Save the file',
                                                         initialfile=cur_dir + '\data_files\sweep' + datetime.today().strftime(
                                                             '%H_%M_%d_%m_%Y'),
                                                         defaultextension='.csv')
        
        self.entry_filename.delete(0, tk.END)
        self.entry_filename.insert(0, filename_sweep)
        self.entry_filename.after(1)

    def open_settings(self):        
        self.window_settings = Universal_frontend((Settings,), Settings)
        self.window_settings.mainloop()

    def open_graph(self):
        
        global cur_animation_num
        
        def return_range(x, n):
            if x % n == 0:
                return [x + p for p in range(n)]
            elif x % n == n - 1:
                return [x - p for p in range(n)][::-1]
            else:
                return return_range(x + 1, n)
        
        globals()[f'graph_object{globals()["cur_animation_num"]}'] = Graph()
        for i in return_range(cur_animation_num, 3):
            globals()[f'x{i + 1}'] = []
            globals()[f'x{i + 1}_status'] = 0
            globals()[f'y{i + 1}'] = []
            globals()[f'y{i + 1}_status'] = 0
            globals()[f'ani{i+1}'] = StartAnimation
            globals()[f'ani{i+1}'].start()
        
    def pause(self):
        global pause_flag
        
        def update_button_text():
            if self.button_pause['text'] == '⏸️':
                self.button_pause['text'] = '▶️'
            if self.button_pause['text'] == '▶️':
                self.button_pause['text'] = '⏸️'
        
        pause_flag = not(pause_flag)
        
        self.button_pause.after(100, update_button_text())
                
        tk.Frame(self).update_idletasks()
        tk.Frame(self).update()
        
        
    def stop(self):
        
        global stop_flag
        
        stop_flag = True
        
    def tozero(self):
        
        global tozero_flag
        
        tozero_flag = True

    def start_sweeping(self):

        global list_of_devices
        global types_of_devices
        global device_to_sweep1
        global parameter_to_sweep1
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global parameters_to_read
        global filename_sweep
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global stop_flag
        global columns
        global script
        global manual_filenames
        global manual_sweep_flags
        global zero_time

        def get_key(val, my_dict):
            for key, value in my_dict.items():
                if val == value:
                    return key
        
        self.list_to_read = []
        # asking multichoise to get parameters to read
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(get_key(entrada, self.dict_lstbox))
        parameters_to_read = self.list_to_read

        self.rewrite_preset()

        # creating columns
        device_to_sweep1 = list_of_devices[self.combo_to_sweep1.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep1)]](), 'set_options')
        parameter_to_sweep1 = parameters[self.sweep_options1.current()]
        columns = ['time', device_to_sweep1 + '.' + parameter_to_sweep1]
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_from.get() != '':
            from_sweep1 = float(self.entry_from.get())
        if self.entry_to.get() != '':
            to_sweep1 = float(self.entry_to.get())
        if self.entry_ratio.get() != '':
            ratio_sweep1 = float(self.entry_ratio.get())
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = - ratio_sweep1
        if self.entry_delay_factor.get() != '':
            delay_factor1 = float(self.entry_delay_factor.get())
        if self.entry_filename.get() != '':
            filename_sweep = self.entry_filename.get()
        sweeper_flag1 = True
        sweeper_flag2 = False
        sweeper_flag3 = False
        manual_filenames = self.manual_filenames
        manual_sweep_flags = self.manual_sweep_flags
        script = self.script

        zero_time = time.perf_counter()
        stop_flag = False
        Sweeper_write()
        self.open_graph()


class Sweeper2d(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        
        self.preset = pd.read_csv(globals()['sweeper2d_path'], sep = ',')
        self.preset = self.preset.fillna('')
        self.combo_to_sweep1_current = int(self.preset['combo_to_sweep1'].values[0])
        self.sweep_options1_current = int(self.preset['sweep_options1'].values[0])
        self.combo_to_sweep2_current = int(self.preset['combo_to_sweep2'].values[0])
        self.sweep_options2_current = int(self.preset['sweep_options2'].values[0])
        self.from1_init = self.preset['from1'].values[0]
        self.to1_init = self.preset['to1'].values[0]
        self.ratio1_init = self.preset['ratio1'].values[0]
        self.delay_factor1_init = self.preset['delay_factor1'].values[0]
        self.from2_init = self.preset['from2'].values[0]
        self.to2_init = self.preset['to2'].values[0]
        self.ratio2_init = self.preset['ratio2'].values[0]
        self.delay_factor2_init = self.preset['delay_factor2'].values[0]
        
        
        label = tk.Label(self, text='2dSweeper', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button_home = tk.Button(self, text='Back to Home',
                                 command=lambda: controller.show_frame(StartPage))
        button_home.pack()

        label_to_sweep1 = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep1.place(relx=0.15, rely=0.12)
    
        label_to_sweep2 = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep2.place(relx=0.3, rely=0.12)
    
        label_to_read = tk.Label(self, text='To read:', font=LARGE_FONT)
        label_to_read.place(relx=0.45, rely=0.12)
        
        label_hierarchy = tk.Label(self, text = 'Hierarchy:', font=LARGE_FONT)
        label_hierarchy.place(relx = 0.05, rely = 0.17)
        
        self.master_option = ['', 'Master', 'Slave']

        self.combo_master1 = ttk.Combobox(self, value = self.master_option)
        self.combo_master1.bind(
            "<<ComboboxSelected>>", self.update_master2_combo)
        self.combo_master1.place(relx = 0.15, rely = 0.17)
        
        self.combo_master2 = ttk.Combobox(self, value = self.master_option)
        self.combo_master2.bind(
            "<<ComboboxSelected>>", self.update_master1_combo)
        self.combo_master2.place(relx = 0.3, rely = 0.17)

        label_devices = tk.Label(self, text = 'Devices:', font=LARGE_FONT)
        label_devices.place(relx = 0.05, rely = 0.21)

        self.combo_to_sweep1 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx=0.15, rely=0.21)
        
        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.25)

        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx=0.3, rely=0.25)
        
        try:
            self.combo_to_sweep1.current(self.combo_to_sweep1_current)
            self.update_sweep_parameters1(event = None)
        except:
            self.combo_to_sweep1.current(0)
            if self.combo_to_sweep1['values'][0] != '':
                self.update_sweep_parameters1(event = None)

        self.combo_to_sweep2 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep2.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx=0.3, rely=0.21)
        
        try:
            self.combo_to_sweep2.current(self.combo_to_sweep2_current)
            self.update_sweep_parameters2(event = None)
        except:
            self.combo_to_sweep2.current(0)
            if self.combo_to_sweep2['values'][0] != '':
                self.update_sweep_parameters2(event = None)
        
        self.status_back_and_forth_slave = tk.IntVar(value = 0)
        self.status_back_and_forth_master = tk.IntVar(value = 0)
        
        global back_and_forth_master
        global back_and_forth_slave
        
        back_and_forth_master = 1
        back_and_forth_slave = 1
        
        self.back_and_forth_master = 2
        self.back_and_forth_slave_count = 2
    
        self.checkbox_back_and_forth_master = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_master, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_master_status())
        self.checkbox_back_and_forth_master.place(relx=0.22, rely=0.61)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.2335, rely = 0.6)
        CreateToolTip(label_back_and_forth_slave, 'Back and forth sweep\nfor this axis')

        self.checkbox_back_and_forth_slave = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_slave, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_slave_status())
        self.checkbox_back_and_forth_slave.place(relx=0.38, rely=0.61)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.3935, rely = 0.6)
        CreateToolTip(label_back_and_forth_slave, 'Back and forth sweep\nfor this axis')
    
        devices = tk.StringVar()
        devices.set(value=parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable=devices,
                                         selectmode='multiple', width=20,
                                         height=len(parameters_to_read) * 1)
        self.lstbox_to_read.place(relx=0.45, rely=0.17)
        
        self.dict_lstbox = {}
        
        for parameter in parameters_to_read:
            self.dict_lstbox[parameter] = parameter
            
        lstbox_height = len(parameters_to_read) / 47
        
        button_update_sweep = tk.Button(self, text = 'Update sweep', command = lambda: self.update_sweep_configuration())
        button_update_sweep.place(relx = 0.45, rely = 0.21 +  lstbox_height)

        self.button_pause = tk.Button(self, text = '⏸️', font = LARGE_FONT, command = lambda: self.pause())
        self.button_pause.place(relx = 0.45, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_pause, 'Pause\Continue sweep')
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.4875, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_stop, 'Stop sweep')
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.45, rely = 0.3 + lstbox_height)
        
        button_start_sweeping = tk.Button(
            self, text="▶", command=lambda: self.start_sweeping(), font = LARGE_FONT)
        button_start_sweeping.place(relx=0.525, rely=0.21 + lstbox_height, height= 90, width=30)
        CreateToolTip(button_start_sweeping, 'Start sweeping')

        label_options = tk.Label(self, text = 'Options:', font=LARGE_FONT)
        label_options.place(relx = 0.05, rely = 0.25)

        label_from1 = tk.Label(self, text='From', font=LARGE_FONT)
        label_from1.place(relx=0.12, rely=0.29)

        label_to1 = tk.Label(self, text='To', font=LARGE_FONT)
        label_to1.place(relx=0.12, rely=0.33)

        label_step1 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step1.place(relx=0.12, rely=0.37)
        CreateToolTip(label_step1, 'Speed of 1d-sweep')

        self.entry_from1 = tk.Entry(self)
        self.entry_from1.insert(0, self.from1_init)
        self.entry_from1.place(relx=0.17, rely=0.29)

        self.entry_to1 = tk.Entry(self)
        self.entry_to1.insert(0, self.to1_init)
        self.entry_to1.place(relx=0.17, rely=0.33)

        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.insert(0, self.ratio1_init)
        self.entry_ratio1.place(relx=0.17, rely=0.37)

        label_delay_factor1 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor1.place(relx=0.12, rely=0.45)
        CreateToolTip(label_delay_factor1, 'Sleep time per 1 point')

        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.insert(0, self.delay_factor1_init)
        self.entry_delay_factor1.place(relx=0.12, rely=0.51)

        label_from2 = tk.Label(self, text='From', font=LARGE_FONT)
        label_from2.place(relx=0.27, rely=0.29)

        label_to2 = tk.Label(self, text='To', font=LARGE_FONT)
        label_to2.place(relx=0.27, rely=0.33)

        label_step2 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step2.place(relx=0.27, rely=0.37)
        CreateToolTip(label_step2, 'Speed of 1d-sweep')

        self.entry_from2 = tk.Entry(self)
        self.entry_from2.insert(0, self.from2_init)
        self.entry_from2.place(relx=0.32, rely=0.29)

        self.entry_to2 = tk.Entry(self)
        self.entry_to2.insert(0, self.to2_init)
        self.entry_to2.place(relx=0.32, rely=0.33)

        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.insert(0, self.ratio2_init)
        self.entry_ratio2.place(relx=0.32, rely=0.37)

        label_delay_factor2 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor2.place(relx=0.27, rely=0.45)
        CreateToolTip(label_delay_factor2, 'Sleep time per 1 point')

        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.insert(0, self.delay_factor2_init)
        self.entry_delay_factor2.place(relx=0.27, rely=0.51)

        # section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        self.filename = filename_sweep[:-4] + '_manual' + '.csv'

        # initials

        self.manual_sweep_flags = [0, 0]
        self.manual_filenames = [self.filename[:-4] +
                                 '1.csv', self.filename[:-4] + '2.csv']

        self.checkbox_manual1 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual1, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=1))
        self.checkbox_manual1.place(relx=0.12, rely=0.57)

        button_new_manual1 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0], i=1))
        button_new_manual1.place(relx=0.12, rely=0.6)
        CreateToolTip(button_new_manual1, 'Create new sweep instruction')

        button_explore_manual1 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=0))
        button_explore_manual1.place(relx=0.15, rely=0.6)
        CreateToolTip(button_explore_manual1, 'Explore existing sweep instruction')

        self.checkbox_manual2 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual2, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=2))
        self.checkbox_manual2.place(relx=0.27, rely=0.57)

        button_new_manual2 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[1], i=0))
        button_new_manual2.place(relx=0.27, rely=0.6)
        CreateToolTip(button_new_manual2, 'Create new sweep instruction')

        button_explore_manual2 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=1))
        button_explore_manual2.place(relx=0.3, rely=0.6)
        CreateToolTip(button_explore_manual2, 'Explore existing sweep instruction')
        
        label_condition = tk.Label(self, text = 'Constraints:', font = LARGE_FONT)
        label_condition.place(relx = 0.12, rely = 0.66)
        CreateToolTip(label_condition, 'Master sweep: x\nSlave sweep: y\nSet condition for a sweep map')
        
        self.text_condition = tk.Text(self, width = 40, height = 7)
        self.text_condition.place(relx = 0.12, rely = 0.7)

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        self.script = ''

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)
        CreateToolTip(button_settings, 'Settings')

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.7, rely=0.8)
        CreateToolTip(graph_button, 'Graph')
        
    def update_master2_combo(self, event, interval = 100):
        if self.combo_master1['value'][self.combo_master1.current()] == '':
            self.combo_master2['value'] = self.master_option
            self.combo_master2.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master':
            self.combo_master2['value'] = ['', 'Slave']
            self.combo_master2.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave':
            self.combo_master2['value'] = ['', 'Master']
            self.combo_master2.after(interval)
            
    def update_master1_combo(self, event, interval = 100):
        if self.combo_master2['value'][self.combo_master1.current()] == '':
            self.combo_master1['value'] = self.master_option
            self.combo_master1.after(interval)
        if self.combo_master2['value'][self.combo_master1.current()] == 'Master':
            self.combo_master1['value'] = ['', 'Slave']
            self.combo_master1.after(interval)
        if self.combo_master2['value'][self.combo_master1.current()] == 'Slave':
            self.combo_master1['value'] = ['', 'Master']
            self.combo_master1.after(interval)

    def update_sweep_parameters1(self, event, interval=100):
        global types_of_devices
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current()]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(
                globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.current(self.sweep_options1_current)
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)
            
        if self.combo_to_sweep1.current() != self.combo_to_sweep1_current:
            self.preset.loc[0, 'combo_to_sweep1'] = self.combo_to_sweep1.current()
            self.preset.to_csv(globals()['sweeper1d_path'], index = False)
            
    def update_sweep_options1(self):
        if self.sweep_options1.current() != self.sweep_options1_current:
            self.preset.loc[0, 'sweep_options1'] = self.sweep_options1.current()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)

    def update_sweep_parameters2(self, event, interval=100):
        global types_of_devices
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current()]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(
                globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.current(self.sweep_options2_current)
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)
            
        if self.combo_to_sweep2.current() != self.combo_to_sweep2_current:
            self.preset.loc[0, 'combo_to_sweep2'] = self.combo_to_sweep2.current()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
            
    def update_sweep_options2(self):
        if self.sweep_options2.current() != self.sweep_options2_current:
            self.preset.loc[0, 'sweep_options2'] = self.sweep_options2.current()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
            
    def rewrite_preset(self):
        if self.entry_from1.get() != self.from1_init:
            self.preset.loc[0, 'from1'] = self.entry_from1.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_to1.get() != self.to1_init:
            self.preset.loc[0, 'to1'] = self.entry_to1.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_ratio1.get() != self.ratio1_init:
            self.preset.loc[0, 'ratio1'] = self.entry_ratio1.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_delay_factor1.get() != self.delay_factor1_init:
            self.preset.loc[0, 'delay_factor1'] = self.entry_delay_factor1.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_from2.get() != self.from2_init:
            self.preset.loc[0, 'from2'] = self.entry_from2.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_to2.get() != self.to2_init:
            self.preset.loc[0, 'to2'] = self.entry_to2.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_ratio2.get() != self.ratio2_init:
            self.preset.loc[0, 'ratio2'] = self.entry_ratio2.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)
        if self.entry_delay_factor2.get() != self.delay_factor2_init:
            self.preset.loc[0, 'delay_factor2'] = self.entry_delay_factor2.get()
            self.preset.to_csv(globals()['sweeper2d_path'], index = False)

    def update_sweep_configuration(self):
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global from_sweep2
        global to_sweep2
        global ratio_sweep2
        global delay_factor2
        
        try:
            from_sweep1 = float(self.entry_from1.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_to1.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep1 = float(self.entry_ratio1.get())
        except ValueError:
            pass
        
        try:
            delay_factor1 = float(self.entry_delay_factor1.get())
        except ValueError:
            pass
        
        try:
            from_sweep2 = float(self.entry_from2.get())
        except ValueError:
            pass
        
        try:
            to_sweep2 = float(self.entry_to2.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep2 = float(self.entry_ratio2.get())
        except ValueError:
            pass
        
        try:
            delay_factor2 = float(self.entry_delay_factor2.get())
        except ValueError:
            pass
        
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
            
        if from_sweep2 > to_sweep2 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
            
        self.rewrite_preset()

    def save_manual_status(self, i):
        if self.manual_sweep_flags[i - 1] != getattr(self, 'status_manual' + str(i)).get():
            self.manual_sweep_flags[i -
                                    1] = getattr(self, 'status_manual' + str(i)).get()
            
    def save_back_and_forth_master_status(self):
        global back_and_forth_master
        
        if self.status_back_and_forth_slave == 0:
            back_and_forth_master = 1
        else:
            back_and_forth_master = self.back_and_forth_master_count
            
    def save_back_and_forth_slave_status(self):
        global back_and_forth_slave
        
        if self.status_back_and_forth_slave == 0:
            back_and_forth_slave = 1
        else:
            back_and_forth_slave = self.back_and_forth_slave_count
            
    def save_back_and_forth_slave_slave_status(self):
        global back_and_forth_slave_slave
        
        if self.status_back_and_forth_slave_slave == 0:
            back_and_forth_slave_slave = 1
        else:
            back_and_forth_slave_slave = self.back_and_forth_slave_slave_count
    
    def open_blank(self, filename, i):
        df = pd.DataFrame(columns=['steps'])
        df.to_csv(filename, index=False)
        self.manual_filenames[i] = filename
        os.startfile(filename)

    def open_settings(self):        
        self.window_settings = Universal_frontend((Settings,), Settings)
        self.window_settings.mainloop()

    def explore_files(self, i):
        self.manual_filenames[i] = tk.filedialog.askopenfilename(initialdir=cur_dir,
                                                                 title='Select a manual sweeper',
                                                                 filetypes=(('CSV files', '*.csv*'),
                                                                            ('all files', '*.*')))

    def set_filename_sweep(self):
        global filename_sweep

        filename_sweep = tk.filedialog.asksaveasfilename(title='Save the file',
                                                         initialfile=cur_dir + '\data_files\sweep' + datetime.today().strftime(
                                                             '%H_%M_%d_%m_%Y'),
                                                         defaultextension='.csv')
        
        self.entry_filename.delete(0, tk.END)
        self.entry_filename.insert(0, filename_sweep)
        self.entry_filename.after(1)

    def open_graph(self):
        global cur_animation_num
        
        def return_range(x, n):
            if x % n == 0:
                return [x + p for p in range(n)]
            elif x % n == n - 1:
                return [x - p for p in range(n)][::-1]
            else:
                return return_range(x + 1, n)
        
        self.window = Universal_frontend(classes=(Graph,), start=Graph)
        for i in return_range(cur_animation_num, 3):
            globals()[f'x{i + 1}'] = []
            globals()[f'x{i + 1}_status'] = 0
            globals()[f'y{i + 1}'] = []
            globals()[f'y{i + 1}_status'] = 0
            globals()[f'ani{i+1}'] = StartAnimation
            globals()[f'ani{i+1}'].start()
        self.window.mainloop()
        
    def pause(self):
        global pause_flag
        
        pause_flag = not(pause_flag)
        
        if self.button_pause['text'] == '⏸️':
            self.button_pause['text'] = '▶️'
        if self.button_pause['text'] == '▶️':
            self.button_pause['text'] = '⏸️'
            
        self.button_pause.after(1000)
        
    def stop(self):
        
        global stop_flag
        
        stop_flag = True
        
    def tozero(self):
        
        global tozero_flag
        
        tozero_flag = True

    def start_sweeping(self):

        global list_of_devices
        global types_of_devices
        global device_to_sweep1
        global device_to_sweep2
        global parameter_to_sweep1
        global parameter_to_sweep2
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global from_sweep2
        global to_sweep2
        global ratio_sweep2
        global delay_factor2
        global parameters_to_read
        global filename_sweep
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global stop_flag
        global condition
        global script
        global columns
        global manual_sweep_flags
        global manual_filenames
        global master_lock
        global zero_time
        global back_and_forth_master
        global back_and_forth_slave

        def get_key(val, my_dict):
            for key, value in my_dict.items():
                if val == value:
                    return key
        
        self.list_to_read = []
        # asking multichoise to get parameters to read
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(get_key(entrada, self.dict_lstbox))
        parameters_to_read = self.list_to_read
        
        self.rewrite_preset()

        # creating columns
        device_to_sweep1 = list_of_devices[self.combo_to_sweep1.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep1)]](), 'set_options')
        parameter_to_sweep1 = parameters[self.sweep_options1.current()]
        
        device_to_sweep2 = list_of_devices[self.combo_to_sweep2.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep2)]](), 'set_options')
        parameter_to_sweep2 = parameters[self.sweep_options2.current()]
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_maste2.current()] == 'Master':
            master_lock = True
            
            device_dub = device_to_sweep1
            device_to_sweep1 = device_to_sweep2
            device_to_sweep2 = device_dub
            
            parameter_dub = parameter_to_sweep1
            parameter_to_sweep1 = parameter_to_sweep2
            parameter_to_sweep2 = parameter_dub
            
            manual_sweep_flags = manual_sweep_flags[::-1]
            manual_filenames = manual_filenames[::-1]
            
            back_and_forth_slave, back_and_forth_master = back_and_forth_master, back_and_forth_slave
        
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1,
                   device_to_sweep2 + '.' + parameter_to_sweep2]
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave':
            master_lock = True
            
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_from1.get() != '':
            from_sweep1 = float(self.entry_from1.get())
        if self.entry_to1.get() != '':
            to_sweep1 = float(self.entry_to1.get())
        if self.entry_ratio1.get() != '':
            ratio_sweep1 = float(self.entry_ratio1.get())
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
        if self.entry_delay_factor1.get() != '':
            delay_factor1 = float(self.entry_delay_factor1.get())
        if self.entry_from2.get() != '':
            from_sweep2 = float(self.entry_from2.get())
        if self.entry_to2.get() != '':
            to_sweep2 = float(self.entry_to2.get())
        if self.entry_ratio2.get() != '':
            ratio_sweep2 = float(self.entry_ratio2.get())
        if from_sweep2 > to_sweep2 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
        if self.entry_delay_factor2.get() != '':
            delay_factor2 = float(self.entry_delay_factor2.get())
        if self.entry_filename.get() != '':
            filename_sweep = self.entry_filename.get()
        sweeper_flag1 = False
        sweeper_flag2 = True
        sweeper_flag3 = False
        condition = self.text_condition.get(1.0, tk.END)[:-1]
        script = self.script
        manual_sweep_flags = self.manual_sweep_flags
        manual_filenames = self.manual_filenames

        zero_time = time.perf_counter()
        stop_flag = False
        Sweeper_write()
        self.open_graph()


class Sweeper3d(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        
        self.preset = pd.read_csv(globals()['sweeper3d_path'], sep = ',')
        self.preset = self.preset.fillna('')
        self.combo_to_sweep1_current = int(self.preset['combo_to_sweep1'].values[0])
        self.sweep_options1_current = int(self.preset['sweep_options1'].values[0])
        self.combo_to_sweep2_current = int(self.preset['combo_to_sweep2'].values[0])
        self.sweep_options2_current = int(self.preset['sweep_options2'].values[0])
        self.combo_to_sweep3_current = int(self.preset['combo_to_sweep3'].values[0])
        self.sweep_options3_current = int(self.preset['sweep_options3'].values[0])
        self.from1_init = self.preset['from1'].values[0]
        self.to1_init = self.preset['to1'].values[0]
        self.ratio1_init = self.preset['ratio1'].values[0]
        self.delay_factor1_init = self.preset['delay_factor1'].values[0]
        self.from2_init = self.preset['from2'].values[0]
        self.to2_init = self.preset['to2'].values[0]
        self.ratio2_init = self.preset['ratio2'].values[0]
        self.delay_factor2_init = self.preset['delay_factor2'].values[0]
        self.from3_init = self.preset['from3'].values[0]
        self.to3_init = self.preset['to3'].values[0]
        self.ratio3_init = self.preset['ratio3'].values[0]
        self.delay_factor3_init = self.preset['delay_factor3'].values[0]
        
        label = tk.Label(self, text='3dSweeper', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button_home = tk.Button(self, text='Back to Home',
                                 command=lambda: controller.show_frame(StartPage))
        button_home.pack()

        label_to_sweep1 = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep1.place(relx=0.15, rely=0.12)

        label_to_sweep2 = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep2.place(relx=0.3, rely=0.12)

        label_to_sweep3 = tk.Label(self, text='To sweep:', font=LARGE_FONT)
        label_to_sweep3.place(relx=0.3, rely=0.12)

        label_to_read = tk.Label(self, text='To read:', font=LARGE_FONT)
        label_to_read.place(relx=0.6, rely=0.12)

        label_hierarchy = tk.Label(self, text = 'Hierarchy:', font=LARGE_FONT)
        label_hierarchy.place(relx = 0.05, rely = 0.17)

        self.combo_master1 = ttk.Combobox(self, value = ['Master', 'Slave', 'Slave-slave'])
        self.combo_master1.place(relx = 0.15, rely = 0.17)
        
        self.combo_master2 = ttk.Combobox(self, value = ['Master', 'Slave', 'Slave-slave'])
        self.combo_master2.place(relx = 0.3, rely = 0.17)
        
        self.combo_master3 = ttk.Combobox(self, value = ['Master', 'Slave', 'Slave-slave'])
        self.combo_master3.place(relx = 0.45, rely = 0.17)
        
        label_devices = tk.Label(self, text = 'Devices:', font=LARGE_FONT)
        label_devices.place(relx = 0.05, rely = 0.21)
        
        lstbox_height = len(parameters_to_read) / 47
        
        button_update_sweep = tk.Button(self, text = 'Update sweep', command = lambda: self.update_sweep_configuration)
        button_update_sweep.place(relx = 0.6, rely = 0.21 + lstbox_height)
        
        self.button_pause = tk.Button(self, text = '⏸️', font = LARGE_FONT, command = lambda: self.pause())
        self.button_pause.place(relx = 0.6, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_pause, 'Pause\Continue sweep')
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.6335, rely = 0.25 + lstbox_height)
        CreateToolTip(self.button_stop, 'Stop sweep')
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.6, rely = 0.3 + lstbox_height)
        
        button_start_sweeping = tk.Button(
            self, text="▶", command=lambda: self.start_sweeping(), font = LARGE_FONT)
        button_start_sweeping.place(relx=0.675, rely=0.21 + lstbox_height, height= 90, width=30)
        CreateToolTip(button_start_sweeping, 'Start sweeping')

        self.combo_to_sweep1 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx=0.15, rely=0.21)
        
        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.25)

        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx=0.3, rely=0.25)

        self.sweep_options3 = ttk.Combobox(self)
        self.sweep_options3.place(relx=0.45, rely=0.25)
    
        try:
            self.combo_to_sweep1.current(self.combo_to_sweep1_current)
            self.update_sweep_parameters1(event = None)
        except:
            self.combo_to_sweep1.current(0)
            if self.combo_to_sweep1['values'][0] != '':
                self.update_sweep_parameters1(event = None)
                
        global back_and_forth_master
        global back_and_forth_slave
        global back_and_forth_slave_slave
    
        self.status_back_and_forth_master = tk.IntVar(value = 0)
    
        self.back_and_forth_master_count = 2
    
        self.checkbox_back_and_forth_master = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_master, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_master_status())
        self.checkbox_back_and_forth_master.place(relx=0.22, rely=0.62)
        
        label_back_and_forth_master = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_master.place(relx = 0.2335, rely = 0.61)
        CreateToolTip(label_back_and_forth_master, 'Back and forth sweep\nfor this axis')

        self.combo_to_sweep2 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep2.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx=0.3, rely=0.21)
        
        try:
            self.combo_to_sweep2.current(self.combo_to_sweep2_current)
            self.update_sweep_parameters2(event = None)
        except:
            self.combo_to_sweep2.current(0)
            if self.combo_to_sweep2['values'][0] != '':
                self.update_sweep_parameters2(event = None)
        
        self.status_back_and_forth_slave = tk.IntVar(value = 0)
    
        self.back_and_forth_slave_count = 2
    
        self.checkbox_back_and_forth_slave = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_slave, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_slave_status())
        self.checkbox_back_and_forth_slave.place(relx=0.35, rely=0.62)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.3635, rely = 0.61)
        CreateToolTip(label_back_and_forth_slave, 'Back and forth sweep\nfor this axis')

        self.combo_to_sweep3 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep3.current(0)
        self.combo_to_sweep3.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters3)
        self.combo_to_sweep3.place(relx=0.45, rely=0.21)
        
        try:
            self.combo_to_sweep3.current(self.combo_to_sweep3_current)
            self.update_sweep_parameters3(event = None)
        except:
            self.combo_to_sweep3.current(0)
            if self.combo_to_sweep3['values'][0] != '':
                self.update_sweep_parameters3(event = None)
        
        self.status_back_and_forth_slave_slave = tk.IntVar(value = 0)
        
        self.back_and_forth_slave_slave_count = 2
    
        back_and_forth_slave_slave = 1
    
        self.checkbox_back_and_forth_slave_slave = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_slave_slave, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_slave_slave_status())
        self.checkbox_back_and_forth_slave_slave.place(relx=0.5, rely=0.62)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.5135, rely = 0.61)
        CreateToolTip(label_back_and_forth_slave, 'Back and forth sweep\nfor this axis')

        self.devices = tk.StringVar()
        self.devices.set(value=parameters_to_read)
        self.lstbox_to_read = tk.Listbox(self, listvariable=self.devices,
                                         selectmode='multiple', width=20,
                                         height=len(parameters_to_read) * 1)
        self.lstbox_to_read.place(relx=0.6, rely=0.17)
        
        self.dict_lstbox = {}
        
        for parameter in parameters_to_read:
            self.dict_lstbox[parameter] = parameter
        
        label_options = tk.Label(self, text = 'Options:', font=LARGE_FONT)
        label_options.place(relx = 0.05, rely = 0.25)

        label_from1 = tk.Label(self, text='From', font=LARGE_FONT)
        label_from1.place(relx=0.12, rely=0.29)

        label_to1 = tk.Label(self, text='To', font=LARGE_FONT)
        label_to1.place(relx=0.12, rely=0.33)

        label_step1 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step1.place(relx=0.12, rely=0.37)
        CreateToolTip(label_step1, 'Speed of 1d-sweep')

        self.entry_from1 = tk.Entry(self)
        self.entry_from1.insert(0, self.from1_init)
        self.entry_from1.place(relx=0.17, rely=0.29)

        self.entry_to1 = tk.Entry(self)
        self.entry_to1.insert(0, self.to1_init)
        self.entry_to1.place(relx=0.17, rely=0.33)

        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.insert(0, self.ratio1_init)
        self.entry_ratio1.place(relx=0.17, rely=0.37)

        label_delay_factor1 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor1.place(relx=0.12, rely=0.45)
        CreateToolTip(label_delay_factor1, 'Sleep time per 1 point')

        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.insert(0, self.delay_factor1_init)
        self.entry_delay_factor1.place(relx=0.12, rely=0.51)

        label_from2 = tk.Label(self, text='From', font=LARGE_FONT)
        label_from2.place(relx=0.27, rely=0.29)

        label_to2 = tk.Label(self, text='To', font=LARGE_FONT)
        label_to2.place(relx=0.27, rely=0.33)

        label_step2 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step2.place(relx=0.27, rely=0.37)
        CreateToolTip(label_step2, 'Speed of 1d-sweep')

        self.entry_from2 = tk.Entry(self)
        self.entry_from2.insert(0, self.from2_init)
        self.entry_from2.place(relx=0.32, rely=0.29)

        self.entry_to2 = tk.Entry(self)
        self.entry_to2.insert(0, self.to2_init)
        self.entry_to2.place(relx=0.32, rely=0.33)

        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.insert(0, self.ratio2_init)
        self.entry_ratio2.place(relx=0.32, rely=0.37)

        label_delay_factor2 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor2.place(relx=0.27, rely=0.45)
        CreateToolTip(label_delay_factor2, 'Sleep time per 1 point')

        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.insert(0, self.delay_factor2_init)
        self.entry_delay_factor2.place(relx=0.27, rely=0.51)

        label_from3 = tk.Label(self, text='From', font=LARGE_FONT)
        label_from3.place(relx=0.42, rely=0.29)

        label_to3 = tk.Label(self, text='To', font=LARGE_FONT)
        label_to3.place(relx=0.42, rely=0.33)

        label_step3 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step3.place(relx=0.42, rely=0.37)
        CreateToolTip(label_step3, 'Speed of 1d-sweep')

        self.entry_from3 = tk.Entry(self)
        self.entry_from3.insert(0, self.from3_init)
        self.entry_from3.place(relx=0.47, rely=0.29)

        self.entry_to3 = tk.Entry(self)
        self.entry_to3.insert(0, self.to3_init)
        self.entry_to3.place(relx=0.47, rely=0.33)

        self.entry_ratio3 = tk.Entry(self)
        self.entry_ratio3.insert(0, self.ratio3_init)
        self.entry_ratio3.place(relx=0.47, rely=0.37)

        label_delay_factor3 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor3.place(relx=0.42, rely=0.45)
        CreateToolTip(label_delay_factor3, 'Sleep time per 1 point')

        self.entry_delay_factor3 = tk.Entry(self)
        self.entry_delay_factor3.insert(0, self.delay_factor3_init)
        self.entry_delay_factor3.place(relx=0.42, rely=0.51)

        # section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        self.status_manual3 = tk.IntVar()
        self.filename = filename_sweep[:-4] + '_manual' + '.csv'

        # initials
        self.manual_sweep_flags = [0, 0, 0]
        self.manual_filenames = [self.filename[:-4] + '1.csv',
                                 self.filename[:-4] + '2.csv', self.filename[:-4] + '3.csv']

        self.checkbox_manual1 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual1, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=1))
        self.checkbox_manual1.place(relx=0.12, rely=0.57)
        
        button_new_manual1 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0], i=0))
        button_new_manual1.place(relx=0.12, rely=0.61)
        CreateToolTip(button_new_manual1, 'Create new sweep instruction')

        button_explore_manual1 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=0))
        button_explore_manual1.place(relx=0.15, rely=0.61)
        CreateToolTip(button_explore_manual1, 'Explore existing sweep instruction')

        self.checkbox_manual2 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual2, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=2))
        self.checkbox_manual2.place(relx=0.27, rely=0.57)

        button_new_manual2 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[1], i=1))
        button_new_manual2.place(relx=0.27, rely=0.61)
        CreateToolTip(button_new_manual2, 'Create new sweep instruction')

        button_explore_manual2 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=1))
        button_explore_manual2.place(relx=0.3, rely=0.61)
        CreateToolTip(button_explore_manual2, 'Explore existing sweep instruction')

        self.checkbox_manual3 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual3, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=3))
        self.checkbox_manual3.place(relx=0.42, rely=0.57)

        button_new_manual3 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[2], i=2))
        button_new_manual3.place(relx=0.42, rely=0.61)
        CreateToolTip(button_new_manual3, 'Create new sweep instruction')

        button_explore_manual3 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=2))
        button_explore_manual3.place(relx=0.45, rely=0.61)
        CreateToolTip(button_explore_manual3, 'Explore existing sweep instruction')
        
        label_condition = tk.Label(self, text = 'Constraints:', font = LARGE_FONT)
        label_condition.place(relx = 0.12, rely = 0.66)
        CreateToolTip(label_condition, 'Master sweep: x\nSlave sweep: y\nSlave-slave sweep: z\nSet condition for a sweep map')
        
        self.text_condition = tk.Text(self, width = 60, height = 7)
        self.text_condition.place(relx = 0.12, rely = 0.7)

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        self.script = ''

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)
        CreateToolTip(button_settings, 'Settings')

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.75, rely=0.8)
        CreateToolTip(graph_button, 'Graph')

    def update_master23_combo(self, event, interval = 1000):
        if self.combo_master1['value'][self.combo_master1.current()] == '':
            self.combo_master2['value'] = self.master_option
            self.combo_master2.after(interval)
            self.combo_master3['value'] = self.master_option
            self.combo_master3.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master':
            self.combo_master2['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master2.after(interval)
            self.combo_master3['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master3.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave':
            self.combo_master2['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master2.after(interval)
            self.combo_master3['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master3.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave-slave':
            self.combo_master2['value'] = ['', 'Master', 'Slave']
            self.combo_master2.after(interval)
            self.combo_master3['value'] = ['', 'Master', 'Slave']
            self.combo_master3.after(interval)
        
    def update_master13_combo(self, event, interval = 1000):
        if self.combo_master2['value'][self.combo_master2.current()] == '':
            self.combo_master1['value'] = self.master_option
            self.combo_master1.after(interval)
            self.combo_master3['value'] = self.master_option
            self.combo_master3.after(interval)
        if self.combo_master2['value'][self.combo_master2.current()] == 'Master':
            self.combo_master1['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master1.after(interval)
            self.combo_master3['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master3.after(interval)
        if self.combo_master2['value'][self.combo_master2.current()] == 'Slave':
            self.combo_master1['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master1.after(interval)
            self.combo_master3['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master3.after(interval)
        if self.combo_master2['value'][self.combo_master2.current()] == 'Slave-slave':
            self.combo_master1['value'] = ['', 'Master', 'Slave']
            self.combo_master1.after(interval)
            self.combo_master3['value'] = ['', 'Master', 'Slave']
            self.combo_master3.after(interval)

    def update_master12_combo(self, event, interval = 1000):
        if self.combo_master3['value'][self.combo_master3.current()] == '':
            self.combo_master1['value'] = self.master_option
            self.combo_master1.after(interval)
            self.combo_master2['value'] = self.master_option
            self.combo_master2.after(interval)
        if self.combo_master3['value'][self.combo_master3.current()] == 'Master':
            self.combo_master1['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master1.after(interval)
            self.combo_master2['value'] = ['', 'Slave', 'Slave-slave']
            self.combo_master2.after(interval)
        if self.combo_master3['value'][self.combo_master3.current()] == 'Slave':
            self.combo_master1['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master1.after(interval)
            self.combo_master2['value'] = ['', 'Master', 'Slave-slave']
            self.combo_master2.after(interval)
        if self.combo_master3['value'][self.combo_master3.current()] == 'Slave-slave':
            self.combo_master1['value'] = ['', 'Master', 'Slave']
            self.combo_master1.after(interval)
            self.combo_master2['value'] = ['', 'Master', 'Slave']
            self.combo_master2.after(interval)

    def update_sweep_parameters1(self, event, interval=100):
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current(
        )]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(
                globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.current(self.sweep_options1_current)
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)

    def update_sweep_parameters2(self, event, interval=100):
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current(
        )]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(
                globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.current(self.sweep_options2_current)
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)

    def update_sweep_parameters3(self, event, interval=100):
        class_of_sweeper_device3 = types_of_devices[self.combo_to_sweep3.current(
        )]
        if class_of_sweeper_device3 != 'Not a class':
            self.sweep_options3['value'] = getattr(
                globals()[class_of_sweeper_device3](), 'set_options')
            self.sweep_options3.current(self.sweep_options3_current)
            self.sweep_options3.after(interval)
        else:
            self.sweep_options3['value'] = ['']
            self.sweep_options3.current(0)
            self.sweep_options3.after(interval)
            
    def rewrite_preset(self):
        if self.entry_from1.get() != self.from1_init:
            self.preset.loc[0, 'from1'] = self.entry_from1.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_to1.get() != self.to1_init:
            self.preset.loc[0, 'to1'] = self.entry_to1.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_ratio1.get() != self.ratio1_init:
            self.preset.loc[0, 'ratio1'] = self.entry_ratio1.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_delay_factor1.get() != self.delay_factor1_init:
            self.preset.loc[0, 'delay_factor1'] = self.entry_delay_factor1.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_from2.get() != self.from2_init:
            self.preset.loc[0, 'from2'] = self.entry_from2.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_to2.get() != self.to2_init:
            self.preset.loc[0, 'to2'] = self.entry_to2.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_ratio2.get() != self.ratio2_init:
            self.preset.loc[0, 'ratio2'] = self.entry_ratio2.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_delay_factor2.get() != self.delay_factor2_init:
            self.preset.loc[0, 'delay_factor2'] = self.entry_delay_factor2.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_from3.get() != self.from3_init:
            self.preset.loc[0, 'from3'] = self.entry_from3.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_to3.get() != self.to3_init:
            self.preset.loc[0, 'to3'] = self.entry_to3.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_ratio3.get() != self.ratio3_init:
            self.preset.loc[0, 'ratio3'] = self.entry_ratio3.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
        if self.entry_delay_factor3.get() != self.delay_factor3_init:
            self.preset.loc[0, 'delay_factor3'] = self.entry_delay_factor3.get()
            self.preset.to_csv(globals()['sweeper3d_path'], index = False)
            
    def update_sweep_configuration(self):
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global from_sweep2
        global to_sweep2
        global ratio_sweep2
        global delay_factor2
        global from_sweep3
        global to_sweep3
        global ratio_sweep3
        global delay_factor3
        
        try:
            from_sweep1 = float(self.entry_from1.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_to1.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep1 = float(self.entry_ratio1.get())
        except ValueError:
            pass
        
        try:
            delay_factor1 = float(self.entry_delay_factor1.get())
        except ValueError:
            pass
        
        try:
            from_sweep2 = float(self.entry_from2.get())
        except ValueError:
            pass
        
        try:
            to_sweep2 = float(self.entry_to2.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep2 = float(self.entry_ratio2.get())
        except ValueError:
            pass
        
        try:
            delay_factor2 = float(self.entry_delay_factor2.get())
        except ValueError:
            pass
        
        try:
            from_sweep3 = float(self.entry_from3.get())
        except ValueError:
            pass
        
        try:
            to_sweep3 = float(self.entry_to3.get())
        except ValueError:
            pass
        
        try:
            ratio_sweep3 = float(self.entry_ratio3.get())
        except ValueError:
            pass
        
        try:
            delay_factor3 = float(self.entry_delay_factor3.get())
        except ValueError:
            pass
        
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
            
        if from_sweep2 > to_sweep2 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
            
        if from_sweep3 > to_sweep3 and ratio_sweep3 > 0:
            ratio_sweep3 = -ratio_sweep3
            
        self.rewrite_preset()

    def save_manual_status(self, i):
        if self.manual_sweep_flags[i - 1] != getattr(self, 'status_manual' + str(i)).get():
            self.manual_sweep_flags[i -
                                    1] = getattr(self, 'status_manual' + str(i)).get()

    def save_back_and_forth_master_status(self):
        global back_and_forth_master
        
        if self.status_back_and_forth_master == 0:
            back_and_forth_master = 1
        else:
            back_and_forth_master = self.back_and_forth_master_count
            
    def save_back_and_forth_slave_status(self):
        global back_and_forth_slave
        
        if self.status_back_and_forth_slave == 0:
            back_and_forth_slave = 1
        else:
            back_and_forth_slave = self.back_and_forth_slave_count
    
    def open_blank(self, filename, i):
        df = pd.DataFrame(columns=['steps'])
        df.to_csv(filename, index=False)
        self.manual_filenames[i] = filename
        os.startfile(filename)
        
    def open_settings(self):        
        self.window_settings = Universal_frontend((Settings,), Settings)
        self.window_settings.mainloop()

    def explore_files(self, i):
        self.manual_filenames[i] = tk.filedialog.askopenfilename(initialdir=cur_dir,
                                                                 title='Select a manual sweeper',
                                                                 filetypes=(('CSV files', '*.csv*'),
                                                                            ('all files', '*.*')))

    def set_filename_sweep(self):
        global filename_sweep

        filename_sweep = tk.filedialog.asksaveasfilename(title='Save the file',
                                                         initialfile=cur_dir + '\data_files\sweep' + datetime.today().strftime(
                                                             '%H_%M_%d_%m_%Y'),
                                                         defaultextension='.csv')
        
        self.entry_filename.delete(0, tk.END)
        self.entry_filename.insert(0, filename_sweep)
        self.entry_filename.after(1)

    def open_graph(self):
        global cur_animation_num
        
        def return_range(x, n):
            if x % n == 0:
                return [x + p for p in range(n)]
            elif x % n == n - 1:
                return [x - p for p in range(n)][::-1]
            else:
                return return_range(x + 1, n)
        
        self.window = Universal_frontend(classes=(Graph,), start=Graph)
        for i in return_range(cur_animation_num, 3):
            globals()[f'x{i + 1}'] = []
            globals()[f'x{i + 1}_status'] = 0
            globals()[f'y{i + 1}'] = []
            globals()[f'y{i + 1}_status'] = 0
            globals()[f'ani{i+1}'] = StartAnimation
            globals()[f'ani{i+1}'].start()
        self.window.mainloop()
        
    def pause(self):
        global pause_flag
        
        pause_flag = not(pause_flag)
        
        if self.button_pause['text'] == '⏸️':
            self.button_pause['text'] = '▶️'
        if self.button_pause['text'] == '▶️':
            self.button_pause['text'] = '⏸️'
            
        self.button_pause.after(1000)
        
    def stop(self):
        
        global stop_flag
        
        stop_flag = True
        
    def tozero(self):
        
        global tozero_flag
        
        tozero_flag = True

    def start_sweeping(self):

        global list_of_devices
        global types_of_devices
        global device_to_sweep1
        global device_to_sweep2
        global device_to_sweep3
        global parameter_to_sweep1
        global parameter_to_sweep2
        global parameter_to_sweep3
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global from_sweep2
        global to_sweep2
        global ratio_sweep2
        global delay_factor2
        global from_sweep3
        global to_sweep3
        global ratio_sweep3
        global delay_factor3
        global parameters_to_read
        global filename_sweep
        global sweeper_flag1
        global sweeper_flag2
        global sweeper_flag3
        global stop_flag
        global condition
        global script
        global columns
        global manual_filenames
        global manual_sweep_flags
        global master_lock
        global zero_time
        global back_and_forth_master
        global back_and_forth_slave
        global back_and_forth_slave_slave
        
        def get_key(val, my_dict):
            for key, value in my_dict.items():
                if val == value:
                    return key
        
        self.list_to_read = []
        # asking multichoise to get parameters to read
        selection = self.lstbox_to_read.curselection()
        for i in selection:
            entrada = self.lstbox_to_read.get(i)
            self.list_to_read.append(get_key(entrada, self.dict_lstbox))
        parameters_to_read = self.list_to_read

        # creating columns
        device_to_sweep1 = list_of_devices[self.combo_to_sweep1.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep1)]](), 'set_options')
        parameter_to_sweep1 = parameters[self.sweep_options1.current()]
        
        device_to_sweep2 = list_of_devices[self.combo_to_sweep2.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep2)]](), 'set_options')
        parameter_to_sweep2 = parameters[self.sweep_options2.current()]
        
        device_to_sweep3 = list_of_devices[self.combo_to_sweep3.current()]
        parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep3)]](), 'set_options')
        parameter_to_sweep3 = parameters[self.sweep_options3.current()]
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave-slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave' and self.combo_master3['value'][self.combo_master3.current()] == 'Master':
            master_lock = True
            '''change 1, 2, 3 -> 3, 2, 1'''
            
            device_to_sweep1, device_to_sweep3 = device_to_sweep3, device_to_sweep1
            parameter_to_sweep1, parameter_to_sweep3 = parameter_to_sweep3, parameter_to_sweep1
            back_and_forth_master, back_and_forth_slave_slave = back_and_forth_slave_slave, back_and_forth_master
            manual_sweep_flags[0], manual_sweep_flags[2] = manual_sweep_flags[2], manual_sweep_flags[0]
            manual_filenames[0], manual_filenames[2] = manual_filenames[2], manual_filenames[0]

        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave-slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Master' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave':
            master_lock = True
            '''change 1, 2, 3 -> 3, 1, 2'''
            
            device_to_sweep1, device_to_sweep2, device_to_sweep3 = device_to_sweep3, device_to_sweep1, device_to_sweep2
            parameter_to_sweep1, parameter_to_sweep2, parameter_to_sweep3 = parameter_to_sweep3, parameter_to_sweep1, parameter_to_sweep2
            back_and_forth_master, back_and_forth_slave, back_and_forth_slave_slave = back_and_forth_slave_slave, back_and_forth_master, back_and_forth_slave
            manual_sweep_flags[0], manual_sweep_flags[1], manual_sweep_flags[2] = manual_sweep_flags[2], manual_sweep_flags[0], manual_sweep_flags[1]
            manual_filenames[0], manual_filenames[1], manual_filenames[2] = manual_filenames[2], manual_filenames[0], manual_filenames[1]
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Master' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave-slave':
            master_lock = True
            '''change 1, 2, 3 -> 2, 1, 3'''
            
            device_to_sweep1, device_to_sweep2 = device_to_sweep2, device_to_sweep1
            parameter_to_sweep1, parameter_to_sweep2 = parameter_to_sweep2, parameter_to_sweep1
            back_and_forth_master, back_and_forth_slave = back_and_forth_slave, back_and_forth_master
            manual_sweep_flags[0], manual_sweep_flags[1] = manual_sweep_flags[1], manual_sweep_flags[0]
            manual_filenames[0], manual_filenames[1] = manual_filenames[1], manual_filenames[0]
            
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave-slave' and self.combo_master3['value'][self.combo_master3.current()] == 'Master':
            master_lock = True
            '''change 1, 2, 3 -> 2, 3, 1'''
            
            device_to_sweep1, device_to_sweep2, device_to_sweep3 = device_to_sweep2, device_to_sweep3, device_to_sweep1
            parameter_to_sweep1, parameter_to_sweep2, parameter_to_sweep3 = parameter_to_sweep2, parameter_to_sweep3, parameter_to_sweep1
            back_and_forth_master, back_and_forth_slave, back_and_forth_slave_slave = back_and_forth_slave, back_and_forth_slave_slave, back_and_forth_master
            manual_sweep_flags[0], manual_sweep_flags[1], manual_sweep_flags[2] = manual_sweep_flags[1], manual_sweep_flags[2], manual_sweep_flags[0]
            manual_filenames[0], manual_filenames[1], manual_filenames[2] = manual_filenames[1], manual_filenames[2], manual_filenames[0]
            
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave-slave' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave':
            master_lock = True
            '''change 1, 2, 3 -> 1, 3, 2'''
            
            device_to_sweep2, device_to_sweep3 = device_to_sweep3, device_to_sweep2
            parameter_to_sweep2, parameter_to_sweep3 = parameter_to_sweep3, parameter_to_sweep2
            back_and_forth_slave, back_and_forth_slave_slave = back_and_forth_slave_slave, back_and_forth_slave
            manual_sweep_flags[1], manual_sweep_flags[2] = manual_sweep_flags[2], manual_sweep_flags[1]
            manual_filenames[1], manual_filenames[2] = manual_filenames[2], manual_filenames[1]
        
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1,
                   device_to_sweep2 + '.' + parameter_to_sweep2,
                   device_to_sweep3 + '.' + parameter_to_sweep3]
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_from1.get() != '':
            from_sweep1 = float(self.entry_from1.get())
        if self.entry_to1.get() != '':
            to_sweep1 = float(self.entry_to1.get())
        if self.entry_ratio1.get() != '':
            ratio_sweep1 = float(self.entry_ratio1.get())
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
        if self.entry_delay_factor1.get() != '':
            delay_factor1 = float(self.entry_delay_factor1.get())
        if self.entry_from2.get() != '':
            from_sweep2 = float(self.entry_from2.get())
        if self.entry_to2.get() != '':
            to_sweep2 = float(self.entry_to2.get())
        if self.entry_ratio2.get() != '':
            ratio_sweep2 = float(self.entry_ratio2.get())
        if from_sweep2 > to_sweep2 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
        if self.entry_delay_factor2.get() != '':
            delay_factor2 = float(self.entry_delay_factor2.get())
        if self.entry_from3.get() != '':
            from_sweep3 = float(self.entry_from3.get())
        if self.entry_to3.get() != '':
            to_sweep3 = float(self.entry_to3.get())
        if self.entry_ratio3.get() != '':
            ratio_sweep3 = float(self.entry_ratio3.get())
        if from_sweep3 > to_sweep3 and ratio_sweep3 > 0:
            ratio_sweep3 = -ratio_sweep3
        if self.entry_delay_factor3.get() != '':
            delay_factor3 = float(self.entry_delay_factor3.get())
        if self.entry_filename.get() != '':
            filename_sweep = self.entry_filename.get()
        sweeper_flag1 = False
        sweeper_flag2 = False
        sweeper_flag3 = True
        condition = self.text_condition.get(1.0, tk.END)[:-1]
        script = self.script
        manual_filenames = self.manual_filenames
        manual_sweep_flags = self.manual_sweep_flags
        
        self.rewrite_preset()

        zero_time = time.perf_counter()
        
        stop_flag = False
        Sweeper_write()
        self.open_graph()

class Settings(tk.Frame):
    
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        
        parent = globals()['Sweeper_object']
        
        label_adress = tk.Label(self, text = 'Set device type:', font = LARGE_FONT)
        label_adress.place(relx = 0.05, rely = 0.05)
        
        self.combo_adresses = ttk.Combobox(self, value = list_of_devices)
        self.combo_adresses.current(0)
        self.combo_adresses.place(relx = 0.05, rely = 0.1)
        
        self.device_classes = []
        for class_ in device_classes:
            self.device_classes.append(var2str(class_))
            
        self.combo_types = ttk.Combobox(self, value = self.device_classes)    
        self.combo_types.bind("<<ComboboxSelected>>", self.set_type_to_adress)
        self.combo_types.place(relx = 0.2, rely = 0.1)
        
        label_names = tk.Label(self, text = 'Change names:', font = LARGE_FONT)
        label_names.place(relx = 0.05, rely = 0.15)
            
        self.combo_devices = ttk.Combobox(self, value = list_of_devices)
        self.combo_devices.current(0)
        self.combo_devices.bind(
            "<<ComboboxSelected>>", self.update_combo_set_parameters)
        self.combo_devices.place(relx=0.05, rely=0.2)
        
        self.combo_set_parameters = ttk.Combobox(self, value = [''])
        self.combo_set_parameters.current(0)
        self.combo_set_parameters.place(relx=0.05, rely=0.25)
        
        parameters = list(parent.lstbox_to_read.get(0, tk.END))
        
        if len(parameters) == 0:
            parameters = ['']
        
        self.combo_get_parameters = ttk.Combobox(self, value = parameters)
        self.combo_get_parameters.current(0)
        self.combo_get_parameters.place(relx=0.05, rely=0.3)
        
        button_change_name_device = tk.Button(self, text = 'Change device name', command = lambda: self.update_names_devices(parent))
        button_change_name_device.place(relx = 0.2, rely = 0.19)
        
        button_change_name_set_parameters = tk.Button(self, text = 'Change set name', command = lambda: self.update_names_set_parameters(parent))
        button_change_name_set_parameters.place(relx = 0.2, rely = 0.24)
        
        button_change_name_get_parameters = tk.Button(self, text = 'Change get name', command = lambda: self.update_names_get_parameters(parent))
        button_change_name_get_parameters.place(relx = 0.2, rely = 0.29)
        
        if hasattr(parent, 'back_and_forth_slave_slave_count'): 
            
            label_back_and_forth_master = tk.Label(self, text = 'Set number of back and forth walks for master axis', font = LARGE_FONT)
            label_back_and_forth_master.place(relx = 0.55, rely = 0.05)
            
            label_back_and_forth_slave = tk.Label(self, text = 'Set number of back and forth walks for slave axis', font = LARGE_FONT)
            label_back_and_forth_slave.place(relx = 0.55, rely = 0.15)
            
            label_back_and_forth_slave_slave = tk.Label(self, text = 'Set number of back and forth walks for slave_slave axis', font = LARGE_FONT)
            label_back_and_forth_slave_slave.place(relx = 0.55, rely = 0.25)
            
            self.combo_back_and_forth_master = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_master.place(relx = 0.55, rely = 0.1)
            
            button_set_back_and_forth_master = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_master_count(parent = parent))
            button_set_back_and_forth_master.place(relx = 0.68, rely = 0.09)
            
            self.combo_back_and_forth_slave = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_slave.place(relx = 0.55, rely = 0.2)
            
            button_set_back_and_forth_slave = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_slave_count(parent = parent))
            button_set_back_and_forth_slave.place(relx = 0.68, rely = 0.19)
            
            self.combo_back_and_forth_slave_slave = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_slave_slave.place(relx = 0.55, rely = 0.3)
            
            button_set_back_and_forth_slave_slave = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_slave_count(parent = parent))
            button_set_back_and_forth_slave_slave.place(relx = 0.68, rely = 0.29)
        
        elif hasattr(parent, 'back_and_forth_slave_count') and not hasattr(parent, 'back_and_forth_slave_slave_count'):
            
            label_back_and_forth_master = tk.Label(self, text = 'Set number of back and forth walks for master axis', font = LARGE_FONT)
            label_back_and_forth_master.place(relx = 0.55, rely = 0.05)
            
            label_back_and_forth_slave = tk.Label(self, text = 'Set number of back and forth walks for slave axis', font = LARGE_FONT)
            label_back_and_forth_slave.place(relx = 0.55, rely = 0.15)
            
            self.combo_back_and_forth_master = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_master.place(relx = 0.55, rely = 0.1)
            
            button_set_back_and_forth_master = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_master_count(parent = parent))
            button_set_back_and_forth_master.place(relx = 0.68, rely = 0.09)
            
            self.combo_back_and_forth_slave = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_slave.place(relx = 0.55, rely = 0.2)
            
            button_set_back_and_forth_slave = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_slave_count(parent = parent))
            button_set_back_and_forth_slave.place(relx = 0.68, rely = 0.19)
            
        else:
            
            label_back_and_forth_master = tk.Label(self, text = 'Set number of back and forth walks for master axis', font = LARGE_FONT)
            label_back_and_forth_master.place(relx = 0.55, rely = 0.05)
            
            self.combo_back_and_forth_master = ttk.Combobox(self, value = [2, 'custom', 'continious'])
            self.combo_back_and_forth_master.place(relx = 0.55, rely = 0.1)
            
            button_set_back_and_forth_master = tk.Button(self, text = 'Set', command = lambda: self.update_back_and_forth_master_count(parent = parent))
            button_set_back_and_forth_master.place(relx = 0.68, rely = 0.09)
        
        for_text_loops = ''
        indent = '\t'
        
        for i in range(1, 4):
            try:
                if getattr(parent, 'checkbox_manual' + str(i)).state() == ():
                    for_text_loops += indent * (i - 1) + 'while condition(axis = ' + str(i) + '):\n' + indent * i + 'step(axis = ' + str(i) + ')\n' + indent * i + 'sleep(time_delay' + str(i) + ')\n'
                else:
                    for_text_loops += indent * (i - 1) + 'for i' + str(i) + ', value' + str(i) + 'in enumerate(data' + str(i)+ '):\n' + indent * i + 'step(axis = ' + str(i) + ')\n' + indent * i + 'sleep(time_delay' + str(i) + ')\n'
            except AttributeError:
                pass
        
        label_script = tk.Label(self, text = 'Manual script', font = LARGE_FONT)
        label_script.place(relx = 0.05, rely = 0.36)
        
        depth = for_text_loops.count('\n') // 3
        
        text_loops = tk.Text(self, width = 60, height = 3 * depth)
        text_loops.place(relx = 0.05, rely = 0.4)
        text_loops.insert(tk.END, for_text_loops)
        text_loops.configure(font = LARGE_FONT, state = tk.DISABLED, bg = '#f0f0f0')
        
        self.text_script = tk.Text(self, width = 60, height = 10)
        self.text_script.place(relx = 0.05, rely = 0.652 - (3 - depth) * 0.083)
        self.text_script.configure(font = LARGE_FONT)
        
        button_explore_script = tk.Button(
            self, text='🔎', font = SUPER_LARGE, command=lambda: self.explore_script())
        button_explore_script.place(relx=0.525, rely=0.4)
        CreateToolTip(button_explore_script, 'Explore existing script')
        
        button_save_script = tk.Button(
            self, text='💾', font = SUPER_LARGE, command=lambda: self.save_script())
        button_save_script.place(relx=0.525, rely=0.48)
        CreateToolTip(button_save_script, 'Save this script')
        
        self.script_filename = ''
        
        button_set_script = tk.Button(
            self, text = 'Apply script', font = LARGE_FONT, command = lambda: self.set_script(parent))
        button_set_script.place(relx = 0.525, rely = 0.56)
        
        
    def set_type_to_adress(self, interval = 1000):
        global adress_dict
        global types_of_devices
        global new_parameters_to_read
        
        if list(self.combo_adresses['values'])[self.combo_adresses.current()] != '':
        
            types_of_devices[self.combo_adresses.current()] = list(self.combo_types['values'])[self.combo_types.current()]
            
            adress_dict[list(self.combo_adresses['values'])[self.combo_adresses.current()]] = list(self.combo_types['values'])[self.combo_types.current()]
            
            with open(cur_dir + '\\config\\adress_dictionary.txt', "w") as outfile:
                json.dump(adress_dict, outfile)
                
            new_parameters_to_read()
        
    
    def update_combo_set_parameters(self, event, interval = 1000):
        device_class = types_of_devices[self.combo_devices.current()]
        if device_class != 'Not a class':
            self.combo_set_parameters['values'] = getattr(globals()[device_class](), 'set_options')
            self.combo_set_parameters.after(interval)
        else:
            self.combo_set_parameters['values'] = ['']
            self.combo_set_parameters.current(0)
            self.combo_set_parameters.after(interval)

    def update_names_devices(self, parent, interval = 1000):
        new_device_name = self.combo_devices.get()
        new_device_values = list(self.combo_devices['values'])
        new_device_values[self.combo_devices.current()] = new_device_name
        self.combo_devices['values'] = new_device_values
        try:
            parent.combo_to_sweep1['values'] = new_device_values
            parent.combo_to_sweep1.after(interval)
        except:
            pass
        try:
            parent.combo_to_sweep2['values'] = new_device_values
            parent.combo_to_sweep2.after(interval)
        except:
            pass
        try:
            parent.combo_to_sweep3['values'] = new_device_values
            parent.combo_to_sweep3.after(interval)
        except:
            pass
        
    def update_names_set_parameters(self, parent, interval = 1000):
        new_set_parameter_name = self.combo_set_parameters.get()
        new_set_parameters_values = list(self.combo_set_parameters['values'])
        new_set_parameters_values[self.combo_set_parameters.current()] = new_set_parameter_name
        self.combo_set_parameters['values'] = new_set_parameters_values
        try:
            parent.sweep_options1['values'] = new_set_parameters_values
            parent.sweep_options1.after(interval)
        except:
            pass
        try:
            parent.sweep_options2['values'] = new_set_parameters_values
            parent.sweep_options2.after(interval)
        except:
            pass
        try:
            parent.sweep_options3['values'] = new_set_parameters_values
            parent.sweep_options3.after(interval)
        except:
            pass
        
    def update_names_get_parameters(self, parent, interval = 1000):
        new_get_parameter_name = self.combo_get_parameters.get()
        new_get_parameters_values = list(self.combo_get_parameters['values'])
        new_get_parameters_values[self.combo_get_parameters.current()] = new_get_parameter_name
        
        parent.dict_lstbox[self.combo_get_parameters['values'][self.combo_get_parameters.current()]] = new_get_parameter_name
        
        self.combo_get_parameters['values'] = new_get_parameters_values
        
        parent.devices.set(value=new_get_parameters_values)
        parent.lstbox_to_read.after(interval)
       
    def update_back_and_forth_master_count(self, parent):
        if self.combo_back_and_forth_master.current() == 0:
            parent.back_and_forth_master_count = 2
        elif self.combo_back_and_forth_master.current() == -1:
            parent.back_and_forth_master_count = int(self.combo_back_and_forth_master.get())
        elif self.combo_back_and_forth_master.current() == 2:
            parent.back_and_forth_master_count = int(1e6)
        else:
            raise Exception(f'Insert proper back_and_forth_master. Should be int, but given {type(self.combo_back_and_forth_master.get())}')
            
    def update_back_and_forth_slave_count(self, parent):
        if self.combo_back_and_forth_slave.current() == 0:
            parent.back_and_forth_slave_count = 2
        elif self.combo_back_and_forth_slave.current() == -1:
            parent.back_and_forth_slave_count = int(self.combo_back_and_forth_slave.get())
        elif self.combo_back_and_forth_slave.current() == 2:
            parent.back_and_forth_slave_count = int(1e6)
        else:
            raise Exception(f'Insert proper back_and_forth_master. Should be int, but given {type(self.combo_back_and_forth_slave.get())}')
            
    def update_back_and_forth_slave_slave_count(self, parent):
        if self.combo_back_and_forth_slave_slave.current() == 0:
            parent.back_and_forth_slave_slave_count = 2
        elif self.combo_back_and_forth_slave_slave.current() == -1:
            parent.back_and_forth_slave_slave_count = int(self.combo_back_and_forth_slave_slave.get())
        elif self.combo_back_and_forth_slave_slave.current() == 2:
            parent.back_and_forth_slave_slave_count = int(1e6)
        else:
            raise Exception(f'Insert proper back_and_forth_master. Should be int, but given {type(self.combo_back_and_forth_slave_slave.get())}')
       
    def explore_script(self, interval = 1):
        script_filename = tk.filedialog.askopenfilename(initialdir=cur_dir,
                                                                 title='Select a manual sweeper',
                                                                 filetypes=(('CSV files', '*.csv*'),
                                                                            ('all files', '*.*')))
        with open(script_filename, 'r') as file:
            try:
                file.open()
                script = file.read()
            except:
                file.close()
            finally:
                file.close()
                
        self.text_script.delete(0, tk.END)
        self.text_script.insert(tk.END, script)
        self.text_script.after(interval)
        
    def save_script(self):
        self.script_filename = tk.filedialog.asksaveasfilename(title='Save the file',
                                                         initialfile=cur_dir + '\config\script' + datetime.today().strftime(
                                                             '%H_%M_%d_%m_%Y'),
                                                         defaultextension='.csv')
        
    def set_script(self, parent):
        parent.script = self.text_script.get(1.0, tk.END)[:-1]

class Sweeper_write(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        
        self.sweeper_flag1 = sweeper_flag1
        self.sweeper_flag2 = sweeper_flag2
        self.sweeper_flag3 = sweeper_flag3
        self.device_to_sweep1 = device_to_sweep1
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameters_to_read = parameters_to_read
        self.from_sweep1 = float(from_sweep1)
        self.to_sweep1 = float(to_sweep1)
        self.ratio_sweep1 = float(ratio_sweep1)
        self.delay_factor1 = float(delay_factor1)
        self.value1 = float(from_sweep1)
        self.condition = condition
        self.step1 = float(delay_factor1) * float(ratio_sweep1)
        self.time1 = (float(from_sweep1) - float(to_sweep1)) / float(ratio_sweep1)
        self.filename_sweep = filename_sweep
        self.columns = columns
        globals()['dataframe'] = []
        if self.sweeper_flag2 == True:
            self.device_to_sweep2 = device_to_sweep2
            self.parameter_to_sweep2 = parameter_to_sweep2
            self.from_sweep2 = float(from_sweep2)
            self.to_sweep2 = float(to_sweep2)
            self.ratio_sweep2 = float(ratio_sweep2)
            self.delay_factor2 = float(delay_factor2)
            self.filename_sweep = filename_sweep
            self.value2 = float(from_sweep2)
            self.columns = columns
            self.step2 = float(delay_factor2) * float(ratio_sweep2)
            self.time2 = (float(from_sweep2) - float(to_sweep2)) / float(ratio_sweep2)
            
            try:
                self.nstep2 = (float(to_sweep2) - float(from_sweep2)) / self.ratio_sweep2 / self.delay_factor2
                self.nstep2 = int(self.nstep2)
            except ValueError:
                self.nstep2 = 1
            
        if self.sweeper_flag3 == True:
            self.device_to_sweep2 = device_to_sweep2
            self.device_to_sweep3 = device_to_sweep3
            self.parameter_to_sweep2 = parameter_to_sweep2
            self.parameter_to_sweep3 = parameter_to_sweep3
            self.from_sweep2 = float(from_sweep2)
            self.to_sweep2 = float(to_sweep2)
            self.ratio_sweep2 = float(ratio_sweep2)
            self.delay_factor2 = float(delay_factor2)
            self.from_sweep3 = float(from_sweep3)
            self.to_sweep3 = float(to_sweep3)
            self.ratio_sweep3 = float(ratio_sweep3)
            self.delay_factor3 = float(delay_factor3)
            self.filename_sweep = filename_sweep
            self.value2 = float(from_sweep2)
            self.value3 = float(from_sweep3)
            self.columns = columns
            self.step2 = float(delay_factor2) * float(ratio_sweep2)
            self.step3 = float(delay_factor3) * float(ratio_sweep3)
            self.time2 = (float(from_sweep2) - float(to_sweep2)) / float(ratio_sweep2)
            self.time3 = (float(from_sweep3) - float(to_sweep3)) / float(ratio_sweep3)
            
            try:
                self.nstep2 = (float(to_sweep2) - float(from_sweep2)) / self.ratio_sweep2 / self.delay_factor2
                self.nstep2 = int(self.nstep2)
            except ValueError:
                self.nstep2 = 1
                
            try:
                self.nstep3 = (float(to_sweep3) - float(from_sweep3)) / self.ratio_sweep3 / self.delay_factor3
                self.nstep3 = int(self.nstep3)
            except ValueError:
                self.nstep3 = 1
            
        print(f'Manual_sweep_flags are {manual_sweep_flags}\nrange1 = [{from_sweep1}:{to_sweep1}), ratio_sweep1 = {ratio_sweep1}\nrange2 = [{from_sweep2}:{to_sweep2}), ratio_sweep2 = {ratio_sweep2}\nrange3 = [{from_sweep3}:{to_sweep3}), ratio_sweep3 = {ratio_sweep3}')

        try:
            threading.Thread.__init__(self)
            self.daemon = True
            self.start()
        except NameError:
            pass

        self.grid_space = True

        if self.condition != '':
            #creating grid space for sweep parameters
            if self.sweeper_flag2 == True:
                ax1 = np.linspace(self.from_sweep1, self.to_sweep1, self.nstep1)
                ax2 = np.linspace(self.from_sweep2, self.to_sweep2, self.nstep2)
                AX1, AX2 = np.meshgrid(ax1, ax2)
                space = AX1.tolist().copy()
                for i in range(AX1.shape[0]):
                    for j in range(AX1.shape[1]):
                        space[i][j] = (np.array([AX1[i][j], AX2[i][j]]) * self.func(tup = tuple((AX1[i][j], AX2[i][j])), dtup = tuple((self.step1 / 2, self.step2 / 2)), condition_str = self.condition, sweep_dimension = 2)).tolist()
                space = np.array(space).reshape(-1, 2)
                
                xnans = []
                ynans = []

                for index, elem in enumerate(space.T[0]):
                    if np.isnan(elem):
                        xnans.append(index)
                        
                for index, elem in enumerate(space.T[1]):
                    if np.isnan(elem):
                        ynans.append(index)
                        
                x = np.delete(space.T[0], xnans)
                y = np.delete(space.T[1], ynans)
                
                self.grid_space = []
                
                for i in range(x.shape[0]):
                    self.grid_space.append([x[i], y[i]])
                        
            if self.sweeper_flag3 == True: 
                ax1 = np.linspace(self.from_sweep1, self.to_sweep1, self.nstep1)
                ax2 = np.linspace(self.from_sweep2, self.to_sweep2, self.nstep2)
                ax3 = np.linspace(self.from_sweep3, self.to_sweep3, self.nstep3)
                AX1, AX2, AX3 = np.meshgrid(ax1, ax2, ax3)
                space = AX1.tolist().copy()
                for i in range(AX1.shape[0]):
                    for j in range(AX1.shape[1]):
                        for k in range(AX1.shape[2]):
                            space[i][j][k] = tuple((AX1[i][j][k], AX2[i][j][k], AX3[i][j][k])) * self.func(tup = tuple((AX1[i][j][k], AX2[i][j][k], AX3[i][j][k])), dtup = tuple((self.step1 / 2, self.step2 / 2, self.step3 / 3)), condition_str = self.condition, sweep_dimension = 3)

                xnans = []
                ynans = []
                znans = []

                for index, elem in enumerate(space.T[0]):
                    if np.isnan(elem):
                        xnans.append(index)
                        
                for index, elem in enumerate(space.T[1]):
                    if np.isnan(elem):
                        ynans.append(index)
                        
                for index, elem in enumerate(space.T[2]):
                    if np.isnan(elem):
                        znans.append(index)
                        
                x = np.delete(space.T[0], xnans)
                y = np.delete(space.T[1], ynans)
                z = np.delete(space.T[2], ynans)
                
                self.grid_space = []
                
                for i in range(x.shape[0]):
                    self.grid_space.append([x[i], y[i], z[i]])


    def func(self, tup, dtup, condition_str, sweep_dimension):
        '''input: tup - tuple, contains coordinates of phase space of sweep parameters,
        dtup: tuple of steps along sweep axis
        condition_str - python-like condition, written by user in a form of string
        sweep_dimension - 2 or 3: how many sweep parameters are there
        #############
        return 1 if point in fase space with coordinates in tup included in condition
        np.nan if not included'''
        
        def isequal(a, b, abs_tol):
            '''equality with tolerance'''
            return abs(a-b) <= abs_tol

        def notequal(a, b, abs_tol):
            '''not equality with tolerance'''
            return abs(a-b) > abs_tol

        def ismore(a, b, abs_tol):
            '''if one lement is more than other with tolerance'''
            return (a-b) > 0

        def ismoreequal(a, b, abs_tol):
            '''if one element is more or equal than other with tolerance'''
            return (a-b) >= abs_tol

        def isless(a, b, abs_tol):
            '''if one lement is less than other with tolerance'''
            return (a-b) < 0

        def islessequal(a, b, abs_tol):
            '''if one lement is less or equal than other with tolerance'''
            return (a-b) <= abs_tol
        
        def insert(string, index, ins):
            A_l = string[:index]
            A_r = string[index + 1:]
            return A_l + ins + A_r
        
        result = 1
        rows_ends = [0]
        for index, elem in enumerate(condition_str):
            if elem == '\n':
                rows_ends.append(index)
        if len(rows_ends) == 0:
            rows_ends.append(-1)
        
        dict_operations = {' == ': isequal, ' != ': notequal, ' > ': ismore, 
                           ' < ': isless, ' >= ': ismoreequal, ' <= ': islessequal, 
                             '==': isequal, '!=': notequal, '>': ismore, 
                             '<': isless, '>=': ismoreequal, '<=': islessequal}
        list_operations = list(dict_operations.keys())
        
        for rows_end in rows_ends:
            indexes = []
            try:
                for eq_operation in list_operations:
                    cur_index = condition_str[rows_end:rows_ends[rows_ends.index(rows_end) + 1]].find(eq_operation)
                    if cur_index > 0:
                        indexes.append([cur_index, eq_operation])
                        break
                lhs = condition_str[rows_end:rows_ends[rows_ends.index(rows_end) + 1]][:indexes[0][0]]
                rhs = condition_str[rows_end:rows_ends[rows_ends.index(rows_end) + 1]][indexes[0][0] + len(indexes[0][1]):]
            except IndexError:
                for eq_operation in list_operations:
                    cur_index = condition_str[rows_end:].find(eq_operation)
                    if cur_index > 0:
                        indexes.append([cur_index, eq_operation])
                        break
                lhs = condition_str[rows_end:][:indexes[0][0]]
                rhs = condition_str[rows_end:][indexes[0][0] + len(indexes[0][1]):]
     
            if sweep_dimension == 2:
                
                x_in_lhs = []
                x_in_rhs = []
                y_in_lhs = []
                y_in_rhs = []
                
                for index, elem in enumerate(lhs):
                    if elem == 'x' or elem == 'X' or elem == 'master' or elem == 'Master':
                        x_in_lhs.append(index)
                for index, elem in enumerate(rhs):
                    if elem == 'x' or elem == 'X' or elem == 'master' or elem == 'Master':
                        x_in_rhs.append(index)
                for i in x_in_lhs:
                    lhs = insert(lhs, i, 'tup[0]')
                for i in x_in_rhs:
                    rhs = insert(rhs, i, 'tup[0]')
                for index, elem in enumerate(lhs):
                    if elem == 'y' or elem == 'Y' or elem == 'slave' or elem == 'Slave':
                        y_in_lhs.append(index)
                for index, elem in enumerate(rhs):
                    if elem == 'y' or elem == 'Y' or elem == 'slave' or elem == 'Slave':
                        y_in_rhs.append(index)
                for i in y_in_lhs:
                    lhs = insert(lhs, i, 'tup[1]')
                for i in y_in_rhs:
                    rhs = insert(rhs, i, 'tup[1]')
                
                if lhs != '' and rhs != '':
                
                    if dict_operations[indexes[0][1]](eval(lhs, locals()), eval(rhs, locals()), np.sqrt(dtup[0]**2 + dtup[1]**2)):
                        result *= 1
                    else:
                        result *= np.nan
                
                else:
                    result *= 1
            
            elif sweep_dimension == 3:
                x_in_lhs = []
                x_in_rhs = []
                y_in_lhs = []
                y_in_rhs = []
                z_in_lhs = []
                z_in_rhs = []
                
                for index, elem in enumerate(lhs):
                    if elem == 'x' or elem == 'X':
                        x_in_lhs.append(index)
                for index, elem in enumerate(rhs):
                    if elem == 'x' or elem == 'X':
                        x_in_rhs.append(index)
                for i in x_in_lhs:
                    lhs = insert(lhs, i, 'tup[0]')
                for i in x_in_rhs:
                    rhs = insert(rhs, i, 'tup[0]')
                for index, elem in enumerate(lhs):
                    if elem == 'y' or elem == 'Y':
                        y_in_lhs.append(index)
                for index, elem in enumerate(rhs):
                    if elem == 'y' or elem == 'Y':
                        y_in_rhs.append(index)
                for i in y_in_lhs:
                    lhs = insert(lhs, i, 'tup[1]')
                for i in y_in_rhs:
                    rhs = insert(rhs, i, 'tup[1]')
                for index, elem in enumerate(lhs):
                    if elem == 'z' or elem == 'Z':
                        z_in_lhs.append(index)
                for index, elem in enumerate(rhs):
                    if elem == 'z' or elem == 'Z':
                        z_in_rhs.append(index)
                for i in z_in_lhs:
                    lhs = insert(lhs, i, 'tup[2]')
                for i in z_in_rhs:
                    rhs = insert(rhs, i, 'tup[2]')
                
                if lhs != '' and rhs != '':
                    if dict_operations[indexes[0][1]](eval(lhs, locals()), eval(rhs, locals()), np.sqrt(dtup[0]**2 + dtup[1]**2 + dtup[2]**2)):
                        result *= 1
                    else:
                        result *= np.nan
                else:
                    result *= 1
            else:
                return 1
        return result

    def transposition(self, a, b):
        
        global manual_sweep_flags
        '''changes device_a and device_b order'''
        
        if 1 in manual_sweep_flags:
            pass
        else:
            print('Transposition happened')
            a = str(a)
            b = str(b)
            globals()[f'device_to_sweep{a}'] = getattr(self, f'device_to_sweep{b}')
            globals()[f'device_to_sweep{b}'] = getattr(self, f'device_to_sweep{a}')
            globals()[f'parameter_to_sweep{a}'] = getattr(self, f'parameter_to_sweep{b}')
            globals()[f'parameter_to_sweep{b}'] = getattr(self, f'parameter_to_sweep{a}')
            globals()[f'from_sweep{a}'] = float(getattr(self, f'from_sweep{b}'))
            globals()[f'to_sweep{a}'] = float(getattr(self, f'to_sweep{b}'))
            globals()[f'ratio_sweep{a}'] = float(getattr(self, f'ratio_sweep{b}'))
            globals()[f'delay_factor{a}'] = float(getattr(self, f'delay_factor{b}'))
            globals()[f'from_sweep{b}'] = float(getattr(self, f'from_sweep{a}'))
            globals()[f'to_sweep{b}'] = float(getattr(self, f'to_sweep{a}'))
            globals()[f'ratio_sweep{b}'] = float(getattr(self, f'ratio_sweep{a}'))
            globals()[f'delay_factor{b}'] = float(getattr(self, f'delay_factor{a}'))
            globals()[f'step{a}']  = float(getattr(self, f'delay_factor{b}')) * float(getattr(self, f'ratio_sweep{b}'))
            globals()[f'step{b}'] = float(getattr(self, f'delay_factor{a}')) * float(getattr(self, f'ratio_sweep{a}'))
            globals()[f'value{a}'] = float(getattr(self, f'from_sweep{b}'))
            globals()[f'value{b}'] = float(getattr(self, f'from_sweep{a}'))
            globals()[f'time{a}'] = (float(getattr(self, f'from_sweep{b}')) - float(getattr(self, f'to_sweep{b}')) / float(getattr(self, f'ratio_sweep{b}')))
            globals()[f'time{b}'] = (float(getattr(self, f'from_sweep{a}')) - float(getattr(self, f'to_sweep{a}')) / float(getattr(self, f'ratio_sweep{a}')))

    def isinarea(self, point, grid_area, dgrid_area, sweep_dimension = 2):
        '''if point is in grid_area return True. 
        Grid size defined by dgrid_area which is tuple'''
        
        if grid_area == True:
            return True
        else:
            def includance(point, reference, dgrid_area, sweep_dimension = 2):
                '''equity with tolerance'''
                if sweep_dimension == 2:
                    return abs(point[0] - reference[0]) <= np.sqrt(dgrid_area[0]**2 + dgrid_area[1]**2) and abs(point[1] - reference[1]) <= np.sqrt(dgrid_area[0]**2 + dgrid_area[1]**2)
                if sweep_dimension == 3:
                    return abs(point[0] - reference[0]) <= np.sqrt(dgrid_area[0]**2 + dgrid_area[1]**2 + dgrid_area[2]**2) and abs(point[1] - reference[1]) <= np.sqrt(dgrid_area[0]**2 + dgrid_area[1]**2 + dgrid_area[2]**2) and abs(point[2] - reference[2]) <= np.sqrt(dgrid_area[0]**2 + dgrid_area[1]**2 + dgrid_area[2]**2)
            
            if sweep_dimension == 2:
                for reference in grid_area:
                    if includance(point = point, reference = reference, dgrid_area = dgrid_area):
                        return True

            if sweep_dimension == 3:
                for reference in grid_area:
                    if includance(point = point, reference = reference, dgrid_area = dgrid_area, 
                                  sweep_dimension = 3):
                        return True

            return False
        
    def run(self):
        global manual_filenames
        global manual_sweep_flags
        global master_flag1
        global master_flag2
        global master_flag3
        global filename_sweep
        global pause_flag
        global stop_flag
        global tozero_flag
        global back_and_forth_slave
        global back_and_forth_master
        global zero_time
        global script
        
        def append_read_parameters():
            '''appends dataframe with parameters to read'''
            
            print('Read parameters appended')
            
            global dataframe
            
            for parameter in self.parameters_to_read:
                index_dot = parameter.find('.')
                adress = parameter[:index_dot]
                option = parameter[index_dot + 1:]
                dataframe.append(getattr(globals()[
                                 types_of_devices[list_of_devices.index(str(adress))]](adress=adress), option)())
        
        def tofile():
            '''appends file with new row - dataframe'''
            
            global dataframe
            global filename_sweep
            
            print('File rewrote')
            
            with open(filename_sweep, 'a') as f_object:
                try:
                    writer_object = writer(f_object)
                    writer_object.writerow(dataframe)
                    f_object.close()
                except KeyboardInterrupt:
                    f_object.close()
                finally:
                    f_object.close()
            return
                  
        def condition(axis):
            
            global stop_flag
            
            '''Determine if current value is in sweep borders of axis'''
            
            axis = str(axis)
            value = getattr(self, 'value' + axis)
            to_sweep = float(globals()['to_sweep' + axis])
            from_sweep = float(globals()['from_sweep' + axis])
            speed = float(globals()['ratio_sweep' + axis])
            
            if stop_flag == True:
                for i in [1, 2, 3]:
                    globals()['sweeper_flag' + str(i)] = False
                return False
            
            if speed >= 0:
                result = value >= from_sweep and value <= to_sweep
                print('Condition checked, result is ' + str(result) + f'\nBoundaries are [{from_sweep};{to_sweep}), Value is {value}, Ratio is positive')
                return result
            else:
                result = value >= to_sweep and value <= from_sweep
                print('Condition checked, result is ' + str(result) + f'\nBoundaries are [{from_sweep};{to_sweep}), Value is {value}, Ratio is negative')
                return result
            
        def step(axis = 1, value = None, back = False):
            
            def try_tozero():
                
                def try_go(axis, value):
                    axis = str(axis)
                    value = float(value)
                    getattr(globals()[types_of_devices[list_of_devices.index(getattr(self, 'device_to_sweep' + axis))]](
                        adress=getattr(self, 'device_to_sweep' + axis)), 'set_' + str(getattr(self, 'parameter_to_sweep' + axis)))(value=value)
                
                try_go(1, 0)
                try:
                    try_go(2, 0)
                    try:
                        try_go(3, 0)
                    except:
                        pass
                except:
                    pass
            
            '''performs a step along sweep axis'''
            
            global zero_time
            global dataframe
            global manual_sweep_flags
            global stop_flag
            global pause_flag
            global tozero_flag
            
            if len(dataframe) == 0:
                dataframe = [time.perf_counter() - zero_time]
            else:
                dataframe[0] = [time.perf_counter() - zero_time][0]
                
            device_to_sweep = getattr(self, 'device_to_sweep' + str(axis))
            parameter_to_sweep = getattr(self, 'parameter_to_sweep' + str(axis))
            
            if pause_flag == False:
                if tozero_flag == False:
                    # sweep process here
                    ###################
                    # set 'parameter_to_sweep' to 'value'
                    if manual_sweep_flags[axis - 1] == 0:
                        value = getattr(self, 'value' + str(axis))
                        getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep)]](
                            adress=device_to_sweep), 'set_' + str(parameter_to_sweep))(value=value)
                        dataframe.append(getattr(self, 'value' + str(axis)))
                        if back == False:
                            setattr(self, 'value' + str(axis), getattr(self, 'value' + str(axis)) + getattr(self, 'step' + str(axis)))
                        else:
                            setattr(self, 'value' + str(axis), getattr(self, 'value' + str(axis)) - getattr(self, 'step' + str(axis)))
                    else:
                        getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep)]](
                            adress=device_to_sweep), 'set_' + str(parameter_to_sweep))(value=value)
                        dataframe.append(value)
                    
                    delay_factor = globals()['delay_factor' + str(axis)]
                    time.sleep(delay_factor)
                    ###################
                    globals()['self'] = self
                    exec(script, globals())
                    return 
                else:
                    try_tozero()
                    
                    stop_flag = True
                    
            else:
                time.sleep(1)
                step(axis, value)
            
            if value == 'None':
                print('Step was made through axis ' + axis + '\nValue = ' + getattr(self, 'value' + axis))
        
        def update_filename():
            '''Add +1 to filename_sweep'''
            global filename_sweep
            global cur_dir
            global DAY
            global MONTH
            global YEAR
            global sweeper_flag1
            global sweeper_flag2
            global sweeper_flag3
            
            files = os.listdir(cur_dir + '\data_files')
            ind = [0]
            basic_name = filename_sweep[len(cur_dir + '\data_files') + 1:-4]
            if '-' in basic_name:
                basic_name = basic_name[:basic_name.find('-')]
            if '_' in basic_name:
                basic_name = basic_name[:basic_name.find('_')]
            if '_' in basic_name:
                basic_name = basic_name[:basic_name.find('_')]
            print(basic_name)
            for file in files:
                if basic_name in file and 'manual' not in file:
                    index_start = len(file) - file[::-1].find('-') - 1
                    index_stop = file.find('.csv')
                    ind.append(int(file[index_start + 1 : index_stop]))
            previous_ind = np.max(ind)
            print(previous_ind)
            if sweeper_flag1 == True:
                filename_sweep = f'{cur_dir}\data_files\{basic_name}-{previous_ind + 1}.csv'
            elif sweeper_flag2 == True:
                value1 = self.value1
                integer1 = int(value1)
                fractional1 = int(10 * (value1 % 1))
                filename_sweep = f'{cur_dir}\data_files\{basic_name}_{integer1}.{fractional1}-{previous_ind + 1}.csv'
            elif sweeper_flag3 == True:
                value1 = self.value1
                value2 = self.value2
                integer1 = int(value1)
                fractional1 = int(10 * (value1 % 1))
                integer2 = int(value2)
                fractional2 = int(10 * (value2 % 1))
                filename_sweep = f'{cur_dir}\data_files\{basic_name}_{integer1}.{fractional1}_{integer2}.{fractional2}-{previous_ind + 1}.csv'
                
            
            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
            globals()['dataframe'].to_csv(filename_sweep, index=False)
            
            print('Filename updated')
        
        def back_and_forth_transposition(axis, full = True):
            
            '''Changes sweep direction'''
            
            axis = str(axis)
            if full == True:
                dub = globals()['to_sweep' + axis]
                globals()['to_sweep' + axis] = globals()['from_sweep' + axis]
                globals()['from_sweep' + axis] = dub
                setattr(self, 'step' + axis, - getattr(self, 'step' + axis))
                globals()['ratio_sweep' + axis] = - globals()['ratio_sweep' + axis]
            else:
                setattr(self, 'value' + axis, globals()['from_sweep' + axis])
                
            print(f'Back and forth transposition (axis = {axis}) happened\nNow From is {globals()["from_sweep" + axis]}, To is {globals()["to_sweep" + axis]}')
            
        def determine_step(i, data, axis):
            
            '''Determine a step if sweep is manual
            Go to manual sweep file and substract neares values'''
            
            axis = str(axis)
            setattr(self, 'value' + axis, data[i])
            try:
                setattr(self, 'step' + axis, abs(data[i+1] - data[i-1]) / 2)
            except IndexError:
                try:
                    setattr(self, 'step' + axis, abs(data[i] - data[i-1]))
                except IndexError:
                    setattr(self, 'step' + axis, abs(data[i] - data[i+1]))
                    
            print('Step was determined')
                    
        def update_dataframe(sure = None):
            
            '''Create dataframe duplicate for further update
            sure = True only for 3D sweep for axis = 2'''
            if len(manual_sweep_flags) == 1:
                globals()['dataframe'] = [time.perf_counter() - zero_time]
            if len(manual_sweep_flags) == 2 or sure == True:
                globals()['dataframe'] = [*globals()['dataframe_after']]
            if len(manual_sweep_flags) == 3 and sure == None:
                globals()['dataframe'] = [*globals()['dataframe_after_after']]
                
            print('Dataframe updated')
                
            
        def current_point():
            global manual_sweep_flags
            
            '''Determines current point in sweep space and its boundaries'''
            
            point = []
            dgrid_area = []
            for ind, flag in enumerate(manual_sweep_flags):
                if flag == 0:
                    point.append(getattr(self, 'value' + str(ind + 1)))
                    dgrid_area.append(getattr(self, 'step' + str(ind + 1)) / 2)
                else:
                    point.append(globals()['value' + str(ind + 1)])
                    dgrid_area.append(getattr(self, 'step' + str(ind + 1)) / 2)
                    
            print('Current point was determined')
            return point, dgrid_area

        def inner_step(value1 = None, value2 = None, value3 = None):
            global manual_sweep_flags
            '''Performs single step in a slave-axis'''
            
            globals()['value1'] = value1
            globals()['value2'] = value2
            globals()['value3'] = value3
            
            if len(manual_sweep_flags) == 1:
                update_dataframe()
                step(1, value1)
                append_read_parameters()
                tofile() 
            else:
                point, dgrid_area = current_point()
                if self.isinarea(point = point, grid_area = self.grid_space, dgrid_area = dgrid_area):
                    if len(manual_sweep_flags) == 2:
                        update_dataframe()
                        step(2, value2)
                    else:
                        update_dataframe()
                        step(3, value3)
                    append_read_parameters()
                    tofile() 
                else:
                    if manual_sweep_flags[1] == 0:
                        self.value2 += self.step2
                    else:
                        pass
                    try:
                        if manual_sweep_flags[2] == 0:
                            self.value3 += self.step3
                        else:
                            pass
                    except IndexError:
                        pass
                
            print('Inner step was made')
                
        def inner_loop_single(direction = 1):
            '''commits a walk through mater (for 1d), slave (for 2d) or slave-slave (for 3d) axis'''
            
            if manual_sweep_flags[len(manual_sweep_flags) - 1] == 0:
                while condition(len(manual_sweep_flags)) and manual_sweep_flags[len(manual_sweep_flags) - 1] == 0:
                    inner_step()
            elif manual_sweep_flags[len(manual_sweep_flags) - 1] == 1:
                data_inner = pd.read_csv(manual_filenames[len(manual_filenames) - 1]).values.reshape(-1)
                for i, value in enumerate(data_inner[::direction]):
                    if manual_sweep_flags[len(manual_sweep_flags) - 1] == 1:
                        data_inner = pd.read_csv(manual_filenames[len(manual_filenames) - 1]).values.reshape(-1)
                        determine_step(i, data_inner, len(manual_sweep_flags))
                        if len(manual_sweep_flags) == 1:
                            inner_step(value1 = value)
                        elif len(manual_sweep_flags) == 2:
                            inner_step(value2 = value)
                        elif len(manual_sweep_flags) == 3:
                            inner_step(value3 = value)
                        else:
                            raise Exception('manual_sweep_flag length is not correct, needs 1, 2 or 3, but got ', len(manual_sweep_flags))
                    else:
                        break
            else:
                raise Exception('manual_sweep_flag is not correct, needs 0 or 1, but got ', manual_sweep_flags[len(manual_sweep_flags) - 1])
            
            print('Single inner loop was made')
            
        def inner_loop_back_and_forth():
            '''travels through a slave-slave axis back and forth as many times, as was given'''
            global back_and_forth_master
            global back_and_forth_slave
            global back_and_forth_slave_slave
            global manual_sweep_flags
            
            flags_dict = {1: 'back_and_forth_master', 2: 'back_and_forth_slave', 3: 'back_and_forth_slave_slave'}
            walks = globals()[flags_dict[len(manual_sweep_flags)]]
            if walks == 1:
                inner_loop_single()
                back_and_forth_transposition(len(manual_sweep_flags), False)
            
            elif walks > 1:
                for i in range(1, walks + 1):
                    inner_loop_single(direction = round(2 * (i % 2) - 1))
                    step(axis = len(manual_sweep_flags), back = True)
                    back_and_forth_transposition(len(manual_sweep_flags))
                        
                if walks % 2 == 1:
                    back_and_forth_transposition(len(manual_sweep_flags))
                    
            else:
                raise Exception('back_and_forth_slave is not correct, needs >= 1, but got ', back_and_forth_slave)
               
            print('Inner loop was made back and forth') 
               
        def external_loop_single(direction = 1):
            '''perform sequence of steps through master (for 2-d) or slave (for 3-d) axis
            with inner_loop on each step'''
            
            cur_axis = len(manual_sweep_flags) - 1
            if manual_sweep_flags[-1] == 0:
                while condition(cur_axis) and manual_sweep_flags[-1] == 0:
                    if len(manual_sweep_flags) == 3:
                        update_dataframe(True)
                    step(cur_axis)
                    if len(manual_sweep_flags) == 2:
                        globals()['dataframe_after'] = [*globals()['dataframe']]
                    elif len(manual_sweep_flags) == 3:
                        globals()['dataframe_after_after'] = [*globals()['dataframe']]
                    else:
                        raise Exception('manual_sweep_flag is not correct size, should be 1, 2 or 3, but got ', len(manual_sweep_flags))
                    inner_loop_back_and_forth()
                    update_filename()
                    
            elif manual_sweep_flags[-1] == 1:
                data_middle = pd.read_csv(manual_filenames[-1]).values.reshape(-1)
                for i, value in enumerate(data_middle[::direction]):
                    if manual_sweep_flags[-1] == 1:
                        determine_step(i, data_middle, cur_axis)
                        step(cur_axis, value = value)
                        if len(manual_sweep_flags) == 2:
                            globals()['dataframe_after'] = [*globals()['dataframe']]
                        else:
                            globals()['dataframe_after_after'] = [*globals()['dataframe']]
                        inner_loop_back_and_forth()
                        update_filename()
                    else:
                        break
            else:
                raise Exception('manual_sweep_flag is not correct, needs 0 or 1, but got ', manual_sweep_flags[-1])
            
            print('Single external loop was made')
            
        def external_loop_back_and_forth():
            '''travels through a slave axis back and forth as many times, as was given'''
            global back_and_forth_master
            global back_and_forth_slave
            
            flags_dict = {2: 'back_and_forth_master', 3: 'back_and_forth_slave'}
            walks = globals()[flags_dict[len(manual_sweep_flags)]]
            if walks == 1:
                external_loop_single()
                back_and_forth_transposition(len(manual_sweep_flags) - 1, False)
            
            elif walks > 1:
                for i in range(1, walks + 1):
                    external_loop_single(round(2 * (i % 2) - 1))
                    step(axis = len(manual_sweep_flags), back = True)
                    back_and_forth_transposition(len(manual_sweep_flags) - 1)
                    
                if back_and_forth_master % 2 == 1:
                    back_and_forth_transposition(len(manual_sweep_flags) - 1)
                    
            else:
                raise Exception(f'{flags_dict[len(manual_sweep_flags)]} is not correct, needs > 1, but got ', walks)

            print('External loop was made back and forth')

        def master_loop_single(direction = 1):
            '''perform sequence of steps through master (3-d) axis
            with external_loop_back_and_forth on each step'''

            if manual_sweep_flags[0] == 0:
                while condition(1) and manual_sweep_flags[0] == 0:
                    step(1)
                    globals()['dataframe_after'] = [*globals()['dataframe']]
                    external_loop_back_and_forth()
                    update_filename()
            elif manual_sweep_flags[0] == 1:
                data_external = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for i, value in enumerate(data_external[::direction]):
                    if manual_sweep_flags[0] == 1:
                        determine_step(i, data_external, 1)
                        step(1, value = value)
                        globals()['dataframe_after'] = [*globals()['dataframe']]
                        external_loop_back_and_forth()
                        update_filename()
                    else:
                        break
            else:
                raise Exception('manual_sweep_flag is not correct, needs 0 or 1, but got ', manual_sweep_flags[-2])
            
            print('Single master loop was made')

        def master_loop_back_and_forth():
            '''travels through a master axis back and forth as many times, as was given'''
            global back_and_forth_master
            
            walks = back_and_forth_master
            if walks == 1:
                master_loop_single()
                back_and_forth_transposition(1, False)
            
            elif walks > 1:
                for i in range(1, walks + 1):
                    master_loop_single(round(2 * (i % 2) - 1))
                    step(axis = 1, back = True)
                    back_and_forth_transposition(1)
                    
                if back_and_forth_master % 2 == 1:
                    back_and_forth_transposition(1)
                    
            else:
                raise Exception('back_and_forth_master is not correct, needs > 1, but got ', walks)

            print('External loop was made back and forth')
        
        if self.sweeper_flag1 == True:
            
            zero_time = time.perf_counter()
    
            update_filename()
            
            if len(manual_sweep_flags) == 1:        
                inner_loop_back_and_forth()
                self.sweeper_flag1 == False

        if self.sweeper_flag2 == True:
            
            zero_time = time.perf_counter()

            if self.time1 > self.time2 and master_lock == False:
                self.transposition(1, 2)
                manual_sweep_flags = manual_sweep_flags[::-1]
                manual_filenames = manual_filenames[::-1]
                columns[1:3] = columns[1:3][:-1]
            
            update_filename()

            if len(manual_sweep_flags) == 2:        
                external_loop_back_and_forth()
                self.sweeper_flag2 == False

            self.sweeper_flag2 == False

        if self.sweeper_flag3 == True:

            if self.time1 > self.time2 and master_lock == False:
                self.transposition(1, 2)
                manual_sweep_flags[0:2] = manual_sweep_flags[0:2][::-1]
                manual_filenames[0:2] = manual_filenames[0:2][::-1]
                columns[1:3] = columns[1:3][:-1]
            if self.time1 > self.time3 and master_lock == False:
                self.transposition(1, 3)
                manual_sweep_flags = manual_sweep_flags[::-1]
                manual_filenames = manual_filenames[::-1]
                columns[1:4] = columns[1:4][:-1]
            if self.time2 > self.time3 and master_lock == False:
                self.transposition(2, 3)
                manual_sweep_flags[1:3] = manual_sweep_flags[1:3][::-1]
                manual_filenames[1:3] = manual_filenames[1:3][::-1]
                columns[2:4] = columns[1:3][:-1]

            update_filename()

            if len(manual_sweep_flags) == 3:
                master_loop_back_and_forth()
                self.sweeper_flag3 == False

class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=True)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="White", padx=2)
        s.pack(side=tk.TOP, pady = 5, fill="both", expand=True)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass

class FigureSettings(object):
    
    def __init__(self, widget):
        self.widget = widget
        self.id = None
        self.x = self.y = 0
            
    def show_plot_settings(self, ax):
        x, y, cx, cy = self.widget.bbox('all')
        x = x + self.widget.winfo_rootx()
        y = y + self.widget.winfo_rooty()
        self.settings_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        self.entry_title = tk.Entry(tw)
        self.entry_title.insert(index = 0, string = str(ax.get_title()))
        self.entry_title.grid(row = 0, column = 0, pady = 2)
        
        button_close = tk.Button(tw, text = '❌', command = lambda: self.hide_title_settings(ax))
        button_close.grid(row = 0, column = 1, pady = 2)
        
    def hide_title_settings(self, ax):
    
        try:
            ax.set_title(self.entry_title.get(), fontsize = 8, pad = -5)
        except:
            pass
        
        self.settings_window.destroy()
    
    def showsettings(self, ax):
        x, y, cx, cy = self.widget.bbox('all')
        x = x + self.widget.winfo_rootx()
        y = y + self.widget.winfo_rooty()
        self.settings_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        self.entry_title = tk.Entry(tw)
        self.entry_title.insert(index = 0, string = str(ax.get_title()))
        self.entry_title.grid(row = 0, column = 1, pady = 2)
        
        button_close = tk.Button(tw, text = '❌', command = lambda: self.hidesettings(ax))
        button_close.grid(row = 0, column = 5, pady = 2)
        
        label_x_device = tk.Label(tw, text = 'x')
        label_x_device.grid(row = 1, column = 0, pady = 2, sticky = tk.W)
        
        self.combo_x_device = ttk.Combobox(tw, values=globals()['columns'])
        self.combo_x_device.bind("<<ComboboxSelected>>", lambda event: self.ax_update(ax, event))
        self.combo_x_device.grid(row = 1, column = 1, pady = 2)
        
        label_log_x = tk.Label(tw, text = 'log')
        label_log_x.grid(row = 1, column = 3, pady = 2)
        
        self.status_log_x = tk.IntVar()
        self.checkbox_log_x = tk.Checkbutton(tw, 
                                             command= lambda: self.save_log_x_status(ax), 
                                             variable = self.status_log_x,
                                             onvalue = 0, offvalue = 1)
        self.checkbox_log_x.grid(row = 1, column = 4, pady = 2)
        CreateToolTip(self.checkbox_log_x, 'Set x logscale')
        
        label_y_device = tk.Label(tw, text = 'y')
        label_y_device.grid(row = 2, column = 0, pady = 2, sticky = tk.W)
        
        self.combo_y_device = ttk.Combobox(tw, values=globals()['columns'])
        self.combo_y_device.bind("<<ComboboxSelected>>", lambda event: self.ax_device_update(ax, event))
        self.combo_y_device.grid(row = 2, column = 1, pady = 2)
        
        label_log_y = tk.Label(tw, text = 'log')
        label_log_y.grid(row = 2, column = 3, pady = 2)
        
        self.status_log_y = tk.IntVar()
        self.checkbox_log_y = tk.Checkbutton(tw, 
                                             command=lambda: self.save_log_y_status(ax), 
                                             variable = self.status_log_y,
                                             onvalue = 0, offvalue = 1)
        self.checkbox_log_y.grid(row = 2, column = 4, pady = 2)
        CreateToolTip(self.checkbox_log_y, 'Set y logscale')
        
        label_xlim = tk.Label(tw, text = 'x lim = ')
        label_xlim.grid(row = 3, column = 0, pady = 2, sticky = tk.W)
        
        self.status_xlim = tk.IntVar()
        self.status_xlim.set(0)
        
        self.entry_x_from = tk.Entry(tw, width = 8)
        self.entry_x_from.grid(row = 3, column = 1, pady = 2, sticky = tk.W)
        
        label_dash_x = tk.Label(tw, text = ' - ')
        label_dash_x.grid(row = 3, column = 1, pady = 2)
        
        self.entry_x_to = tk.Entry(tw, width = 8)
        self.entry_x_to.grid(row = 3, column = 1, pady = 2, sticky = tk.E)
        
        checkbox_xlim = tk.Checkbutton(tw, command = lambda: self.set_xlim(ax))
        checkbox_xlim.grid(row = 3, column = 3, pady = 2)
        CreateToolTip(checkbox_xlim, 'Set x autoscale off')
        
        label_ylim = tk.Label(tw, text = 'y lim = ')
        label_ylim.grid(row = 4, column = 0, pady = 2, sticky = tk.W)
        
        self.status_ylim = tk.IntVar()
        self.status_ylim.set(0)
        
        self.entry_y_from = tk.Entry(tw, width = 8)
        self.entry_y_from.grid(row = 4, column = 1, pady = 2, sticky = tk.W)
    
        label_dash_y = tk.Label(tw, text = ' - ')
        label_dash_y.grid(row = 4, column = 1, pady = 2)
        
        self.entry_y_to = tk.Entry(tw, width = 8)
        self.entry_y_to.grid(row = 4, column = 1, pady = 2, sticky = tk.E)
        
        checkbox_ylim = tk.Checkbutton(tw, command = lambda: self.set_ylim(ax))
        checkbox_ylim.grid(row = 4, column = 3, pady = 2)
        CreateToolTip(checkbox_ylim, 'Set y autoscale off')
        
        label_xlabel = tk.Label(tw, text = 'x label = ')
        label_xlabel.grid(row = 5, column = 0, pady = 2, sticky = tk.W)
        
        self.entry_xlabel = tk.Entry(tw)
        self.entry_xlabel.insert(index = 0, string = 'x')
        self.entry_xlabel.grid(row = 5, column = 1)
    
        label_ylabel = tk.Label(tw, text = 'y label = ')
        label_ylabel.grid(row = 6, column = 0, pady = 2, sticky = tk.W)
        
        self.entry_ylabel = tk.Entry(tw)
        self.entry_ylabel.insert(index = 0, string = 'y')
        self.entry_ylabel.grid(row = 6, column = 1, pady = 2)
        
        label_x_transformation = tk.Label(tw, text = 'x = ')
        label_x_transformation.grid(row = 7, column = 0, pady = 2, sticky = tk.W)
        CreateToolTip(label_x_transformation, 'X transformation')
        
        self.entry_x_transformation = tk.Entry(tw)
        self.entry_x_transformation.insert(index = 0, string = globals()[f'x_transformation{var2str(ax)[len(var2str(ax)) - 1]}'])
        self.entry_x_transformation.grid(row = 7, column = 1, pady = 2)
        
        label_y_transformation = tk.Label(tw, text = 'y = ')
        label_y_transformation.grid(row = 8, column = 0, pady = 2, sticky = tk.W)
        CreateToolTip(label_y_transformation, 'Y transformation')
        
        self.entry_y_transformation = tk.Entry(tw)
        self.entry_y_transformation.insert(index = 0, string = globals()[f'y_transformation{var2str(ax)[len(var2str(ax)) - 1]}'])
        self.entry_y_transformation.grid(row = 8, column = 1, pady = 2)
        
    def save_log_x_status(self, ax):
        if self.status_log_x.get() == 0:
            self.status_log_x.set(1)
            ax.set_xscale('log')
        elif self.status_log_x.get() == 1:
            self.status_log_x.set(0)
            ax.set_xscale('linear')
        
    def save_log_y_status(self, ax):
        if self.status_log_y.get() == 0:
            self.status_log_y.set(1)
            ax.set_yscale('log')
        elif self.status_log_y.get() == 1:
            self.status_log_y.set(0)
            ax.set_yscale('linear')
            
    def set_xlim(self, ax):
        if self.status_xlim.get() == 0:
            ax.autoscale(enable = False, axis = 'x')
            globals()[f'x{var2str(ax)[len(var2str(ax)) - 1]}_autoscale'] = False
            self.status_xlim.set(1)
        elif self.status_xlim.get() == 1:
            ax.autoscale(enable = True, axis = 'x')
            globals()[f'x{var2str(ax)[len(var2str(ax)) - 1]}_autoscale'] = True
            self.status_xlim.set(0)
        
    def set_ylim(self, ax):
        if self.status_ylim.get() == 0:
            ax.autoscale(enable = False, axis = 'y')
            globals()[f'y{var2str(ax)[len(var2str(ax)) - 1]}_autoscale'] = False
            self.status_ylim.set(1)
        elif self.status_ylim.get() == 1:
            ax.autoscale(enable = True, axis = 'y')
            globals()[f'y{var2str(ax)[len(var2str(ax)) - 1]}_autoscale'] = True
            self.status_ylim.set(0)
        
    def ax_update(self, ax, event):
        
        order = var2str(ax)[len(var2str(ax)) - 1]
        
        globals()[f'x{order}_status'] = self.combo_x_device.current()
        globals()[f'y{order}_status'] = self.combo_y_device.current()
        
        xscale_status = ax.get_xscale()
        yscale_status = ax.get_yscale()
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.clear()
        ax.set_xscale(xscale_status)
        ax.set_yscale(yscale_status)
        getattr(Graph, 'axes_settings')(i, order)
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        ax.autoscale(enable = globals()[f'x{order}_autoscale'], axis = 'x')
        ax.autoscale(enable = globals()[f'y{order}_autoscale'], axis = 'y')
    
    def hidesettings(self, ax):
        global x_transformation
        global y_transformation
        
        tw = self.settings_window
        if self.status_xlim.get() == 1:
            try:
                ax.set_xlim(left = float(self.entry_x_from.get()), right = float(self.entry_x_to.get()))
            except:
                pass
        if self.status_ylim.get() == 1:
            try:
                ax.set_ylim(bottom = float(self.entry_y_from.get()), top = float(self.entry_y_to.get()))
            except:
                pass
        
        try:
            ax.set_xlabel(self.entry_xlabel.get(), fontsize = 8)
        except:
            pass
        
        try:
            ax.set_ylabel(self.entry_ylabel.get(), fontsize = 8)
        except:
            pass
        
        try:
            globals()[f'x_transformation{var2str(ax)[len(var2str(ax)) - 1]}'] = self.entry_x_transformation.get()
        except:
            pass
    
        try:
            globals()[f'y_transformation{var2str(ax)[len(var2str(ax)) - 1]}'] = self.entry_y_transformation.get()
        except:
            pass
        
        if tw:
            tw.destroy()
        
def CreateFigureSettings(widget, ax):
    settingsFigure = FigureSettings(widget)
    def enter(event):
        settingsFigure.showsettings(ax)
    widget.bind('<Button-3>', enter)
    widget.bind('<Double-1>', enter)
    
class StartAnimation:
    
    def start():
        global cur_animation_num
        i = cur_animation_num
        globals()[f'animation{i}'] = blit_animation.FuncAnimation(
            fig = globals()[f'fig{i}'], func = lambda x: my_animate(x, n = i), interval=interval, blit = False)
        cur_animation_num += 1

class Graph():
    
    def __init__(self):
        self.tw = tk.Toplevel(globals()['Sweeper_object'])
        
        self.tw.geometry("1920x1080")
        self.tw.title("Graph")
        
        self.order = globals()['cur_animation_num'] 

        self.create_fig(self.order, (2.5, 1.65))
        self.create_fig(self.order + 1, (1.5, 0.8))
        self.create_fig(self.order + 2, (1.5, 0.8))

        label_x1 = tk.Label(self.tw, text='x', font=LARGE_FONT)
        label_x1.place(relx=0.02, rely=0.76)

        label_y1 = tk.Label(self.tw, text='y', font=LARGE_FONT)
        label_y1.place(relx=0.15, rely=0.76)

        self.combo_x1 = ttk.Combobox(self.tw, values=columns)
        self.combo_x1.bind("<<ComboboxSelected>>", lambda event: self.ax_update(1, event))
        self.combo_x1.place(relx=0.035, rely=0.76)

        self.combo_y1 = ttk.Combobox(self.tw, values=columns)
        self.combo_y1.bind("<<ComboboxSelected>>", lambda event: self.ax_update(1, event))
        self.combo_y1.place(relx=0.165, rely=0.76)

        globals()[f'self.plot{self.order}'] = FigureCanvasTkAgg(globals()[f'fig{self.order}'], self.tw)
        globals()[f'self.plot{self.order}'].draw()
        globals()[f'self.plot{self.order}'].get_tk_widget().place(relx=0, rely=0)
        CreateFigureSettings(globals()[f'self.plot{self.order}'].get_tk_widget(), globals()[f'ax{self.order}'])
        CreateToolTip(globals()[f'self.plot{self.order}'].get_tk_widget(), 'Right click to configure')

        globals()[f'self.toolbar{self.order}'] = VerticalNavigationToolbar2Tk(globals()[f'self.plot{self.order}'], self.tw)
        globals()[f'self.toolbar{self.order}'].config(background = 'White')
        globals()[f'self.toolbar{self.order}'].update()
        globals()[f'self.toolbar{self.order}'].place(relx=0, rely=0)
        globals()[f'self.plot{self.order}']._tkcanvas.place(relx=0, rely=0)

        globals()[f'self.plot{self.order + 1}'] = FigureCanvasTkAgg(globals()[f'fig{self.order + 1}'], self.tw)
        globals()[f'self.plot{self.order + 1}'].draw()
        globals()[f'self.plot{self.order + 1}'].get_tk_widget().place(relx=0.52, rely=0)
        CreateFigureSettings(globals()[f'self.plot{self.order + 1}'].get_tk_widget(), globals()[f'ax{self.order + 1}'])
        CreateToolTip(globals()[f'self.plot{self.order + 1}'].get_tk_widget(), 'Right click to configure')
        globals()[f'self.plot{self.order + 1}']._tkcanvas.place(relx=0.62, rely=0)

        globals()[f'self.plot{self.order + 2}'] = FigureCanvasTkAgg(globals()[f'fig{self.order + 2}'], self.tw)
        globals()[f'self.plot{self.order + 2}'].draw()
        globals()[f'self.plot{self.order + 2}'].get_tk_widget().place(relx=0.02, rely=0.50)
        CreateFigureSettings(globals()[f'self.plot{self.order + 2}'].get_tk_widget(), globals()[f'ax{self.order + 2}'])
        CreateToolTip(globals()[f'self.plot{self.order + 2}'].get_tk_widget(), 'Right click to configure')
        globals()[f'self.plot{self.order + 2}']._tkcanvas.place(relx=0.62, rely=0.39)
        
        self.table_dataframe = ttk.Treeview(self.tw, columns = columns, show = 'headings', height = 1)
        self.table_dataframe.place(relx = 0.28, rely = 0.76)
        
        self.initial_value = []
        
        for ind, heading in enumerate(columns):
            self.table_dataframe.heading(ind, text = heading)
            self.table_dataframe.column(ind,anchor=tk.CENTER, stretch=tk.NO, width=80)
            self.initial_value.append(heading)
                
        self.table_dataframe.insert('', tk.END, 'Current dataframe', text = 'Current dataframe', values = self.initial_value)
        
        self.update_item('Current dataframe')
        
        self.button_pause = tk.Button(self.tw, text = '⏸️', font = LARGE_FONT, command = lambda: globals()['Sweeper_object'].pause())
        self.button_pause.place(relx = 0.02, rely = 0.82)
        CreateToolTip(self.button_pause, 'Pause\Continue sweep')
        
        self.button_stop = tk.Button(self.tw, text = '⏹️', font = LARGE_FONT, command = lambda: globals()['Sweeper_object'].stop())
        self.button_stop.place(relx = 0.06, rely = 0.82)
        CreateToolTip(self.button_stop, 'Stop sweep')
        
        self.button_tozero = tk.Button(self.tw, text = 'To zero', width = 11, command = lambda: globals()['Sweeper_object'].tozero())
        self.button_tozero.place(relx = 0.1, rely = 0.82, width = 48, height = 32)
        
    def axes_settings(self, i, pad = 0, tick_size = 4, label_size = 6, x_pad =0, y_pad = 1, title_size = 8, title_pad = -5):
        globals()[f'ax{i}'].tick_params(axis='y', which='major', length = 0, pad=pad, labelsize=tick_size)
        globals()[f'ax{i}'].tick_params(axis='x', which='major', length = 0, pad=pad + 1, labelsize=tick_size)
        globals()[f'ax{i}'].set_xlabel('x', fontsize = label_size, labelpad = x_pad)
        globals()[f'ax{i}'].set_ylabel('y', fontsize = label_size, labelpad = y_pad)
        globals()[f'ax{i}'].set_title(f'Plot {i}', fontsize = title_size, pad = title_pad)
        

    def create_fig(self, i, figsize, pad = 0, tick_size = 4, label_size = 6, x_pad =0, y_pad = 1, title_size = 8, title_pad = -5):
        globals()[f'fig{i}'] = Figure(figsize, dpi=300)
        globals()[f'ax{i}'] = globals()[f'fig{i}'].add_subplot(111)
        globals()[f'x_transformation{i}'] = 'x'
        globals()[f'y_transformation{i}'] = 'y'
        globals()[f'x{i}_autoscale'] = True
        globals()[f'y{i}_autoscale'] = True
        ax = globals()[f'ax{i}']
        ax.bbox.union([label.get_window_extent() for label in ax.get_xticklabels()])
        self.axes_settings(i, pad, tick_size, label_size, x_pad, y_pad, title_size, title_pad)

    def update_idletasks(self):
        self.tw.update_idletasks()
        
    def update(self):
        self.tw.update()

    def ax_update(self, n, event):
        '''n - order of figure'''
        globals()[f'x{self.order}_status'] = self.combo_x1.current()
        globals()[f'y{self.order}_status'] = self.combo_y1.current()
        
        ax = globals()[f'ax{self.order}']
        order = self.order + n - 1
        
        xscale_status = ax.get_xscale()
        yscale_status = ax.get_yscale()
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        ax.clear()
        ax.set_xscale(xscale_status)
        ax.set_yscale(yscale_status)
        self.axes_settings(i = order)
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        ax.autoscale(enable = globals()[f'x{order}_autoscale'], axis = 'x')
        ax.autoscale(enable = globals()[f'y{order}_autoscale'], axis = 'y')
        
    def update_item(self, item):
        try:
            dataframe = pd.read_csv(filename_sweep).tail(1).values.flatten().round(2)
            self.table_dataframe.item(item, values=tuple(dataframe))
            self.table_dataframe.after(500, self.update_item, item)
        except FileNotFoundError:
            self.table_dataframe.after(500, self.update_item, item)

interval = 200


def main():
    #write_config_parameters()
    #write_config_channels()
    app = Universal_frontend(classes=(StartPage, Sweeper1d, Sweeper2d, Sweeper3d),
                             start=StartPage)
    app.mainloop()
    while True:
        pass


if __name__ == '__main__':
    main()
