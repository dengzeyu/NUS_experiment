import pyvisa as visa
from pyvisa import constants
import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
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

#Check if everything connected properly
rm = visa.ResourceManager()
rm.list_resources()

print(rm.list_resources(), '\n')

#Setting devices names
################################################################################
#keithley 6514 electrometer
keit_elec = rm.open_resource('GPIB0::1::INSTR', write_termination= '\n', 
                             read_termination='\n')
keit_elec.write('*rst; *cls') #reset + clear status
keit_elec.write('VOLT:DC:NPLC 0.55') #number of power line status (0.1, 10)
################################################################################


################################################################################
#keythley 2200-20-5 power supply
power_supply = rm.open_resource('GPIB0::2::INSTR', write_termination= '\n', 
                             read_termination='\n')
################################################################################


################################################################################
#thorlabs TC300 temperature controller
temp = rm.open_resource('ASRL3::INSTR', baud_rate = 115200, 
                        data_bits = 8, parity = constants.VI_ASRL_PAR_NONE,
                        stop_bits = constants.VI_ASRL_STOP_ONE, 
                        flow_control = constants.VI_ASRL_FLOW_NONE,
                        write_termination = '\r', read_termination = '\r')

################################################################################

#Write command to a device and get it's output
def get(device, command):
    device.write(command)
    return device.read()

#starting time
zero_time = time.process_time()

#Create Pandas dataframe and filename

filename = r'C:\NUS\Transport lab\Test\data_files\test' + datetime.today().strftime(
                                '%H_%M_%d_%m_%Y') + '.csv' 
data = pd.DataFrame(columns = ['time', 'keit_elec', 'temp', 'power_supply'], dtype = float)

#defining window initial parameters
fig = Figure(figsize = (6, 2.5), dpi = 200)

#defining subplots location

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

def animate(i):
    #function to animate graph on each step
    
    global data
    
    cur_time = time.process_time() - zero_time
    
    appended_dataframe = pd.DataFrame({'time': [cur_time], 
                                       'keit_elec': [float(get(keit_elec, 'READ?')[0:13])],
                                       'temp': [float(get(temp, 'TACT1?')[2:])],
                                       'power_supply': [float(get(power_supply, 'FETC:VOLT:DC?'))]})
    
    data = pd.concat([data, appended_dataframe])
    data.to_csv(filename, sep = ' ')
     
    #Plotting data
    keit_elec_data = pd.read_csv(filename, sep = ' ')['keit_elec'].values.tolist()
    temp_data = pd.read_csv(filename, sep = ' ')['temp'].values.tolist()
    power_supply_data = pd.read_csv(filename, sep = ' ')['power_supply'].values.tolist()
    time_data = pd.read_csv(filename, sep = ' ')['time'].values.tolist()
    
    ax1.clear()
    ax1.plot(time_data, keit_elec_data, lw = 1, color = 'blue')
    
    ax2.clear()
    ax2.plot(time_data, temp_data, lw = 1, color = 'crimson')
    
    ax3.clear()
    ax3.plot(time_data, power_supply_data, lw = 1, color = 'green')


#Setting classes for each device

class keit_elec:
    #set a query for keit_elec device to get a value on a screen
    def __init__(self, *args, **kwargs):
        self.value = [float(get(keit_elec, 'READ?')[0:13])]

    
class spectrometer(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.iconbitmap(self)
        tk.Tk.wm_title(self, 'Keitley test')
        
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
        label.pack()
        
        button  = ttk.Button(self, text = 'Back to Home', command = lambda: controller.show_frame(StartPage))
        button.pack()
        
class Graph(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = 'graph', font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
        button = ttk.Button(self, text = 'Back to Home', command = lambda: controller.show_frame(StartPage))
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
    ani = animation.FuncAnimation(fig, animate, interval = interval)
    app.mainloop()
    
if __name__ == '__main__':
    main()