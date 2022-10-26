import os
cur_dir = os.getcwd() 
import re
import json
from csv import writer
import threading
from tkinter import ttk
import tkinter as tk
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import pyvisa as visa
from pyvisa import constants
import time
from datetime import datetime
import pandas as pd
import matplotlib
import numpy as np
import random
matplotlib.use("TkAgg")
plt.rcParams['animation.html'] = 'jshtml'
LARGE_FONT = ('Verdana', 12)
SUPER_LARGE = ('Verdana', 16)
style.use('ggplot')

# Check if everything connected properly
rm = visa.ResourceManager()
list_of_devices = rm.list_resources()

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
from_sweep1 = 0
to_sweep1 = 1
ratio_sweep1 = 0.1
delay_factor1 = 0.1
from_sweep2 = 0
to_sweep2 = 1
ratio_sweep2 = 0.1
delay_factor2 = 0.1
from_sweep3 = 0
to_sweep3 = 1
ratio_sweep3 = 0.1
delay_factor3 = 0.1
filename_sweep = cur_dir + '\data_files\sweep' + datetime.today().strftime(
    '%H_%M_%d_%m_%Y') + '.csv'
sweeper_flag1 = False
sweeper_flag2 = False
sweeper_flag3 = False

settings_flag = False

pause_flag = False
stop_flag = False
tozero_flag = False

condition = ''

manual_sweep_flags = [0]
manual_filenames = [cur_dir + '\data_files\manual' + datetime.today().strftime(
    '%H_%M_%d_%m_%Y') + '.csv']

master_lock = False

back_and_forth_slave = False
back_and_forth_master = False

columns = []

# variables for plotting

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
            return [time.process_time() - zero_time, self.x, self.y]
        except:
            pass
        # return [time.process_time() - zero_time, float(np.random.randint(10)), float(np.random.randint(10))]

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

    def set_T1_min(self, t1_min=0):
        # Set the CH1 Target Temperature Min value,
        # (Range: -200 to TMAX1°C, with a resolution of 1°C).
        self.tc.write('TMIN1=' + str(t1_min))

    def set_T1_max(self, t1_max=30):
        # Set the CH1 Target Temperature Max value, n equals value
        # TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t1_max))

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

    def set_T2_min(self, t2_min=0):
        # Set the CH2 Target Temperature Min value,
        # (Range: -200 to TMAX2°C, with a resolution of 1°C).
        self.tc.write('TMIN1=' + str(t2_min))

    def set_T2_max(self, t2_max=20):
        # Set the CH2 Target Temperature Max value, n equals value
        # TMIN1 to 400°C, with a resolution of 1°C).
        self.tc.write('T1MAX=' + str(t2_max))


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
        
with open(cur_dir + '\\config\\adress_dictionary.txt', 'r') as file:
    adress_dict = file.read()
adress_dict = json.loads(adress_dict)
    
for ind_, type_ in enumerate(types_of_devices):
    if type_ == 'Not a class':
        print(1)
        if list_of_devices[ind_] in list(adress_dict.keys()):
            print(2)
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

zero_time = time.process_time()

# animation functions

# defining plots initial parameters
labelsize = 4
pad = 1

fig221 = Figure(figsize=(1.8, 1), dpi=300)
ax1 = fig221.add_subplot(111)
ax1.tick_params(axis='both', which='major', pad=pad, labelsize=labelsize)

fig222 = Figure(figsize=(1.8, 1), dpi=300)
ax2 = fig222.add_subplot(111)
ax2.tick_params(axis='both', which='major', pad=pad, labelsize=labelsize)

fig223 = Figure(figsize=(1.8, 1), dpi=300)
ax3 = fig223.add_subplot(111)
ax3.tick_params(axis='both', which='major', pad=pad, labelsize=labelsize)

fig224 = Figure(figsize=(1.8, 1), dpi=300)
ax4 = fig224.add_subplot(111)
ax4.tick_params(axis='both', which='major', pad=pad, labelsize=labelsize)


def animate221(i):
    # function to animate graph on each step
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
        ax1.clear()
        ax1.plot(x1, y1, '-', lw=1, color='darkblue')
        print(x1, y1)
    except FileNotFoundError:
        ax1.clear()
        ax1.plot(x1, y1, '-', lw=1, color='darkblue')


def animate222(i):
    # function to animate graph on each step
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
        ax2.clear()
        ax2.plot(x2, y2, '-', lw=1, color='crimson')
    except FileNotFoundError:
        ax2.clear()
        ax2.plot(x2, y2, '-', lw=1, color='crimson')


def animate223(i):
    # function to animate graph on each step
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
        ax3.clear()
        ax3.plot(x3, y3, '-', lw=1, color='darkgreen')
    except FileNotFoundError:
        ax3.clear()
        ax3.plot(x3, y3, '-', lw=1, color='darkgreen')


config_parameters_filename = cur_dir + '\config\parameters_' + datetime.today().strftime(
    '%H_%M_%d_%m_%Y') + '.csv' '.csv'

config_parameters = pd.DataFrame(columns=['Sensitivity', 'Time_constant',
                                 'Low_pass_filter_slope', 'Synchronous_filter_status',
                                          'Remote', 'Amplitude', 'Frequency',
                                          'Phase'])

config_parameters.to_csv(config_parameters_filename, index=False)

config_channels_filename = cur_dir + '\config\channels_' + datetime.today().strftime(
    '%H_%M_%d_%m_%Y') + '.csv' '.csv'

config_channels = pd.DataFrame(columns=['Ch1', 'Ch2'])

config_channels.to_csv(config_channels_filename, index=False)


class write_config_parameters(threading.Thread):

    def __init__(self, adress='GPIB0::3::INSTR'):
        threading.Thread.__init__(self)
        self.adress = adress
        self.daemon = True
        self.start()

    def run(self):
        while True:
            dataframe_parameters = lock_in(adress=self.adress).parameter()
            with open(config_parameters_filename, 'a') as f_object:
                try:
                    # Pass this file object to csv.writer()
                    # and get a writer object
                    writer_object = writer(f_object)

                    # Pass the list as an argument into
                    # the writerow()
                    writer_object.writerow(*dataframe_parameters.values)
                    time.sleep(5)

                    # Close the file object
                    f_object.close()
                except KeyboardInterrupt():
                    f_object.close()


class write_config_channels(threading.Thread):

    def __init__(self, adress='GPIB0::3::INSTR'):
        threading.Thread.__init__(self)
        self.adress = adress
        self.daemon = True
        self.start()

    def run(self):
        while True:
            dataframe_channels = lock_in(adress=self.adress).channels()
            with open(config_channels_filename, 'a') as f_object:
                try:
                    writer_object = writer(f_object)
                    writer_object.writerow(*dataframe_channels.values)
                    time.sleep(0.3)

                    # Close the file object
                    f_object.close()
                except:
                    f_object.close()


zero_time = time.process_time()


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

        lock_in_settings_button = tk.Button(
            self, text="Lock in settings", command=lambda: controller.show_frame(Lock_in_settings))
        lock_in_settings_button.place(relx=0.1, rely=0.1)

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
        
    


class Lock_in_settings(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text='Lock in settings', font=LARGE_FONT)
        label.place(relx=0.485, rely=0.02)

        label_time_constant = tk.Label(self, text='Time constant')
        label_time_constant.place(relx=0.02, rely=0.015)

        self.combo_time_constant = ttk.Combobox(self,
                                                value=lock_in().time_constant_options)
        self.combo_time_constant.current(8)
        self.combo_time_constant.bind(
            "<<ComboboxSelected>>", self.set_time_constant)
        self.combo_time_constant.place(relx=0.02, rely=0.05)

        self.value_time_constant = tk.StringVar(value='0.0')
        self.label_value_time_constant = tk.Label(
            self, text=(self.value_time_constant.get()))
        self.label_value_time_constant.place(relx=0.02, rely=0.085)

        label_low_pass_filter_slope = tk.Label(
            self, text='Low pass filter slope')
        label_low_pass_filter_slope.place(relx=0.02, rely=0.125)

        self.combo_low_pass_filter_slope = ttk.Combobox(self,
                                                        value=lock_in().low_pass_filter_slope_options)
        self.combo_low_pass_filter_slope.current(1)
        self.combo_low_pass_filter_slope.bind(
            "<<ComboboxSelected>>", self.set_low_pass_filter_slope)
        self.combo_low_pass_filter_slope.place(relx=0.02, rely=0.160)

        self.value_low_pass_filter_slope = tk.StringVar(value='0.0')
        self.label_value_low_pass_filter_slope = tk.Label(
            self, text=(self.value_low_pass_filter_slope.get()))
        self.label_value_low_pass_filter_slope.place(relx=0.02, rely=0.195)

        label_synchronous_filter_status = tk.Label(
            self, text='Synchronous filter status')
        label_synchronous_filter_status.place(relx=0.02, rely=0.235)

        self.combo_synchronous_filter_status = ttk.Combobox(self,
                                                            value=lock_in().synchronous_filter_status_options)
        self.combo_synchronous_filter_status.current(0)
        self.combo_synchronous_filter_status.bind(
            "<<ComboboxSelected>>", self.set_synchronous_filter_status)
        self.combo_synchronous_filter_status.place(relx=0.02, rely=0.270)

        self.value_synchronous_filter_status = tk.StringVar(value='0.0')
        self.label_value_synchronous_filter_status = tk.Label(
            self, text=(self.value_synchronous_filter_status.get()))
        self.label_value_synchronous_filter_status.place(relx=0.02, rely=0.305)

        label_aux_rule = tk.Label(
            self, text='AUX output voltage \n -10.5 < V < 10.5')
        label_aux_rule.place(relx=0.02, rely=0.4)

        label_aux1_voltage = tk.Label(self, text='AUX1 output')
        label_aux1_voltage.place(relx=0.02, rely=0.45)

        self.aux1_initial = tk.StringVar(value='0')

        entry_aux1_voltage = tk.Entry(self, textvariable=self.aux1_initial)
        entry_aux1_voltage.place(relx=0.02, rely=0.485)

        label_aux2_voltage = tk.Label(self, text='AUX2 output')
        label_aux2_voltage.place(relx=0.02, rely=0.515)

        self.aux2_initial = tk.StringVar(value='0')

        entry_aux2_voltage = tk.Entry(self, textvariable=self.aux2_initial)
        entry_aux2_voltage.place(relx=0.02, rely=0.550)

        label_aux3_voltage = tk.Label(self, text='AUX3 output')
        label_aux3_voltage.place(relx=0.02, rely=0.580)

        self.aux3_initial = tk.StringVar(value='0')

        entry_aux3_voltage = tk.Entry(self, textvariable=self.aux3_initial)
        entry_aux3_voltage.place(relx=0.02, rely=0.615)

        label_aux4_voltage = tk.Label(self, text='AUX4 output')
        label_aux4_voltage.place(relx=0.02, rely=0.645)

        self.aux4_initial = tk.StringVar(value='0')

        entry_aux4_voltage = tk.Entry(self, textvariable=self.aux4_initial)
        entry_aux4_voltage.place(relx=0.02, rely=0.680)

        button_aux_voltage = tk.Button(self, text='Set AUX voltage',
                                        command=self.aux_button_clicked)
        button_aux_voltage.place(relx=0.15, rely=0.675)

        label_sensitivity = tk.Label(self, text='Sensitivity')
        label_sensitivity.place(relx=0.15, rely=0.015)

        self.combo_sensitivity = ttk.Combobox(
            self, value=lock_in().sensitivity_options)
        self.combo_sensitivity.current(15)
        self.combo_sensitivity.bind(
            "<<ComboboxSelected>>", self.set_sensitivity)
        self.combo_sensitivity.place(relx=0.15, rely=0.05)

        self.value_sensitivity = tk.StringVar(value='0.0')
        self.label_value_sensitivity = tk.Label(
            self, text=(self.value_sensitivity.get()))
        self.label_value_sensitivity.place(relx=0.15, rely=0.085)

        label_remote = tk.Label(self, text='Display locking')
        label_remote.place(relx=0.15, rely=0.125)

        self.combo_remote = ttk.Combobox(
            self, value=lock_in().remote_status_options)
        self.combo_remote.current(1)
        self.combo_remote.bind("<<ComboboxSelected>>", self.set_remote)
        self.combo_remote.place(relx=0.15, rely=0.160)

        self.value_remote = tk.StringVar(value='0.0')
        self.label_value_remote = tk.Label(
            self, text=(self.value_remote.get()))
        self.label_value_remote.place(relx=0.15, rely=0.195)

        self.value_ch1 = tk.StringVar(value='0.0')
        self.label_value_ch1 = tk.Label(self, text=(
            '\n' + self.value_ch1.get()), font=('Arial', 16))
        self.label_value_ch1.place(relx=0.15, rely=0.3)

        self.combo_ch1 = ttk.Combobox(self, value=lock_in().modes_ch1_options)
        self.combo_ch1.current(0)
        self.combo_ch1.bind("<<ComboboxSelected>>", self.set_ch1_mode)
        self.combo_ch1.place(relx=0.15, rely=0.4)

        self.value_ch2 = tk.StringVar(value='0.0')
        self.label_value_ch2 = tk.Label(self, text=(
            '\n' + self.value_ch1.get()), font=('Arial', 16))
        self.label_value_ch2.place(relx=0.3, rely=0.3)

        self.combo_ch2 = ttk.Combobox(self, value=lock_in().modes_ch2_options)
        self.combo_ch2.current(0)
        self.combo_ch2.bind("<<ComboboxSelected>>", self.set_ch2_mode)
        self.combo_ch2.place(relx=0.3, rely=0.4)

        label_amplitude = tk.Label(
            self, text='Amplitude of SIN output, V. \n 0.004 < V < 5.000')
        label_amplitude.place(relx=0.485, rely=0.315)

        self.amplitude_initial = tk.StringVar(value='0.5')

        entry_amplitude = tk.Entry(self, textvariable=self.amplitude_initial)
        entry_amplitude.place(relx=0.5, rely=0.4)

        self.value_amplitude = tk.StringVar(value='0.0')
        self.label_value_amplitude = tk.Label(
            self, text=(self.value_amplitude.get()))
        self.label_value_amplitude.place(relx=0.5, rely=0.435)

        label_frequency = tk.Label(
            self, text='Frequency, Hz. \n 0.001 < Hz < 102000')
        label_frequency.place(relx=0.65, rely=0.315)

        self.frequency_initial = tk.StringVar(value='30.0')

        entry_frequency = tk.Entry(self, textvariable=self.frequency_initial)
        entry_frequency.place(relx=0.65, rely=0.4)

        self.value_frequency = tk.StringVar(value='0.0')
        self.label_value_frequency = tk.Label(
            self, text=(self.value_frequency.get()))
        self.label_value_frequency.place(relx=0.65, rely=0.435)

        label_phase = tk.Label(
            self, text='Phase shift, deg. \n -360.00 < deg < 729.99')
        label_phase.place(relx=0.8, rely=0.315)

        self.phase_initial = tk.StringVar(value='0.0')

        entry_phase = tk.Entry(self, textvariable=self.phase_initial)
        entry_phase.place(relx=0.8, rely=0.4)

        self.value_phase = tk.StringVar(value='0.0')
        self.label_value_phase = tk.Label(self, text=(self.value_phase.get()))
        self.label_value_phase.place(relx=0.8, rely=0.435)

        button_reference = tk.Button(self, text='Set reference parameters',
                                      command=self.reference_button_clicked)
        button_reference.place(relx=0.8, rely=0.485)

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
        button_listbox = tk.Button(self, text = "Collect data", command = select)
        button_listbox.place(relx = 0.615, rely = 0.665)
        '''
        thread_update_sensitivity = threading.Thread(
            target=self.update_sensitivity())
        thread_update_time_constant = threading.Thread(
            target=self.update_time_constant())
        thread_update_low_pass_filter_slope = threading.Thread(
            target=self.update_low_pass_filter_slope())
        thread_update_synchronous_filter_status = threading.Thread(
            target=self.update_synchronous_filter_status())
        thread_update_remote = threading.Thread(target=self.update_remote())
        thread_update_amplitude = threading.Thread(
            target=self.update_amplitude())
        thread_update_phase = threading.Thread(target=self.update_phase())
        thread_update_frequency = threading.Thread(
            target=self.update_frequency())
        thread_update_ch1 = threading.Thread(target=self.update_value_ch1())
        thread_update_ch2 = threading.Thread(target=self.update_value_ch2())

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

        button_back_home = tk.Button(self, text='Back to Home',
                                      command=lambda: controller.show_frame(StartPage))
        button_back_home.place(relx=0.85, rely=0.85)

    def set_sensitivity(self, event):
        lock_in().set_sensitivity(mode=int(self.combo_sensitivity.current()))

    def set_time_constant(self, event):
        lock_in().set_time_constant(mode=int(self.combo_time_constant.current()))

    def set_low_pass_filter_slope(self, event):
        lock_in().set_low_pass_filter_slope(
            mode=int(self.combo_low_pass_filter_slope.current()))

    def set_synchronous_filter_status(self, event):
        lock_in().set_synchronous_filter_status(
            mode=int(self.combo_synchronous_filter_status.current()))

    def set_ch1_mode(self, event):
        lock_in().set_ch1_mode(mode=int(self.combo_ch1.current()))

    def set_ch2_mode(self, event):
        lock_in().set_ch2_mode(mode=int(self.combo_ch2.current()))

    def set_remote(self, event):
        lock_in().set_remote(mode=int(self.combo_remote.current()))

    def aux_button_clicked(self):
        lock_in().set_AUX1_output(value=float(self.aux1_initial.get()))
        lock_in().set_AUX2_output(value=float(self.aux2_initial.get()))
        lock_in().set_AUX3_output(value=float(self.aux3_initial.get()))
        lock_in().set_AUX4_output(value=float(self.aux4_initial.get()))

    def reference_button_clicked(self):
        lock_in().set_frequency(value=float(self.frequency_initial.get()))
        lock_in().set_phase(value=float(self.phase_initial.get()))
        lock_in().set_amplitude(value=float(self.amplitude_initial.get()))

    def update_time_constant(self, interval=2987):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Time_constant'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_time_constant['text'] = str(
            lock_in().time_constant_options[int(value)])
        self.label_value_time_constant.after(
            interval, self.update_time_constant)

    def update_sensitivity(self, interval=2989):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Sensitivity'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_sensitivity['text'] = str(
            lock_in().sensitivity_options[int(value)])
        self.label_value_sensitivity.after(interval, self.update_sensitivity)

    def update_low_pass_filter_slope(self, interval=2991):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Low_pass_filter_slope'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_low_pass_filter_slope['text'] = str(
            lock_in().low_pass_filter_slope_options[int(value)])
        self.label_value_low_pass_filter_slope.after(
            interval, self.update_low_pass_filter_slope)

    def update_synchronous_filter_status(self, interval=2993):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Synchronous_filter_status'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_synchronous_filter_status['text'] = str(
            lock_in().synchronous_filter_status_options[int(value)])
        self.label_value_synchronous_filter_status.after(
            interval, self.update_synchronous_filter_status)

    def update_remote(self, interval=2995):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Remote'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_remote['text'] = str(
            lock_in().remote_status_options[int(value)])
        self.label_value_remote.after(interval, self.update_remote)

    def update_amplitude(self, interval=2997):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Amplitude'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_amplitude['text'] = str(value)
        self.label_value_amplitude.after(interval, self.update_amplitude)

    def update_phase(self, interval=2999):

        try:
            value = pd.read_csv(config_parameters_filename)['Phase'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_phase['text'] = str(value)
        self.label_value_phase.after(interval, self.update_phase)

    def update_frequency(self, interval=3001):

        try:
            value = pd.read_csv(config_parameters_filename)[
                'Frequency'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_frequency['text'] = str(value)
        self.label_value_frequency.after(interval, self.update_frequency)

    def update_value_ch1(self, interval=307):

        try:
            value = pd.read_csv(config_channels_filename)['Ch1'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_ch1['text'] = '\n' + str(value)
        self.label_value_ch1.after(interval, self.update_value_ch1)

    def update_value_ch2(self, interval=311):

        try:
            value = pd.read_csv(config_channels_filename)['Ch2'].values[-1]
        except IndexError:
            value = 0.0
        self.label_value_ch2['text'] = '\n' + str(value)
        self.label_value_ch2.after(interval, self.update_value_ch2)

class Sweeper1d(tk.Frame):

    def __init__(self, parent, controller):       

        tk.Frame.__init__(self, parent)

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
            self, value=['Time', *list_of_devices])
        self.combo_to_sweep1.current(0)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters)
        self.combo_to_sweep1.place(relx=0.15, rely=0.16)

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
        self.button_pause.place(relx = 0.3, rely = 0.25 +lstbox_height)
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.3375, rely = 0.25 + lstbox_height)
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.3, rely = 0.3 + lstbox_height)

        label_options = tk.Label(self, text = 'Options:', font = LARGE_FONT)
        label_options.place(relx = 0.05, rely = 0.2)
        

        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.2)

        label_min = tk.Label(self, text='From', font=LARGE_FONT)
        label_min.place(relx=0.12, rely=0.24)

        label_max = tk.Label(self, text='To', font=LARGE_FONT)
        label_max.place(relx=0.12, rely=0.28)

        label_step = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step.place(relx=0.12, rely=0.32)

        self.entry_min = tk.Entry(self)
        self.entry_min.place(relx=0.17, rely=0.24)

        self.entry_max = tk.Entry(self)
        self.entry_max.place(relx=0.17, rely=0.28)

        self.entry_ratio = tk.Entry(self)
        self.entry_ratio.place(relx=0.17, rely=0.32)

        label_delay_factor = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor.place(relx=0.12, rely=0.4)

        self.entry_delay_factor = tk.Entry(self)
        self.entry_delay_factor.place(relx=0.12, rely=0.46)

        # section of manual sweep points selection
        self.status_manual = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            self.filename = filename_sweep[:index_sweep] + \
                'manual' + filename_sweep[index_sweep + 5:]
        else:
            self.filename[:-4] + '_manual' + '.csv'
            
        # initials
        self.manual_sweep_flags = [0]
        self.manual_filenames = [self.filename]

        checkbox_manual = ttk.Checkbutton(self, text='Maunal sweep select',
                                          variable=self.status_manual, onvalue=1,
                                          offvalue=0, command=lambda: self.save_manual_status())
        checkbox_manual.place(relx=0.12, rely=0.52)

        button_new_manual = tk.Button(self, text = '🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0]))
        button_new_manual.place(relx=0.12, rely=0.56)

        button_explore_manual = tk.Button(
            self, text = '🔎', font = LARGE_FONT, command=lambda: self.explore_files())
        button_explore_manual.place(relx=0.15, rely=0.56)

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        button_start_sweeping = tk.Button(
            self, text="Start sweeping", command=lambda: self.start_sweeping())
        button_start_sweeping.place(relx=0.7, rely=0.7)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.7, rely=0.76)

    def update_sweep_parameters(self, event, interval=1000):
        if self.combo_to_sweep1.current() == 0:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)
            pass
        else:
            class_of_sweeper_device = types_of_devices[self.combo_to_sweep1.current(
            ) - 1]
            if class_of_sweeper_device != 'Not a class':
                self.sweep_options1['value'] = getattr(
                    globals()[class_of_sweeper_device](), 'set_options')
                self.sweep_options1.after(interval)

    def update_sweep_configurarion(self):
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        
        try:
            from_sweep1 = float(self.entry_min.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_max.get())
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
    
    def save_manual_status(self):
        if self.manual_sweep_flags[0] != self.status_manual.get():
            self.manual_sweep_flags[0] = self.status_manual.get()

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
        global fig221
        global fig222
        global fig223
        global animate221
        global animate222
        global animate223
        self.window_graph = Universal_frontend(classes=(Graph,), start=Graph)
        self.ani221 = animation.FuncAnimation(
            fig221, animate221, interval=interval)
        self.ani222 = animation.FuncAnimation(
            fig222, animate222, interval=interval)
        self.ani223 = animation.FuncAnimation(
            fig223, animate223, interval=interval)
        self.window_graph.mainloop()
        
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
        global columns
        global manual_filenames
        global manual_sweep_flags

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
        if self.combo_to_sweep1.current() == 0:
            columns = ['Time']
        else:
            device_to_sweep1 = list_of_devices[self.combo_to_sweep1.current()]
            parameters = getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep1)]](), 'set_options')
            parameter_to_sweep1 = parameters[self.sweep_options1.current()]
            columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1]
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_min.get() != '':
            from_sweep1 = self.entry_min.get()
        if self.entry_max.get() != '':
            to_sweep1 = self.entry_max.get()
        if self.entry_ratio.get() != '':
            ratio_sweep1 = self.entry_ratio.get()
        if from_sweep1 < to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = - ratio_sweep1
        if self.entry_delay_factor.get() != '':
            delay_factor1 = self.entry_delay_factor.get()
        if self.entry_filename.get() != '':
            filename_sweep = self.entry_filename.get()
        sweeper_flag1 = True
        sweeper_flag2 = False
        sweeper_flag3 = False
        manual_filenames = self.manual_filenames
        manual_sweep_flags = self.manual_sweep_flags

        Sweeper_write()


class Sweeper2d(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
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
        self.combo_to_sweep1.current(0)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx=0.15, rely=0.21)

        self.combo_to_sweep2 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep2.current(0)
        self.combo_to_sweep2.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx=0.3, rely=0.21)
        
        self.status_back_and_forth_slave = tk.IntVar(value = 0)
        
        back_and_forth_slave = False
    
        self.checkbox_back_and_forth_slave = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_slave, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_slave_status())
        self.checkbox_back_and_forth_slave.place(relx=0.38, rely=0.61)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.3935, rely = 0.6)
    
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
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.4875, rely = 0.25 + lstbox_height)
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.45, rely = 0.3 + lstbox_height)

        label_options = tk.Label(self, text = 'Options:', font=LARGE_FONT)
        label_options.place(relx = 0.05, rely = 0.25)

        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.25)

        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx=0.3, rely=0.25)

        label_min1 = tk.Label(self, text='From', font=LARGE_FONT)
        label_min1.place(relx=0.12, rely=0.29)

        label_max1 = tk.Label(self, text='To', font=LARGE_FONT)
        label_max1.place(relx=0.12, rely=0.33)

        label_step1 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step1.place(relx=0.12, rely=0.37)

        self.entry_min1 = tk.Entry(self)
        self.entry_min1.place(relx=0.17, rely=0.29)

        self.entry_max1 = tk.Entry(self)
        self.entry_max1.place(relx=0.17, rely=0.33)

        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.place(relx=0.17, rely=0.37)

        label_delay_factor1 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor1.place(relx=0.12, rely=0.45)

        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.place(relx=0.12, rely=0.51)

        label_min2 = tk.Label(self, text='From', font=LARGE_FONT)
        label_min2.place(relx=0.27, rely=0.29)

        label_max2 = tk.Label(self, text='To', font=LARGE_FONT)
        label_max2.place(relx=0.27, rely=0.33)

        label_step2 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step2.place(relx=0.27, rely=0.37)

        self.entry_min2 = tk.Entry(self)
        self.entry_min2.place(relx=0.32, rely=0.29)

        self.entry_max2 = tk.Entry(self)
        self.entry_max2.place(relx=0.32, rely=0.33)

        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.place(relx=0.32, rely=0.37)

        label_delay_factor2 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor2.place(relx=0.27, rely=0.45)

        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.place(relx=0.27, rely=0.51)

        # section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            self.filename = filename_sweep[:index_sweep] + \
                'manual' + filename_sweep[index_sweep + 5:]
        else:
            self.filename[:-4] + '_manual' + '.csv'

        # initials

        self.manual_sweep_flags = [0, 0]
        self.manual_filenames = [self.filename[:-4] +
                                 '1.csv', self.filename[:-4] + '2.csv']

        checkbox_manual1 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual1, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=1))
        checkbox_manual1.place(relx=0.12, rely=0.57)

        button_new_manual1 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0], i=1))
        button_new_manual1.place(relx=0.12, rely=0.6)

        button_explore_manual1 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=0))
        button_explore_manual1.place(relx=0.15, rely=0.6)

        checkbox_manual2 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual2, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=2))
        checkbox_manual2.place(relx=0.27, rely=0.57)

        button_new_manual2 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[1], i=0))
        button_new_manual2.place(relx=0.27, rely=0.6)

        button_explore_manual2 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=1))
        button_explore_manual2.place(relx=0.3, rely=0.6)
        
        label_condition = tk.Label(self, text = 'Constraints:', font = LARGE_FONT)
        label_condition.place(relx = 0.12, rely = 0.66)
        
        self.text_condition = tk.Text(self, width = 40, height = 7)
        self.text_condition.place(relx = 0.12, rely = 0.7)

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        button_start_sweeping = tk.Button(
            self, text="Start sweeping", command=lambda: self.start_sweeping())
        button_start_sweeping.place(relx=0.7, rely=0.7)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.7, rely=0.8)
        
    def update_master2_combo(self, event, interval = 1000):
        if self.combo_master1['value'][self.combo_master1.current()] == '':
            self.combo_master2['value'] = self.master_option
            self.combo_master2.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master':
            self.combo_master2['value'] = ['', 'Slave']
            self.combo_master2.after(interval)
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave':
            self.combo_master2['value'] = ['', 'Master']
            self.combo_master2.after(interval)
            
    def update_master1_combo(self, event, interval = 1000):
        if self.combo_master2['value'][self.combo_master1.current()] == '':
            self.combo_master1['value'] = self.master_option
            self.combo_master1.after(interval)
        if self.combo_master2['value'][self.combo_master1.current()] == 'Master':
            self.combo_master1['value'] = ['', 'Slave']
            self.combo_master1.after(interval)
        if self.combo_master2['value'][self.combo_master1.current()] == 'Slave':
            self.combo_master1['value'] = ['', 'Master']
            self.combo_master1.after(interval)

    def update_sweep_parameters1(self, event, interval=1000):
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current(
        )]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(
                globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)

    def update_sweep_parameters2(self, event, interval=1000):
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current(
        )]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(
                globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)

    def update_sweep_configurarion(self):
        global from_sweep1
        global to_sweep1
        global ratio_sweep1
        global delay_factor1
        global from_sweep2
        global to_sweep2
        global ratio_sweep2
        global delay_factor2
        
        try:
            from_sweep1 = float(self.entry_min1.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_max1.get())
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
            from_sweep2 = float(self.entry_min2.get())
        except ValueError:
            pass
        
        try:
            to_sweep2 = float(self.entry_max2.get())
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

    def save_manual_status(self, i):
        if self.manual_sweep_flags[i - 1] != getattr(self, 'status_manual' + str(i)).get():
            self.manual_sweep_flags[i -
                                    1] = getattr(self, 'status_manual' + str(i)).get()

    def save_back_and_forth_slave_status(self):
        global back_and_forth_slave
        
        if self.status_back_and_forth_slave == 0:
            back_and_forth_slave = False
        else:
            back_and_forth_slave = True
    
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
        global fig221
        global fig222
        global fig223
        global animate221
        global animate222
        global animate223
        self.window = Universal_frontend(classes=(Graph,), start=Graph)
        self.ani221 = animation.FuncAnimation(
            fig221, animate221, interval=interval)
        self.ani222 = animation.FuncAnimation(
            fig222, animate222, interval=interval)
        self.ani223 = animation.FuncAnimation(
            fig223, animate223, interval=interval)
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
        global condition
        global columns
        global manual_sweep_flags
        global manual_filenames
        global master_lock

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
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_maste2.current()] == 'Master':
            master_lock = True
            
            device_dub = device_to_sweep1
            device_to_sweep1 = device_to_sweep2
            device_to_sweep2 = device_dub
            
            parameter_dub = parameter_to_sweep1
            parameter_to_sweep1 = parameter_to_sweep2
            parameter_to_sweep2 = parameter_dub
        
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1,
                   device_to_sweep2 + '.' + parameter_to_sweep2]
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave':
            master_lock = True
            
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_min1.get() != '':
            from_sweep1 = self.entry_min1.get()
        if self.entry_max1.get() != '':
            to_sweep1 = self.entry_max1.get()
        if self.entry_ratio1.get() != '':
            ratio_sweep1 = self.entry_ratio1.get()
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
        if self.entry_delay_factor1.get() != '':
            delay_factor1 = self.entry_delay_factor1.get()
        if self.entry_min2.get() != '':
            from_sweep2 = self.entry_min2.get()
        if self.entry_max2.get() != '':
            to_sweep2 = self.entry_max2.get()
        if self.entry_ratio2.get() != '':
            ratio_sweep2 = self.entry_ratio2.get()
        if from_sweep2 > to_sweep1 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
        if self.entry_delay_factor2.get() != '':
            delay_factor2 = self.entry_delay_factor2.get()
        sweeper_flag1 = False
        sweeper_flag2 = True
        sweeper_flag3 = False
        condition = self.text_condition.get(1.0, tk.END)[:-1]
        manual_sweep_flags = self.manual_sweep_flags
        manual_filenames = self.manual_filenames

        Sweeper_write()


class Sweeper3d(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
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
        
        self.button_stop = tk.Button(self, text = '⏹️', font = LARGE_FONT, command = lambda: self.stop())
        self.button_stop.place(relx = 0.6335, rely = 0.25 + lstbox_height)
        
        self.button_tozero = tk.Button(self, text = 'To zero', width = 11, command = lambda: self.tozero())
        self.button_tozero.place(relx = 0.6, rely = 0.3 + lstbox_height)

        self.combo_to_sweep1 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep1.current(0)
        self.combo_to_sweep1.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters1)
        self.combo_to_sweep1.place(relx=0.15, rely=0.21)

        self.combo_to_sweep2 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep2.current(0)
        self.combo_to_sweep2.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters2)
        self.combo_to_sweep2.place(relx=0.3, rely=0.21)
        
        self.status_back_and_forth_master = tk.IntVar(value = 0)
    
        self.checkbox_back_and_forth_master = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_master, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_master_status())
        self.checkbox_back_and_forth_master.place(relx=0.35, rely=0.62)
        
        label_back_and_forth_master = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_master.place(relx = 0.3635, rely = 0.61)

        self.combo_to_sweep3 = ttk.Combobox(self, value=list_of_devices)
        self.combo_to_sweep3.current(0)
        self.combo_to_sweep3.bind(
            "<<ComboboxSelected>>", self.update_sweep_parameters3)
        self.combo_to_sweep3.place(relx=0.45, rely=0.21)
        
        self.status_back_and_forth_slave = tk.IntVar(value = 0)
    
        back_and_forth_slave = False
    
        self.checkbox_back_and_forth_slave = ttk.Checkbutton(self,
                                           variable=self.status_back_and_forth_slave, onvalue=1,
                                           offvalue=0, command=lambda: self.save_back_and_forth_slave_status())
        self.checkbox_back_and_forth_slave.place(relx=0.5, rely=0.62)
        
        label_back_and_forth_slave = tk.Label(self, text = '🔁', font = SUPER_LARGE)
        label_back_and_forth_slave.place(relx = 0.5135, rely = 0.61)

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

        self.sweep_options1 = ttk.Combobox(self)
        self.sweep_options1.place(relx=0.15, rely=0.25)

        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx=0.3, rely=0.25)

        self.sweep_options2 = ttk.Combobox(self)
        self.sweep_options2.place(relx=0.45, rely=0.25)

        label_min1 = tk.Label(self, text='From', font=LARGE_FONT)
        label_min1.place(relx=0.12, rely=0.29)

        label_max1 = tk.Label(self, text='To', font=LARGE_FONT)
        label_max1.place(relx=0.12, rely=0.33)

        label_step1 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step1.place(relx=0.12, rely=0.37)

        self.entry_min1 = tk.Entry(self)
        self.entry_min1.place(relx=0.17, rely=0.29)

        self.entry_max1 = tk.Entry(self)
        self.entry_max1.place(relx=0.17, rely=0.33)

        self.entry_ratio1 = tk.Entry(self)
        self.entry_ratio1.place(relx=0.17, rely=0.37)

        label_delay_factor1 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor1.place(relx=0.12, rely=0.45)

        self.entry_delay_factor1 = tk.Entry(self)
        self.entry_delay_factor1.place(relx=0.12, rely=0.51)

        label_min2 = tk.Label(self, text='From', font=LARGE_FONT)
        label_min2.place(relx=0.27, rely=0.29)

        label_max2 = tk.Label(self, text='To', font=LARGE_FONT)
        label_max2.place(relx=0.27, rely=0.33)

        label_step2 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step2.place(relx=0.27, rely=0.37)

        self.entry_min2 = tk.Entry(self)
        self.entry_min2.place(relx=0.32, rely=0.29)

        self.entry_max2 = tk.Entry(self)
        self.entry_max2.place(relx=0.32, rely=0.33)

        self.entry_ratio2 = tk.Entry(self)
        self.entry_ratio2.place(relx=0.32, rely=0.37)

        label_delay_factor2 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor2.place(relx=0.27, rely=0.45)

        self.entry_delay_factor2 = tk.Entry(self)
        self.entry_delay_factor2.place(relx=0.27, rely=0.51)

        label_min3 = tk.Label(self, text='From', font=LARGE_FONT)
        label_min3.place(relx=0.42, rely=0.29)

        label_max3 = tk.Label(self, text='To', font=LARGE_FONT)
        label_max3.place(relx=0.42, rely=0.33)

        label_step3 = tk.Label(self, text='Ratio, \n Δ/s', font=LARGE_FONT)
        label_step3.place(relx=0.42, rely=0.37)

        self.entry_min3 = tk.Entry(self)
        self.entry_min3.place(relx=0.47, rely=0.29)

        self.entry_max3 = tk.Entry(self)
        self.entry_max3.place(relx=0.47, rely=0.33)

        self.entry_ratio3 = tk.Entry(self)
        self.entry_ratio3.place(relx=0.47, rely=0.37)

        label_delay_factor3 = tk.Label(
            self, text='Delay factor, s', justify=tk.LEFT, font=LARGE_FONT)
        label_delay_factor3.place(relx=0.42, rely=0.45)

        self.entry_delay_factor3 = tk.Entry(self)
        self.entry_delay_factor3.place(relx=0.42, rely=0.51)

        # section of manual sweep points selection
        self.status_manual1 = tk.IntVar()
        self.status_manual2 = tk.IntVar()
        self.status_manual3 = tk.IntVar()
        index_sweep = filename_sweep.find('sweep')
        if index_sweep != -1:
            self.filename = filename_sweep[:index_sweep] + \
                'manual' + filename_sweep[index_sweep + 5:]
        else:
            self.filename[:-4] + '_manual' + '.csv'

        # initials
        self.manual_sweep_flags = [0, 0, 0]
        self.manual_filenames = [self.filename[:-4] + '1.csv',
                                 self.filename[:-4] + '1.csv', self.filename[:-4] + '1.csv']

        checkbox_manual1 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual1, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=1))
        checkbox_manual1.place(relx=0.12, rely=0.57)

        button_new_manual1 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[0], i=0))
        button_new_manual1.place(relx=0.12, rely=0.61)

        button_explore_manual1 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=0))
        button_explore_manual1.place(relx=0.15, rely=0.61)

        checkbox_manual2 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual2, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=2))
        checkbox_manual2.place(relx=0.27, rely=0.57)

        button_new_manual2 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[1], i=1))
        button_new_manual2.place(relx=0.27, rely=0.61)

        button_explore_manual2 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=1))
        button_explore_manual2.place(relx=0.3, rely=0.61)

        checkbox_manual3 = ttk.Checkbutton(self, text='Maunal sweep select',
                                           variable=self.status_manual3, onvalue=1,
                                           offvalue=0, command=lambda: self.save_manual_status(i=3))
        checkbox_manual3.place(relx=0.42, rely=0.57)

        button_new_manual3 = tk.Button(self, text='🖊', font = LARGE_FONT, command=lambda: self.open_blank(
            filename=self.manual_filenames[2], i=2))
        button_new_manual3.place(relx=0.42, rely=0.61)

        button_explore_manual3 = tk.Button(
            self, text='🔎', font = LARGE_FONT, command=lambda: self.explore_files(i=2))
        button_explore_manual3.place(relx=0.45, rely=0.61)
        
        label_condition = tk.Label(self, text = 'Constraints:', font = LARGE_FONT)
        label_condition.place(relx = 0.12, rely = 0.66)
        
        self.text_condition = tk.Text(self, width = 60, height = 7)
        self.text_condition.place(relx = 0.12, rely = 0.7)

        self.filename_textvariable = tk.StringVar(self, value = filename_sweep)
        width = int(len(self.filename_textvariable.get()) * 0.95)
        self.entry_filename = tk.Entry(self, textvariable = self.filename_textvariable, font = LARGE_FONT, 
                                       width = width)
        self.entry_filename.place(relx = 0.97 - width / 100, rely = 0.9)

        button_settings = tk.Button(self, text = '⚙️', font = SUPER_LARGE, command = lambda: self.open_settings())
        button_settings.place(relx = 0.85, rely = 0.15)

        button_filename = tk.Button(
            self, text = 'Browse...', command=lambda: self.set_filename_sweep())
        button_filename.place(relx=0.85, rely=0.9)

        button_start_sweeping = tk.Button(
            self, text="Start sweeping", command=lambda: self.start_sweeping())
        button_start_sweeping.place(relx=0.75, rely=0.7)

        graph_button = tk.Button(
            self, text='📊', font = SUPER_LARGE, command=lambda: self.open_graph())
        graph_button.place(relx=0.75, rely=0.8)

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

    def update_sweep_parameters1(self, event, interval=1000):
        class_of_sweeper_device1 = types_of_devices[self.combo_to_sweep1.current(
        )]
        if class_of_sweeper_device1 != 'Not a class':
            self.sweep_options1['value'] = getattr(
                globals()[class_of_sweeper_device1](), 'set_options')
            self.sweep_options1.after(interval)
        else:
            self.sweep_options1['value'] = ['']
            self.sweep_options1.current(0)
            self.sweep_options1.after(interval)

    def update_sweep_parameters2(self, event, interval=1000):
        class_of_sweeper_device2 = types_of_devices[self.combo_to_sweep2.current(
        )]
        if class_of_sweeper_device2 != 'Not a class':
            self.sweep_options2['value'] = getattr(
                globals()[class_of_sweeper_device2](), 'set_options')
            self.sweep_options2.after(interval)
        else:
            self.sweep_options2['value'] = ['']
            self.sweep_options2.current(0)
            self.sweep_options2.after(interval)

    def update_sweep_parameters3(self, event, interval=1000):
        class_of_sweeper_device3 = types_of_devices[self.combo_to_sweep3.current(
        )]
        if class_of_sweeper_device3 != 'Not a class':
            self.sweep_options3['value'] = getattr(
                globals()[class_of_sweeper_device3](), 'set_options')
            self.sweep_options3.after(interval)
        else:
            self.sweep_options3['value'] = ['']
            self.sweep_options3.current(0)
            self.sweep_options3.after(interval)
            
    def update_sweep_configurarion(self):
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
            from_sweep1 = float(self.entry_min1.get())
        except ValueError:
            pass
        
        try:
            to_sweep1 = float(self.entry_max1.get())
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
            from_sweep2 = float(self.entry_min2.get())
        except ValueError:
            pass
        
        try:
            to_sweep2 = float(self.entry_max2.get())
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
            from_sweep3 = float(self.entry_min3.get())
        except ValueError:
            pass
        
        try:
            to_sweep3 = float(self.entry_max3.get())
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

    def save_manual_status(self, i):
        if self.manual_sweep_flags[i - 1] != getattr(self, 'status_manual' + str(i)).get():
            self.manual_sweep_flags[i -
                                    1] = getattr(self, 'status_manual' + str(i)).get()

    def save_back_and_forth_master_status(self):
        global back_and_forth_master
        
        if self.status_back_and_forth_master == 0:
            back_and_forth_master = False
        else:
            back_and_forth_master = True
            
    def save_back_and_forth_slave_status(self):
        global back_and_forth_slave
        
        if self.status_back_and_forth_slave == 0:
            back_and_forth_slave = False
        else:
            back_and_forth_slave = True
    
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
        global fig221
        global fig222
        global fig223
        global animate221
        global animate222
        global animate223
        self.window = Universal_frontend(classes=(Graph,), start=Graph)
        self.ani221 = animation.FuncAnimation(
            fig221, animate221, interval=interval)
        self.ani222 = animation.FuncAnimation(
            fig222, animate222, interval=interval)
        self.ani223 = animation.FuncAnimation(
            fig223, animate223, interval=interval)
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
        global condition
        global columns
        global manual_filenames
        global manual_sweep_flags
        global master_lock
        
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
            
            device_dub = device_to_sweep1
            device_to_sweep1 = device_to_sweep3
            device_to_sweep3 = device_dub
            
            parameter_dub = parameter_to_sweep1
            parameter_to_sweep1 = parameter_to_sweep3
            parameter_to_sweep3 = parameter_dub

        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave-slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Master' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave':
            master_lock = True
            
            device_dub1 = device_to_sweep1
            device_dub2 = device_to_sweep2
            device_to_sweep1 = device_to_sweep3
            device_to_sweep2 = device_dub1
            device_to_sweep3 = device_dub2
            
            parameter_dub1 = parameter_to_sweep1
            parameter_dub2 = parameter_to_sweep2
            parameter_to_sweep1 = parameter_to_sweep3
            parameter_to_sweep2 = parameter_dub1
            parameter_to_sweep3 = parameter_dub2
        
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Master' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave-slave':
            master_lock = True
            
            device_dub = device_to_sweep1
            device_to_sweep1 = device_to_sweep2
            device_to_sweep2 = device_dub

            
            parameter_dub = parameter_to_sweep1
            parameter_to_sweep1 = parameter_to_sweep2
            parameter_to_sweep2 = parameter_dub
            
        if self.combo_master1['value'][self.combo_master1.current()] == 'Slave' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave-slave' and self.combo_master3['value'][self.combo_master3.current()] == 'Master':
            master_lock = True
            
            device_dub1 = device_to_sweep1
            device_dub2 = device_to_sweep2
            device_to_sweep1 = device_dub2
            device_to_sweep2 = device_to_sweep3
            device_to_sweep3 = device_dub1
            
            parameter_dub1 = parameter_to_sweep1
            parameter_dub2 = parameter_to_sweep2
            parameter_to_sweep1 = parameter_dub2
            parameter_to_sweep2 = parameter_to_sweep3
            parameter_to_sweep3 = parameter_dub1
            
        if self.combo_master1['value'][self.combo_master1.current()] == 'Master' and self.combo_master2['value'][self.combo_master2.current()] == 'Slave-slave' and self.combo_master3['value'][self.combo_master3.current()] == 'Slave':
            master_lock = True
            
            device_dub = device_to_sweep2
            device_to_sweep2 = device_to_sweep3
            device_to_sweep3 = device_dub

            
            parameter_dub = parameter_to_sweep2
            parameter_to_sweep1 = parameter_to_sweep3
            parameter_to_sweep3 = parameter_dub
        
        columns = ['Time', device_to_sweep1 + '.' + parameter_to_sweep1,
                   device_to_sweep2 + '.' + parameter_to_sweep2,
                   device_to_sweep3 + '.' + parameter_to_sweep3]
        for option in parameters_to_read:
            columns.append(option)

        # fixing sweeper parmeters
        if self.entry_min1.get() != '':
            from_sweep1 = self.entry_min1.get()
        if self.entry_max1.get() != '':
            to_sweep1 = self.entry_max1.get()
        if self.entry_ratio1.get() != '':
            ratio_sweep1 = self.entry_ratio1.get()
        if from_sweep1 > to_sweep1 and ratio_sweep1 > 0:
            ratio_sweep1 = -ratio_sweep1
        if self.entry_delay_factor1.get() != '':
            delay_factor1 = self.entry_delay_factor1.get()
        if self.entry_min2.get() != '':
            from_sweep2 = self.entry_min2.get()
        if self.entry_max2.get() != '':
            to_sweep2 = self.entry_max2.get()
        if self.entry_ratio2.get() != '':
            ratio_sweep2 = self.entry_ratio2.get()
        if from_sweep2 > to_sweep2 and ratio_sweep2 > 0:
            ratio_sweep2 = -ratio_sweep2
        if self.entry_delay_factor2.get() != '':
            delay_factor2 = self.entry_delay_factor2.get()
        if self.entry_min3.get() != '':
            from_sweep3 = self.entry_min3.get()
        if self.entry_max3.get() != '':
            to_sweep3 = self.entry_max3.get()
        if self.entry_ratio3.get() != '':
            ratio_sweep3 = self.entry_ratio3.get()
        if from_sweep3 > to_sweep3 and ratio_sweep3 > 0:
            ratio_sweep3 = -ratio_sweep3
        if self.entry_delay_factor3.get() != '':
            delay_factor3 = self.entry_delay_factor3.get()
        sweeper_flag1 = False
        sweeper_flag2 = False
        sweeper_flag3 = True
        condition = self.text_condition.get(1.0, tk.END)[:-1]
        manual_filenames = self.manual_filenames
        manual_sweep_flags = self.manual_sweep_flags

        Sweeper_write()

class Settings(tk.Frame):
    
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        
        parent = globals()['Sweeper_object']
        
        label_adress = tk.Label(self, text = 'Set device type:')
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
        
        label_names = tk.Label(self, text = 'Change names:')
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
        
        self.entry_new_device = tk.Entry(self, width = 30)
        self.entry_new_device.place(relx = 0.2, rely = 0.2)
        
        self.entry_new_set_parameter = tk.Entry(self, width = 30)
        self.entry_new_set_parameter.place(relx = 0.2, rely = 0.25)
        
        self.entry_new_get_parameter = tk.Entry(self, width = 30)
        self.entry_new_get_parameter.place(relx = 0.2, rely = 0.3)
        
        button_change_name_device = tk.Button(self, text = 'Change device name', command = lambda: self.update_names_devices(parent))
        button_change_name_device.place(relx = 0.35, rely = 0.19)
        
        button_change_name_set_parameters = tk.Button(self, text = 'Change set name', command = lambda: self.update_names_set_parameters(parent))
        button_change_name_set_parameters.place(relx = 0.35, rely = 0.24)
        
        button_change_name_get_parameters = tk.Button(self, text = 'Change get name', command = lambda: self.update_names_get_parameters(parent))
        button_change_name_get_parameters.place(relx = 0.35, rely = 0.29)
        
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
        new_device_name = self.entry_new_device.get()
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
        new_set_parameter_name = self.entry_new_set_parameter.get()
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
        new_get_parameter_name = self.entry_new_get_parameter.get()
        new_get_parameters_values = list(self.combo_get_parameters['values'])
        new_get_parameters_values[self.combo_get_parameters.current()] = new_get_parameter_name
        
        parent.dict_lstbox[self.combo_get_parameters['values'][self.combo_get_parameters.current()]] = new_get_parameter_name
        
        self.combo_get_parameters['values'] = new_get_parameters_values
        
        parent.devices.set(value=new_get_parameters_values)
        parent.lstbox_to_read.after(interval)
        
            

class Sweeper_write(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        self.device_to_sweep1 = device_to_sweep1
        self.device_to_sweep2 = device_to_sweep2
        self.device_to_sweep3 = device_to_sweep3
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.parameter_to_sweep3 = parameter_to_sweep3
        self.from_sweep1 = float(from_sweep1)
        self.to_sweep1 = float(to_sweep1)
        self.ratio_sweep1 = float(ratio_sweep1)
        self.delay_factor1 = float(delay_factor1)
        self.from_sweep2 = float(from_sweep2)
        self.to_sweep2 = float(to_sweep2)
        self.ratio_sweep2 = float(ratio_sweep2)
        self.delay_factor2 = float(delay_factor2)
        self.from_sweep3 = float(from_sweep3)
        self.to_sweep3 = float(to_sweep3)
        self.ratio_sweep3 = float(ratio_sweep3)
        self.delay_factor3 = float(delay_factor3)
        self.parameters_to_read = parameters_to_read
        self.filename_sweep = filename_sweep
        self.value1 = float(from_sweep1)
        self.value2 = float(from_sweep2)
        self.value3 = float(from_sweep3)
        self.columns = columns
        self.sweeper_flag1 = sweeper_flag1
        self.sweeper_flag2 = sweeper_flag2
        self.sweeper_flag3 = sweeper_flag3
        self.condition = condition
        self.step1 = float(delay_factor1) * float(ratio_sweep1)
        self.step2 = float(delay_factor2) * float(ratio_sweep2)
        self.step3 = float(delay_factor3) * float(ratio_sweep3)
        self.time1 = (float(from_sweep1) - float(to_sweep1)) / float(ratio_sweep1)
        self.time2 = (float(from_sweep2) - float(to_sweep2)) / float(ratio_sweep2)
        self.time3 = (float(from_sweep3) - float(to_sweep3)) / float(ratio_sweep3)
        
        try:
            self.nstep1 = (float(to_sweep1) - float(from_sweep1)) / self.ratio_sweep1 / self.delay_factor1
            self.nstep1 = int(self.nstep1)
        except ValueError:
            self.nstep1 = 1
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
        #input: tup - tuple, contains coordinates of phase space of sweep parameters,
        #dtup: tuple of steps along sweep axis
        #condition_str - python-like condition, written by user in a form of string
        #sweep_dimension - 2 or 3: how many sweep parameters are there
        #############
        #return 1 if point in fase space with coordinates in tup included in condition
        #np.nan if not included
        
        def isequal(a, b, abs_tol):
            #equality with tolerance
            return abs(a-b) <= abs_tol

        def notequal(a, b, abs_tol):
            #not equality with tolerance
            return abs(a-b) > abs_tol

        def ismore(a, b, abs_tol):
            #if one lement is more than other with tolerance
            return (a-b) > 0

        def ismoreequal(a, b, abs_tol):
            #if one lement is more or equal than other with tolerance
            return (a-b) >= abs_tol

        def isless(a, b, abs_tol):
            #if one lement is less than other with tolerance
            return (a-b) < 0

        def islessequal(a, b, abs_tol):
            #if one lement is less or equal than other with tolerance
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
                print('else')
                return 1
        return result

    def transposition(self, a, b):
        
        global manual_sweep_flags
        # changes device_a and device_b order
        if 1 in manual_sweep_flags:
            pass
        else:
            print('Transposition happened')
            a = str(a)
            b = str(b)
            setattr(self, 'device_to_sweep' + a, globals()['device_to_sweep' + b])
            setattr(self, 'device_to_sweep' + b, globals()['device_to_sweep' + a])
            setattr(self, 'parameter_to_sweep' + a, globals()['parameter_to_sweep' + b])
            setattr(self, 'parameter_to_sweep' + b, globals()['parameter_to_sweep' + a])
            setattr(self, 'from_sweep' + a, float(globals()['from_sweep' + b]))
            setattr(self, 'to_sweep' + a, float(globals()['to_sweep' + b]))
            setattr(self, 'ratio_sweep' + a, float(globals()['ratio_sweep' + b]))
            setattr(self, 'delay_factor' + a, float(globals()['delay_factor' + b]))
            setattr(self, 'from_sweep' + b, float(globals()['from_sweep' + a]))
            setattr(self, 'to_sweep' + b, float(globals()['to_sweep' + a]))
            setattr(self, 'ratio_sweep' + b, float(globals()['ratio_sweep' + a]))
            setattr(self, 'delay_factor' + b, float(globals()['delay_factor' + a]))
            setattr(self, 'step' + a, float(globals()['delay_factor' + b]) * float(globals()['ratio_sweep' + b]))
            setattr(self, 'step' + b, float(globals()['delay_factor' + a]) * float(globals()['ratio_sweep' + a]))
            setattr(self, 'value' + a, float(globals()['from_sweep' + b]))
            setattr(self, 'value' + b, float(globals()['from_sweep' + a]))
            setattr(self, 'time' + a, (float(globals()['from_sweep' + b]) - float(globals()['to_sweep' + b])) / float(globals()['ratio_sweep' + b]))
            setattr(self, 'time' + b, (float(globals()['from_sweep' + a]) - float(globals()['to_sweep' + a])) / float(globals()['ratio_sweep' + a]))

    def isinarea(self, point, grid_area, dgrid_area, sweep_dimension = 2):
        #if point is in grid_area return True. grid size defined by dgrid_area which is tuple
        
        if grid_area == True:
            return True
        else:
            def includance(point, reference, dgrid_area, sweep_dimension = 2):
                #equity with tolerance
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
        
        def append_read_parameters():
            #appends dataframe with parameters to read
            
            global dataframe
            
            for parameter in self.parameters_to_read:
                index_dot = parameter.find('.')
                adress = parameter[:index_dot]
                option = parameter[index_dot + 1:]
                dataframe.append(getattr(globals()[
                                 types_of_devices[list_of_devices.index(str(adress))]](adress=adress), option)())
        
        def tofile():
            #appends file with new row - dataframe
            
            global dataframe
            global filename_sweep
            
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
            
            axis = str(axis)
            result = getattr(self, 'value' + axis) < float(globals()['to_sweep' + axis])
            
            if stop_flag == True:
                return False
            
            if float(globals()['ratio_sweep' + axis]) > 0:
                return result
            else:
                return not result
        
        def step(axis = 1, value = None):
            
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
            
            #performs a step along sweep axis
            
            global zero_time
            global dataframe
            global manual_sweep_flags
            global stop_flag
            global pause_flag
            global tozero_flag
            
            if len(dataframe) == 0:
                dataframe = [time.process_time() - zero_time]
            else:
                dataframe[0] = [time.process_time() - zero_time][0]
                
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
                        setattr(self, 'value' + str(axis), getattr(self, 'value' + str(axis)) + getattr(self, 'step' + str(axis)))
                    else:
                        getattr(globals()[types_of_devices[list_of_devices.index(device_to_sweep)]](
                            adress=device_to_sweep), 'set_' + str(parameter_to_sweep))(value=value)
                        dataframe.append(value)
                    
                    delay_factor = getattr(self, 'delay_factor' + str(axis))
                    time.sleep(delay_factor)
                    ###################
                    return 
                else:
                    try_tozero()
                    
                    stop_flag = True
                    
            else:
                time.sleep(1)
                print('pause')
                step(axis, value)
        
        def update_filename(i):
            global filename_sweep
            self.filename_sweep = self.filename_sweep[:-(5 + len(str(i)))] + str(-i) + '.csv'
            filename_sweep = self.filename_sweep
            return
        
        def back_and_forth_transposition(axis):
            axis = str(axis)
            dub = getattr(self, 'to_sweep' + axis)
            setattr(self, 'to_sweep' + axis, getattr(self, 'from_sweep' + axis))
            setattr(self, 'from_sweep' + axis, dub)
            globals()['ratio_sweep' + axis] = - float(globals()['ratio_sweep' + axis])
            
        def determine_step(i, data, axis):
            axis = str(axis)
            try:
                setattr(self, 'step' + axis, abs(data[i+1] - data[i-1]) / 4)
            except IndexError:
                try:
                    setattr(self, 'step' + axis, abs(data[i] - data[i-1]) / 2)
                except IndexError:
                    setattr(self, 'step' + axis, abs(data[i] - data[i+1]) / 2)
        
        if self.sweeper_flag1 == True:
            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
            
            while condition(1) and manual_sweep_flags == [0]:
                if self.device_to_sweep1 == 'Time':
                    globals()['dataframe'] = [time.process_time() - zero_time]
                else:
                    step(1)
                append_read_parameters()
                tofile()

            if self.sweeper_flag1 == True and manual_sweep_flags == [1]:
                data = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for value in data:
                    step(1, value = value)
                    append_read_parameters()
                    tofile()

                self.sweeper_flag1 = False

        if self.sweeper_flag2 == True:

            if self.time1 > self.time2 and master_lock == False:
                self.transposition(1, 2)
                manual_sweep_flags = manual_sweep_flags[::-1]
                manual_filenames = manual_filenames[::-1]
                columns[1:3] = columns[1:3][:-1]
                
            i = 1
            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
            self.filename_sweep = self.filename_sweep[:-4] + str(-i) + '.csv'
            filename_sweep = self.filename_sweep
            globals()['dataframe'].to_csv(self.filename_sweep, index=False)

            while condition(1) and manual_sweep_flags == [0, 0]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                while condition(2) and manual_sweep_flags == [0, 0]:
                    if self.isinarea(point = [self.value1, self.value2], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                        globals()['dataframe'] = [*dataframe_after]
                        step(2)
                        append_read_parameters()
                        tofile()
                    else:
                        self.value2 += self.step2
                    
                if back_and_forth_slave == True:
                    back_and_forth_transposition(2)
                    while condition(2) and manual_sweep_flags == [0, 0]:
                        if self.isinarea(point = [self.value1, self.value2], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                            globals()['dataframe'] = [*dataframe_after]
                            step(2)
                            append_read_parameters()
                            tofile()
                        else:
                            self.value2 += self.step2
                    back_and_forth_transposition(2)
                    
                self.value2 = self.from_sweep2
                i += 1
                globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                update_filename(i)
                globals()['dataframe'].to_csv(self.filename_sweep, index=False)

            if manual_sweep_flags == [1, 0]:
                data = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for i, value in enumerate(data):
                    if manual_sweep_flags == [1, 0]:
                        determine_step(i, data, 1)
                        step(1, value = value)
                        dataframe_after = [*globals()['dataframe']]
                        while condition(2) and manual_sweep_flags == [1, 0]:
                            if self.isinarea(point = [value, self.value2], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                                globals()['dataframe'] = [*dataframe_after]
                                step(2)
                                append_read_parameters()
                                tofile()
                            else:
                                self.value2 += self.step2
                            
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(2)
                            while condition(2) and manual_sweep_flags == [1, 0]:
                                if self.isinarea(point = [value, self.value2], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                                    globals()['dataframe'] = [*dataframe_after]
                                    step(2)
                                    append_read_parameters()
                                    tofile()
                                else:
                                    self.value2 += self.step2
                            back_and_forth_transposition(2)
                            
                        self.value2 = self.from_sweep2
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    else:
                        break

            while condition(1) and manual_sweep_flags == [0, 1]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                data = pd.read_csv(manual_filenames[1]).values.reshape(-1)
                for i, value in enumerate(data):
                    if manual_sweep_flags == [0, 1]:
                        determine_step(i, data, 2)
                        if self.isinarea(point = [self.value1, value], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                            globals()['dataframe'] = [*dataframe_after]
                            step(2, value = value)
                            append_read_parameters()
                            tofile()  
                    else:
                        break
                    
                if back_and_forth_slave == True:
                    back_and_forth_transposition(2)
                    for i, value in enumerate(data[::-1]):
                        determine_step(i, data, 2)
                        if manual_sweep_flags == [0, 1]:
                            if self.isinarea(point = [self.value1, value], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                                globals()['dataframe'] = [*dataframe_after]
                                step(2, value = value)
                                append_read_parameters()
                                tofile() 
                        else:
                            break
                i += 1
                globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                update_filename(i)
                globals()['dataframe'].to_csv(self.filename_sweep, index=False)

            if manual_sweep_flags == [1, 1]:
                print([1, 1], ' = ', manual_sweep_flags)
                data1 = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                data2 = pd.read_csv(manual_filenames[1]).values.reshape(-1)
                for i1, value1 in enumerate(data1):
                    determine_step(i1, data1, 1)
                    step(1, value = value1)
                    dataframe_after = [*globals()['dataframe']]
                    for i2, value2 in enumerate(data2):
                        if self.isinarea(point = [self.value1, value], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                            globals()['dataframe'] = [*dataframe_after]
                            determine_step(i2, data2, 2)
                            step(2, value = value2)
                            append_read_parameters()
                            tofile()
                    if back_and_forth_slave == True:
                        back_and_forth_transposition(2)
                        for i2, value2 in enumerate(data2[::-1]):
                            if self.isinarea(point = [self.value1, value], grid_area = self.grid_space, dgrid_area = [self.step1 / 2, self.step2 / 2]):
                                globals()['dataframe'] = [*dataframe_after]
                                determine_step(i2, data2, 2)
                                step(2, value = value2)
                                append_read_parameters()
                                tofile()
                                
                    i += 1
                    globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                    update_filename(i)
                    globals()['dataframe'].to_csv(self.filename_sweep, index=False)

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

            i = 1
            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
            self.filename_sweep = self.filename_sweep[:-4] + str(i) + '.csv'
            globals()['dataframe'].to_csv(self.filename_sweep, index=False)

            while condition(1) and manual_sweep_flags == [0, 0, 0]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                while condition(2) and manual_sweep_flags == [0, 0, 0]:
                    globals()['dataframe'] = [*dataframe_after]
                    step(2)
                    dataframe_after_after = [*globals()['dataframe']]
                    while condition(3) and manual_sweep_flags == [0, 0, 0]:
                        if self.isinarea(point = (self.value1, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                            globals()['dataframe'] = [*dataframe_after_after]
                            step(3)
                            append_read_parameters()
                            tofile()
                        else:
                            self.value3 += self.step3
                    if back_and_forth_slave == True:
                        back_and_forth_transposition(3)
                        while condition(3) and manual_sweep_flags == [0, 0, 0]:
                            if self.isinarea(point = (self.value1, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                globals()['dataframe'] = [*dataframe_after_after]
                                step(3)
                                append_read_parameters()
                                tofile()
                            else:
                                self.value3 += self.step3
                        back_and_forth_transposition(3)                    
                    self.value3 = self.from_sweep3
                    i += 1
                    globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                    update_filename(i)
                    globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    
                if back_and_forth_master == True:
                    back_and_forth_transposition(2)
                    while condition(2) and manual_sweep_flags == [0, 0, 0]:
                        globals()['dataframe'] = [*dataframe_after]
                        step(2)
                        dataframe_after_after = [*globals()['dataframe']]
                        while condition(3) and manual_sweep_flags == [0, 0, 0]:
                            if self.isinarea(point = (self.value1, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                globals()['dataframe'] = [*dataframe_after_after]
                                step(3)
                                append_read_parameters()
                                tofile()
                            else:
                                self.value3 += self.step3
                                
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(3)
                            while condition(3) and manual_sweep_flags == [0, 0, 0]:
                                if self.isinarea(point = (self.value1, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    step(3)
                                    append_read_parameters()
                                    tofile()
                                else:
                                    self.value3 += self.step3
                            back_and_forth_transposition(3)                    
                        self.value3 = self.from_sweep3
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        back_and_forth_transposition(3)
                    
                self.value2 = self.from_sweep3
            self.sweeper_flag3 == False

            if manual_sweep_flags == [1, 0, 0]:
                data = pd.read_csv(manual_filenames[0]).values.reshape[-1]
                for i, value in enumerate(data):
                    if manual_sweep_flags == [1, 0, 0]:
                        determine_step(i, data, 1)
                        step(1, value = value)
                        dataframe_after = [*globals()['dataframe']]
                        while condition(2) and manual_sweep_flags == [1, 0, 0]:
                            globals()['dataframe'] = [*dataframe_after]
                            step(2)
                            dataframe_after_after = [*globals()['dataframe']]
                            while condition(3) and manual_sweep_flags == [1, 0, 0]:
                                if self.isinarea(point = (value, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    step(3)
                                    append_read_parameters()
                                    tofile()
                                else:
                                    self.value3 += self.step3
                            
                            if back_and_forth_slave == True:
                                back_and_forth_transposition(3)
                                while condition(3) and manual_sweep_flags == [1, 0, 0]:
                                    if self.isinarea(point = (value, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        step(3)
                                        append_read_parameters()
                                        tofile()
                                    else:
                                        self.value3 += self.step3
                                back_and_forth_transposition(3)
                                
                            self.value3 = self.from_sweep3
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False) 
                        
                        if back_and_forth_master == True:
                            back_and_forth_transposition(2)
                            while condition(2) and manual_sweep_flags == [1, 0, 0]:
                                globals()['dataframe'] = [*dataframe_after]
                                step(2)
                                dataframe_after_after = [*globals()['dataframe']]
                                while condition(3) and manual_sweep_flags == [1, 0, 0]:
                                    if self.isinarea(point = (value, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        step(3)
                                        append_read_parameters()
                                        tofile()
                                    else:
                                        self.value3 += self.step3
                                
                                if back_and_forth_slave == True:
                                    back_and_forth_transposition(3)
                                    while condition(3) and manual_sweep_flags == [1, 0, 0]:
                                        if self.isinarea(point = (value, self.value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            step(3)
                                            append_read_parameters()
                                            tofile()
                                        else:
                                            self.value3 += self.step3
                                    back_and_forth_transposition(3)
                                    
                                self.value3 = self.from_sweep3
                                i += 1
                                globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                                update_filename(i)
                                globals()['dataframe'].to_csv(self.filename_sweep, index=False) 
                                back_and_forth_transposition(2)
                                
                    else:
                        break

            while condition(1) and manual_sweep_flags == [0, 1, 0]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                data = pd.read_csv(manual_filenames[1]).values.reshape(-1)
                for i, value in enumerate(data):
                    if manual_sweep_flags == [0, 1, 0]:
                        determine_step(i, data, 2)
                        globals()['dataframe'] = [*dataframe_after]
                        step(2, value = value)
                        dataframe_after_after = [*globals()['dataframe']]
                        while condition(3) and manual_sweep_flags == [0, 1, 0]:
                            if self.isinarea(point = (self.value1, value, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                globals()['dataframe'] = [*dataframe_after_after]
                                step(3)
                                append_read_parameters()
                                tofile()
                            else:
                                self.value3 += self.step3
                            
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(3)
                            while condition(3) and manual_sweep_flags == [0, 1, 0]:
                                if self.isinarea(point = (self.value1, value, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    step(3)
                                    append_read_parameters()
                                    tofile()
                                else:
                                    self.value3 += self.step3
                            back_and_forth_transposition(3)
                            
                        self.value3 = self.from_sweep3
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    else:
                        break
                    
                if back_and_forth_master == True:
                    back_and_forth_transposition(2)
                    for i, value in enumerate(data[::1]):
                        if manual_sweep_flags == [0, 1, 0]:
                            determine_step(i, data, 2)
                            globals()['dataframe'] = [*dataframe_after]
                            step(2, value = value)
                            dataframe_after_after = [*globals()['dataframe']]
                            while condition(3) and manual_sweep_flags == [0, 1, 0]:
                                if self.isinarea(point = (self.value1, value, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    step(3)
                                    append_read_parameters()
                                    tofile()
                                else:
                                    self.value3 += self.step3
                                
                            if back_and_forth_slave == True:
                                back_and_forth_transposition(3)
                                while condition(3) and manual_sweep_flags == [0, 1, 0]:
                                    if self.isinarea(point = (self.value1, value, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        step(3)
                                        append_read_parameters()
                                        tofile()
                                    else:
                                        self.value3 += self.step3
                                back_and_forth_transposition(3)
                                
                            self.value3 = self.from_sweep3
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        else:
                            break
                    back_and_forth_transposition(2)

            while condition(1) and manual_sweep_flags == [0, 0, 1]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                while condition(2) and manual_sweep_flags == [0, 0, 1]:
                    globals()['dataframe'] = [*dataframe_after]
                    step(2)
                    dataframe_after_after = [*globals()['dataframe']]
                    data = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                    for i, value in enumerate(data):
                        if manual_sweep_flags == [0, 0, 1]:
                            if self.isinarea(point = (self.value1, self.value2, value), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                globals()['dataframe'] = [*dataframe_after_after]
                                determine_step(i, data, 3)
                                step(3, value = value)
                                append_read_parameters()
                                tofile()
                        else:
                            break
                        
                    if back_and_forth_slave == True:
                        back_and_forth_transposition(3)
                        for i, value in enumerate(data):
                            if manual_sweep_flags == [0, 0, 1]:
                                if self.isinarea(point = (self.value1, self.value2, value), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    determine_step(i, data, 3)
                                    step(3, value = value)
                                    append_read_parameters()
                                    tofile()
                        back_and_forth_transposition(3)
                    i += 1
                    globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                    update_filename(i)
                    globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                
                if back_and_forth_master == True:
                    back_and_forth_transposition(2)
                    while condition(2) and manual_sweep_flags == [0, 0, 1]:
                        globals()['dataframe'] = [*dataframe_after]
                        step(2)
                        dataframe_after_after = [*globals()['dataframe']]
                        data = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                        for i, value in enumerate(data):
                            if manual_sweep_flags == [0, 0, 1]:
                                if self.isinarea(point = (self.value1, self.value2, value), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    determine_step(i, data, 3)
                                    step(3, value = value)
                                    append_read_parameters()
                                    tofile()
                            else:
                                break
                            
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(3)
                            for i, value in enumerate(data):
                                if manual_sweep_flags == [0, 0, 1]:
                                    if self.isinarea(point = (self.value1, self.value2, value), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        determine_step(i, data, 3)
                                        step(3, value = value)
                                        append_read_parameters()
                                        tofile()
                            back_and_forth_transposition(3)
                    back_and_forth_transposition(2)
                    i += 1
                    globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                    update_filename(i)
                    globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    
                self.value2 = self.from_sweep3

            if manual_sweep_flags == [1, 1, 0]:
                data1 = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for i1, value1 in enumerate(data1):
                    if manual_sweep_flags == [1, 1, 0]:
                        determine_step(i1, data1, 1)
                        step(1, value = value1)
                        dataframe_after = [*globals()['dataframe']]
                        data2 = pd.read_csv(manual_filenames[1]).values.reshape(-1)
                        for i2, value2 in enumerate(data2):
                            if manual_sweep_flags == [1, 1, 0]:
                                determine_step(i2, data2, 2)
                                globals()['dataframe'] = [*dataframe_after]
                                step(2, value = value2)
                                dataframe_after_after = [*globals()['dataframe']]
                                while condition(3) and manual_sweep_flags == [1, 1, 0]:
                                    if self.isinarea(point = (value1, value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        step(3)
                                        append_read_parameters()
                                        tofile()
                                    else:
                                        self.value3 += self.step3
                                if back_and_forth_slave == True:
                                    back_and_forth_transposition(3)
                                    while condition(3) and manual_sweep_flags == [1, 1, 0]:
                                        if self.isinarea(point = (value1, value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            step(3)
                                            append_read_parameters()
                                            tofile()
                                        else:
                                            self.value3 += self.step3
                                    back_and_forth_transposition(3)
                                        
                            else:
                                break
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        
                        if back_and_forth_master == True:
                            back_and_forth_transposition(2)
                            for i2, value2 in enumerate(data2[::-1]):
                                if manual_sweep_flags == [1, 1, 0]:
                                    determine_step(i2, data2, 2)
                                    globals()['dataframe'] = [*dataframe_after]
                                    step(2, value = value2)
                                    dataframe_after_after = [*globals()['dataframe']]
                                    while condition(3) and manual_sweep_flags == [1, 1, 0]:
                                        if self.isinarea(point = (value1, value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            step(3)
                                            append_read_parameters()
                                            tofile()
                                        else:
                                            self.value3 += self.step3
                                    if back_and_forth_slave == True:
                                        back_and_forth_transposition(3)
                                        while condition(3) and manual_sweep_flags == [1, 1, 0]:
                                            if self.isinarea(point = (value1, value2, self.value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                                globals()['dataframe'] = [*dataframe_after_after]
                                                step(3)
                                                append_read_parameters()
                                                tofile()
                                            else:
                                                self.value3 += self.step3
                                        back_and_forth_transposition(3)
                                            
                                else:
                                    break
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        back_and_forth_transposition(2)
                    else:
                        break
                            
            if manual_sweep_flags == [1, 0, 1]:
                data1 = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for i1, value1 in enumerate(data1):
                    if manual_sweep_flags == [1, 0, 1]:
                        determine_step(i1, data1, 1)
                        step(1, value = value1)
                        while condition(2) and manual_sweep_flags == [1, 0, 1]:
                            globals()['dataframe'] = [*dataframe_after]
                            step(2)
                            dataframe_after_after = [*globals()['dataframe']]
                            data3 = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                            for i3, value3 in enumerate(data3):
                                if manual_sweep_flags == [1, 0, 1]:
                                    if self.isinarea(point = (value1, self.value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        determine_step(i3, data3, 3)
                                        step(3, value = value3)
                                        append_read_parameters()
                                        tofile()
                                        
                            if back_and_forth_slave == True:
                                back_and_forth_transposition(3)
                                for i3, value3 in enumerate(data3):
                                    if manual_sweep_flags == [1, 0, 1]:
                                        if self.isinarea(point = (value1, self.value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            determine_step(i3, data3, 3)
                                            step(3, value = value3)
                                            append_read_parameters()
                                            tofile()
                                back_and_forth_transposition(3)
                                
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                            
                        if back_and_forth_master == True:
                            back_and_forth_transposition(2)
                            while condition(2) and manual_sweep_flags == [1, 0, 1]:
                                globals()['dataframe'] = [*dataframe_after]
                                step(2)
                                dataframe_after_after = [*globals()['dataframe']]
                                data3 = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                                for i3, value3 in enumerate(data3):
                                    if manual_sweep_flags == [1, 0, 1]:
                                        if self.isinarea(point = (value1, self.value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            determine_step(i3, data3, 3)
                                            step(3, value = value3)
                                            append_read_parameters()
                                            tofile()
                                            
                                if back_and_forth_slave == True:
                                    back_and_forth_transposition(3)
                                    for i3, value3 in enumerate(data3):
                                        if manual_sweep_flags == [1, 0, 1]:
                                            if self.isinarea(point = (value1, self.value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                                globals()['dataframe'] = [*dataframe_after_after]
                                                determine_step(i3, data3, 3)
                                                step(3, value = value3)
                                                append_read_parameters()
                                                tofile()
                                    back_and_forth_transposition(3)
                                    
                                i += 1
                                globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                                update_filename(i)
                                globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                            back_and_forth_transposition(2)
                            
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                            
                            
            while condition(1) and manual_sweep_flags == [0, 1, 1]:
                step(1)
                dataframe_after = [*globals()['dataframe']]
                data2 = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                for i2, value2 in enumerate(data2):
                    if manual_sweep_flags == [0, 1, 1]:
                        globals()['dataframe'] = [*dataframe_after]
                        determine_step(i2, data2, 2)
                        step(2, value = value2)
                        dataframe_after_after = [*dataframe]
                        data3 = pd.read_csv(
                            manual_filenames[2]).values.reshape(-1)
                        for i3, value3 in enumerate(data3):
                            if manual_sweep_flags == [0, 1, 1]:
                                if self.isinarea(point = (self.value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    determine_step(i3, data3, 3)
                                    step(3, value = value3)
                                    append_read_parameters()
                                    tofile()
                            else:
                                break
                            
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(3)
                            for i3, value3 in enumerate(data3):
                                if manual_sweep_flags == [0, 1, 1]:
                                    if self.isinarea(point = (self.value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        determine_step(i3, data3, 3)
                                        step(3, value = value3)
                                        append_read_parameters()
                                        tofile()
                                else:
                                    break
                            back_and_forth_transposition(3)
                            
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    else:
                        break
                    
                if back_and_forth_master == True:
                    back_and_forth_transposition(2)
                    for i2, value2 in enumerate(data2):
                        if manual_sweep_flags == [0, 1, 1]:
                            globals()['dataframe'] = [*dataframe_after]
                            determine_step(i2, data2, 2)
                            step(2, value = value2)
                            dataframe_after_after = [*dataframe]
                            data3 = pd.read_csv(
                                manual_filenames[2]).values.reshape(-1)
                            for i3, value3 in enumerate(data3):
                                if manual_sweep_flags == [0, 1, 1]:
                                    if self.isinarea(point = (self.value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        determine_step(i3, data3, 3)
                                        step(3, value = value3)
                                        append_read_parameters()
                                        tofile()
                                else:
                                    break
                                
                            if back_and_forth_slave == True:
                                back_and_forth_transposition(3)
                                for i3, value3 in enumerate(data3):
                                    if manual_sweep_flags == [0, 1, 1]:
                                        if self.isinarea(point = (self.value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                            globals()['dataframe'] = [*dataframe_after_after]
                                            determine_step(i3, data3, 3)
                                            step(3, value = value3)
                                            append_read_parameters()
                                            tofile()
                                    else:
                                        break
                                back_and_forth_transposition(3)
                                
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        else:
                            break
                    back_and_forth_transposition(2)
                    
                    i += 1
                    globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                    update_filename(i)
                    globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        

            if manual_sweep_flags == [1, 1, 1]:
                data1 = pd.read_csv(manual_filenames[0]).values.reshape(-1)
                for i1, value1 in enumerate(data1):
                    determine_step(i1, data1, 1)
                    step(1, value = value1)
                    dataframe_after = [*globals()['dataframe']]
                    data2 = pd.read_csv(
                        manual_filenames[2]).values.reshape(-1)
                    for i2, value2 in enumerate(data2):
                        globals()['dataframe'] = [*dataframe_after]
                        determine_step(i2, data2, 2)
                        step(2, value = value2)
                        dataframe_after_after = [*globals()['dataframe']]
                        data3 = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                        for i3, value3 in enumerate(data3):
                            if self.isinarea(point = (value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                globals()['dataframe'] = [*dataframe_after_after]
                                determine_step(i3, data3, 3)
                                step(value = value3)
                                append_read_parameters()
                                tofile()
                                
                        if back_and_forth_slave == True:
                            back_and_forth_transposition(3)
                            for i3, value3 in enumerate(data3):
                                if self.isinarea(point = (value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    determine_step(i3, data3, 3)
                                    step(value = value3)
                                    append_read_parameters()
                                    tofile()
                            back_and_forth_transposition(3)
                                    
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                    
                    if back_and_forth_master == True:
                        back_and_forth_transposition(2)
                        for i2, value2 in enumerate(data2):
                            globals()['dataframe'] = [*dataframe_after]
                            determine_step(i2, data2, 2)
                            step(2, value = value2)
                            dataframe_after_after = [*globals()['dataframe']]
                            data3 = pd.read_csv(manual_filenames[2]).values.reshape(-1)
                            for i3, value3 in enumerate(data3):
                                if self.isinarea(point = (value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                    globals()['dataframe'] = [*dataframe_after_after]
                                    determine_step(i3, data3, 3)
                                    step(value = value3)
                                    append_read_parameters()
                                    tofile()
                                    
                            if back_and_forth_slave == True:
                                back_and_forth_transposition(3)
                                for i3, value3 in enumerate(data3):
                                    if self.isinarea(point = (value1, value2, value3), grid_area = self.grid_space, dgrid_area = (self.step1 / 2, self.step2 / 2, self.step3 / 2), sweep_dimension = 3):
                                        globals()['dataframe'] = [*dataframe_after_after]
                                        determine_step(i3, data3, 3)
                                        step(value = value3)
                                        append_read_parameters()
                                        tofile()
                                back_and_forth_transposition(3)
                                        
                            i += 1
                            globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                            update_filename(i)
                            globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        back_and_forth_transposition(2)
                        
                        i += 1
                        globals()['dataframe'] = pd.DataFrame(columns=self.columns)
                        update_filename(i)
                        globals()['dataframe'].to_csv(self.filename_sweep, index=False)
                        


class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
        s.pack(side=tk.TOP, pady=5)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass


class Graph(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_x1 = tk.Label(self, text='x', font=LARGE_FONT)
        label_x1.place(relx=0.02, rely=0.455)

        label_y1 = tk.Label(self, text='y', font=LARGE_FONT)
        label_y1.place(relx=0.15, rely=0.455)

        self.combo_x1 = ttk.Combobox(self, values=columns)
        self.combo_x1.bind("<<ComboboxSelected>>", self.x1_update)
        self.combo_x1.place(relx=0.035, rely=0.46)

        self.combo_y1 = ttk.Combobox(self, values=columns)
        self.combo_y1.bind("<<ComboboxSelected>>", self.y1_update)
        self.combo_y1.place(relx=0.165, rely=0.46)

        label_x2 = tk.Label(self, text='x', font=LARGE_FONT)
        label_x2.place(relx=0.52, rely=0.455)

        label_y2 = tk.Label(self, text='y', font=LARGE_FONT)
        label_y2.place(relx=0.65, rely=0.455)

        self.combo_x2 = ttk.Combobox(self, values=columns)
        self.combo_x2.bind("<<ComboboxSelected>>", self.x2_update)
        self.combo_x2.place(relx=0.535, rely=0.46)

        self.combo_y2 = ttk.Combobox(self, values=columns)
        self.combo_y2.bind("<<ComboboxSelected>>", self.y2_update)
        self.combo_y2.place(relx=0.665, rely=0.46)

        label_x3 = tk.Label(self, text='x', font=LARGE_FONT)
        label_x3.place(relx=0.02, rely=0.955)

        label_y3 = tk.Label(self, text='y', font=LARGE_FONT)
        label_y3.place(relx=0.15, rely=0.955)

        self.combo_x3 = ttk.Combobox(self, values=columns)
        self.combo_x3.bind("<<ComboboxSelected>>", self.x3_update)
        self.combo_x3.place(relx=0.035, rely=0.96)

        self.combo_y3 = ttk.Combobox(self, values=columns)
        self.combo_y3.bind("<<ComboboxSelected>>", self.y3_update)
        self.combo_y3.place(relx=0.165, rely=0.96)

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

        plot221 = FigureCanvasTkAgg(fig221, self)
        plot221.draw()
        plot221.get_tk_widget().place(relx=0.02, rely=0)

        toolbar221 = VerticalNavigationToolbar2Tk(plot221, self)
        toolbar221.update()
        toolbar221.place(relx=0.45, rely=0)
        plot221._tkcanvas.place(relx=0.02, rely=0)

        plot222 = FigureCanvasTkAgg(fig222, self)
        plot222.draw()
        plot222.get_tk_widget().place(relx=0.52, rely=0)

        toolbar222 = VerticalNavigationToolbar2Tk(plot222, self)
        toolbar222.update()
        toolbar222.place(relx=0.95, rely=0)
        plot222._tkcanvas.place(relx=0.52, rely=0)

        plot223 = FigureCanvasTkAgg(fig223, self)
        plot223.draw()
        plot223.get_tk_widget().place(relx=0.02, rely=0.50)

        toolbar223 = VerticalNavigationToolbar2Tk(plot223, self)
        toolbar223.update()
        toolbar223.place(relx=0.45, rely=0.5)
        plot223._tkcanvas.place(relx=0.02, rely=0.5)

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
    #write_config_parameters()
    #write_config_channels()
    app = Universal_frontend(classes=(StartPage, Sweeper1d, Sweeper2d, Sweeper3d),
                             start=StartPage)
    app.mainloop()
    while True:
        pass


if __name__ == '__main__':
    main()