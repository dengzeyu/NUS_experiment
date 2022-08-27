import pyvisa as visa
from pyvisa import constants
import time
from datetime import datetime
import pandas as pd
import matplotlib
import numpy as np
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

#Check if everything connected properly
rm = visa.ResourceManager()
rm.list_resources()

print(rm.list_resources(), '\n')

class lock_in():
    
    def __init__(self, adress = 'GPIB0::3::INSTR'):
        
        self.sr830 = 5#rm.open_resource(adress, write_termination= '\n', read_termination='\n')
        
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
        
        
    def frequency(self):
        return get(self.sr830, 'FREQ?')
    
    def phase(self):
        return get(self.sr830, 'PHAS?')
        
    def amplitude(self):
        return get(self.sr830, 'SLVL?')
    
    def sensitivity(self):
        return get(self.sr830, 'SENS?')
    
    def time_constant(self):
        return get(self.sr830, 'OFLT?')
    
    def low_pass_filter_slope(self):
        return get(self.sr830, 'OFSL?')
    
    def synchronous_filter_status(self):
        return get(self.sr830, 'SYNC?')
    
    def remote(self):
        return get(self.sr830, 'OVRM?')
    
    def ch1(self):
        return get(self.sr830, 'OUTR?1')
    
    def ch2(self):
        return get(self.sr830, 'OUTR?2')
    
    def error(self):
        return get(self.sr830, 'ERRS?')
        
    def parameter(self):
        return pd.DataFrame({'Sensitivity': int([self.sensitivity()])}, 
                                 {'Time constant': int([self.time_constant()])},
                                 {'Low pass filter slope': int([self.low_pass_filter_slope()])}, 
                                 {'Synchronous filter status': int([self.synchronous_filter_status()])},
                                 {'Remote': int([self.remote()])},
                                 {'Ch1': float([self.ch1()])},
                                 {'Ch2': float([self.ch2()])},
                                 {'Amplitude': float([self.amplitude()])}, 
                                 {'Frequency': float([self.frequency()])},
                                 {'Phase': float([self.phase()])},
                                 {'Error': str([self.error()])})
    
    def snap_data(self):
        return get(self.sr830, 'SNAP?1,2,3,4')
    
    def x(self):
        return self.snap_data[:10]
    
    def y(self):
        return self.snap_data[12:22]
    
    def r(self):
        return self.snap_data[24:34]
    
    def theta(self):
        return self.snap_data[36:]
    
    def snap_aux(self):
        return get(self.sr830, 'SNAP?5,6,7,8')
    
    def aux1(self):
        return self.snap_aux[:9]
    
    def aux2(self):
        return self.snap_aux[11:20]
    
    def aux3(self):
        return self.snap_aux[22:26]
    
    def aux4(self):
        return self.snap_aux[28:]
        
    def data(self):
    
        return pd.DataFrame({'X': float(self.x()), 'Y': float(self.y()), 'R': float(self.r()), 
                             'Theta': float(self.theta()), 'AUX1': float(self.aux1()),
                             'AUX2': float(self.aux2()), 'AUX3': float(self.aux3()), 'AUX4': float(self.aux4())})
        
    def set_ch1_mode(self, mode = 0):
        line = 'DDEF?1,' + str(mode)
        self.sr830.write(line)
        
    def set_ch2_mode(self, mode = 0):
        line = 'DDEF?2,' + str(mode)
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
        
    def set_aux_voltage(self, ch = 1, V = 0):
        line = 'AUXV' + str(ch) + ',' + str(V)
        self.sr830.write(line)
        
        
#Write command to a device and get it's output
def get(device, command):
    #device.write(command)
    return np.random.random(1)#device.read()

config_filename = r'C:\NUS\Transport lab\App\config\parameter.csv'

def write_config(dataframe, filename = config_filename):
    dataframe.to_csv(filename, sep = ' ')
    
#starting time
zero_time = time.process_time()

#Create Pandas dataframe and filename

filename = r'C:\NUS\Transport lab\Test\data_files\test' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv' 
data = pd.DataFrame(columns = ['time', 'keit_elec', 'temp', 'power_supply'], dtype = float)

#defining window initial parameters
fig = Figure(figsize = (6, 2.5), dpi = 200)

#defining subplots location

'''
ax1 = fig.add_subplot(221)
ax1.set_title(r'V(t)')
ax1.set_xlabel(r'Time, $s$')
ax1.set_ylabel(r'DC voltage, $V$')

ax2 = fig.add_subplot(222)
ax2.set_title(r'T(t)')
ax2.set_xlabel(r'Time, $s$')
ax2.set_ylabel(r'Temperature, $\degree C$')

ax3 = fig.add_subplot(223)
ax3.set_title(r'V(t)')
ax3.set_xlabel(r'Time, $s$')
ax3.set_ylabel(r'Power voltage, $V$')
'''

def animate(i):#, spectrometer_instance):
    #function to animate graph on each step
    global data
    
    cur_time = time.process_time() - zero_time
    
    appended_dataframe = pd.DataFrame({'time': [cur_time]
                                       })
    data = pd.concat([data, appended_dataframe])
    data.to_csv(filename, sep = ' ')
     
    #Plotting data
    keit_elec_data = pd.read_csv(filename, sep = ' ')['keit_elec'].values.tolist()
    temp_data = pd.read_csv(filename, sep = ' ')['temp'].values.tolist()
    power_supply_data = pd.read_csv(filename, sep = ' ')['power_supply'].values.tolist()
    time_data = pd.read_csv(filename, sep = ' ')['time'].values.tolist()
    
    #spectrometer_instance.frames[Settings].update()
    
    
    '''
    ax1.clear()
    ax1.plot(time_data, keit_elec_data, lw = 1, color = 'blue')
    
    ax2.clear()
    ax2.plot(time_data, temp_data, lw = 1, color = 'crimson')
    
    ax3.clear()
    ax3.plot(time_data, power_supply_data, lw = 1, color = 'green')
    '''

class spectrometer(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.iconbitmap(self)
        tk.Tk.wm_title(self, 'Lock in test')
        
        container = tk.Frame(self)
        container.pack(side = 'top', fill = 'both', expand = 'True')
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}
        
        for F in (StartPage, Settings, Graph):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
        
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = 'Start Page', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button = ttk.Button(self, text = "Settings", command = lambda: controller.show_frame(Settings))
        button.pack()
        
        button2 = ttk.Button(self, text = 'Graph', command = lambda: controller.show_frame(Graph))
        button2.pack()
        
        
class Settings(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text = 'Settings', font = LARGE_FONT)
        label.place(relx = 0.485, rely = 0.02)
        
        label_time_constant = tk.Label(self, text = 'Time constant')
        label_time_constant.place(relx = 0.02, rely = 0.015)
        
        self.combo_time_constant = ttk.Combobox(self,
                                        value = lock_in().time_constant_options)
        self.combo_time_constant.current(8)
        self.combo_time_constant.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_time_constant).start())
        self.combo_time_constant.place(relx = 0.02, rely = 0.05)
        
        self.value_time_constant = tk.StringVar(value = '0.0')
        self.label_value_time_constant = tk.Label(self, text = (self.value_time_constant.get()))
        self.label_value_time_constant.place(relx = 0.02, rely = 0.085)
        
        label_low_pass_filter_slope = tk.Label(self, text = 'Low pass filter slope')
        label_low_pass_filter_slope.place(relx = 0.02, rely = 0.125)
        
        self.combo_low_pass_filter_slope = ttk.Combobox(self, 
                                        value = lock_in().low_pass_filter_slope_options)
        self.combo_low_pass_filter_slope.current(1)
        self.combo_low_pass_filter_slope.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_low_pass_filter_slope).start())
        self.combo_low_pass_filter_slope.place(relx = 0.02, rely = 0.160)
        
        self.value_low_pass_filter_slope = tk.StringVar(value = '0.0')
        self.label_value_low_pass_filter_slope = tk.Label(self, text = (self.value_low_pass_filter_slope.get()))
        self.label_value_low_pass_filter_slope.place(relx = 0.02, rely = 0.195)
        
        label_synchronous_filter_status = tk.Label(self, text = 'Synchronous filter status')
        label_synchronous_filter_status.place(relx = 0.02, rely = 0.235)        
        
        self.combo_synchronous_filter_status = ttk.Combobox(self, 
                                        value = lock_in().synchronous_filter_status_options)
        self.combo_synchronous_filter_status.current(0)
        self.combo_synchronous_filter_status.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_synchronous_filter_status).start())
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
        self.combo_sensitivity.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_sensitivity).start())
        self.combo_sensitivity.place(relx = 0.15, rely = 0.05)
        
        self.value_sensitivity = tk.StringVar(value = '0.0')
        self.label_value_sensitivity = tk.Label(self, text = (self.value_sensitivity.get()))
        self.label_value_sensitivity.place(relx = 0.15, rely = 0.085)
        
        label_remote = tk.Label(self, text = 'Display locking')
        label_remote.place(relx = 0.15, rely = 0.125)        

        self.combo_remote = ttk.Combobox(self, value = lock_in().remote_status_options)
        self.combo_remote.current(1)
        self.combo_remote.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_remote).start())
        self.combo_remote.place(relx = 0.15, rely = 0.160)
        
        self.value_remote = tk.StringVar(value = '0.0')
        self.label_value_remote = tk.Label(self, text = (self.value_remote.get()))
        self.label_value_remote.place(relx = 0.15, rely = 0.195)
        
        self.value_ch1 = tk.StringVar(value = '0.0')
        self.label_value_ch1 = tk.Label(self, text = ('\n' + self.value_ch1.get()), font = ('Arial', 16))
        self.label_value_ch1.place(relx = 0.15, rely = 0.3)
        
        self.combo_ch1 = ttk.Combobox(self, value = lock_in().modes_ch1_options)
        self.combo_ch1.current(0)
        self.combo_ch1.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_ch1_mode).start())
        self.combo_ch1.place(relx = 0.15, rely = 0.4)
         
        self.value_ch2 = tk.StringVar(value = '0.0')
        self.label_value_ch2 = tk.Label(self, text = ('\n' + self.value_ch1.get()), font = ('Arial', 16))
        self.label_value_ch2.place(relx = 0.3, rely = 0.3)
        
        self.combo_ch2 = ttk.Combobox(self, value = lock_in().modes_ch2_options)
        self.combo_ch2.current(0)
        self.combo_ch2.bind("<<ComboboxSelected>>", threading.Thread(target = self.set_ch2_mode).start())
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
        threading.Thread(target = self.update_sensitivity()).start()
        threading.Thread(target = self.update_time_constant()).start()
        threading.Thread(target = self.update_low_pass_filter_slope()).start()
        threading.Thread(target = self.update_synchronous_filter_status()).start()
        threading.Thread(target = self.update_remote()).start()
        threading.Thread(target = self.update_amplitude()).start()
        threading.Thread(target = self.update_phase()).start()
        threading.Thread(target = self.update_frequency()).start()
        threading.Thread(target = self.update_value_ch1()).start()
        threading.Thread(target = self.update_value_ch2()).start()
        
        button_back_home  = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button_back_home.place(relx = 0.85, rely = 0.85)
        
    def set_sensitivity(self):
        lock_in().set_sensitivity(mode = int(self.combo_sensitivity.current()))
        
    def set_time_constant(self):
        lock_in().set_time_constant(mode = int(self.combo_time_constant.current()))
        
    def set_low_pass_filter_slope(self):
        lock_in().set_low_pass_filter_slope(
            mode = int(self.combo_low_pass_filter_slope.current()))
    
    def set_synchronous_filter_status(self):
        lock_in().set_synchronous_filter_status(
            mode = int(self.combo_synchronous_filter_status.current()))
     
    def set_ch1_mode(self):
        lock_in().set_ch1_mode(mode = int(self.combo_ch1.current()))
    
    def set_ch2_mode(self):
        lock_in().set_ch2_mode(mode = int(self.combo_ch2.current()))
    
    def set_remote(self):
        lock_in().set_remote(mode = int(self.combo_remote.current()))
        
    def aux_button_clicked(self):
        lock_in().set_aux_voltage(ch = 1, V = float(self.aux1_initial.get()))
        lock_in().set_aux_voltage(ch = 2, V = float(self.aux2_initial.get()))
        lock_in().set_aux_voltage(ch = 3, V = float(self.aux3_initial.get()))
        lock_in().set_aux_voltage(ch = 4, V = float(self.aux4_initial.get()))
        
    def reference_button_clicked(self):
        lock_in().set_frequency(value = float(self.frequency_initial.get()))
        lock_in().set_phase(value = float(self.phase_initial.get()))
        lock_in().set_amplitude(value = float(self.amplitude_initial.get()))
        
    def update_time_constant(self, interval = 1000):     
        
        self.label_value_time_constant['text'] = str(lock_in().time_constant_options[int(lock_in().time_constant())])
        self.label_value_time_constant.after(interval, self.update_time_constant)
        
        
    def update_sensitivity(self, interval = 1000):
    
        self.label_value_sensitivity['text'] = str(lock_in().sensitivity_options[int(lock_in().sensitivity())])
        self.label_value_sensitivity.after(interval, self.update_sensitivity)
        
    def update_low_pass_filter_slope(self, interval = 1000):
        
        self.label_value_low_pass_filter_slope['text'] = str(lock_in().low_pass_filter_slope_options[int(lock_in().low_pass_filter_slope())])
        self.label_value_low_pass_filter_slope.after(interval, self.update_low_pass_filter_slope)
        
    def update_synchronous_filter_status(self, interval = 1000):
    
        self.label_value_synchronous_filter_status['text'] = str(lock_in().synchronous_filter_status_options[int(lock_in().synchronous_filter_status())])
        self.label_value_synchronous_filter_status.after(interval, self.update_synchronous_filter_status)
        
    def update_remote(self, interval = 1000): 

        self.label_value_remote['text'] = str(lock_in().remote_status_options[int(lock_in().remote())])
        self.label_value_remote.after(interval, self.update_remote)
        
    def update_amplitude(self, interval = 500):
     
        self.label_value_amplitude['text'] = str(lock_in().amplitude())
        self.label_value_amplitude.after(interval, self.update_amplitude)
        
    def update_phase(self, interval = 500):
        
        self.label_value_phase['text'] = str(lock_in().phase())
        self.label_value_phase.after(interval, self.update_phase)
     
    def update_frequency(self, interval = 500):   
     
        self.label_value_frequency['text'] = str(lock_in().frequency())
        self.label_value_frequency.after(interval, self.update_frequency)
      
    def update_value_ch1(self, interval = 100):
      
        self.label_value_ch1['text'] = '\n' + str(lock_in().ch1())
        self.label_value_ch1.after(interval, self.update_value_ch1)
       
    def update_value_ch2(self, interval = 100): 
       
        self.label_value_ch2['text'] = '\n' + str(lock_in().ch2())
        self.label_value_ch2.after(interval, self.update_value_ch2)
    
        
class Graph(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = 'graph', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button = ttk.Button(self, text = 'Back to Home', 
                            command = lambda: controller.show_frame(StartPage))
        button.pack()
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        
interval = 100

def main():
    app = spectrometer()
    ani = animation.FuncAnimation(fig, animate, interval = interval)#, fargs = (app,))
    app.mainloop()
    
if __name__ == '__main__':
    main()