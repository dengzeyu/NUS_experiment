import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.rcParams['animation.html'] = 'jshtml'
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk

LARGE_FONT = ('Verdana', 12)
style.use('ggplot')

#forming data into file
zero_time = time.process_time()
data = pd.DataFrame(columns = ['Time', 'lock_in', 'wwl', 'V_keyt2010', 'N_steps'], dtype = float)

filename = r'C:\NUS\Transport lab\Test\data_files\test' + datetime.today().strftime('%H_%M_%d_%m_%Y') + '.csv'

print(filename, '\n')

fig = Figure(figsize = (5, 5), dpi = 200)
ax = fig.add_subplot(111)

def animate(i):
    
    global data

    cur_time = time.process_time() - zero_time
    
    appended_dataframe = pd.DataFrame({'Time': [cur_time], 'lock_in': float(np.random.rand(1)), 'wwl': [float(np.random.rand(1))], 'V_keyt2010': [float(np.random.rand(1))], 'N_steps': [float(np.random.rand(1))]})
    data = pd.concat([data, appended_dataframe])
    data.to_csv(filename, sep = ' ')
                
    #Plotting data
    y = pd.read_csv(filename, sep = ' ')['lock_in'].values.tolist()
    x = pd.read_csv(filename, sep = ' ')['Time'].values.tolist()
    
    ax.clear()
    ax.plot(x, y, '-o', color = 'blue')

    

class spectrometer(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.iconbitmap(self)
        tk.Tk.wm_title(self, 'spectrometer')
        
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


def main():
    app = spectrometer()
    ani = animation.FuncAnimation(fig, animate, interval = 20)
    app.mainloop()
    
if __name__ == '__main__':
    main()
