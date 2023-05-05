import pandas as pd
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import numpy as np

LARGE_FONT = ('Verdana', 12)
SUPER_LARGE = ('Verdana', 16)

class Universal_frontend(tk.Tk):

    def __init__(self, classes, start, size = '350x250', title = 'Symmetrisation / antisymmetrisation', *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self)
        tk.Tk.geometry(self, newGeometry = size)
        tk.Tk.wm_title(self, title)

        container = tk.Frame(self)
        container.grid(column = 0, row = 0)
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
        globals()['Sweeper_object'] = frame

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label_filename = tk.Label(self, text = 'Filename', font = LARGE_FONT)
        label_filename.grid(row = 0, column = 0, pady = 2)
        
        self.entry_filename = tk.Entry(self)
        #self.entry_filename.insert(index = 0)
        self.entry_filename.grid(row = 0, column = 2, pady = 2)
        
        self.button_read_file = tk.Button(self, text = '🔎', font = LARGE_FONT, command = self.explore_file)
        self.button_read_file.grid(row = 0, column = 1, pady = 2)
        
        label_field = tk.Label(self, text = 'Choose field', font = LARGE_FONT)
        label_field.grid(row = 2, column = 0, pady = 2)
        
        self.combo_field = ttk.Combobox(self, value = [''])
        self.combo_field.bind(
            "<<ComboboxSelected>>", self.choose_field)
        self.combo_field.grid(row = 3, column = 0)
        
        label_xx = tk.Label(self, text = 'Choose Uxx', font = LARGE_FONT)
        label_xx.grid(row = 4, column = 0, pady = 2)
        
        label_div1 = tk.Label(self, text = '/', font = LARGE_FONT)
        label_div1.grid(row = 4, column = 1, pady = 2)
        
        label_i_xx = tk.Label(self, text = 'choose Ixx', font = LARGE_FONT)
        label_i_xx.grid(row = 4, column = 2, pady = 2)
        
        self.combo_xx = ttk.Combobox(self, value = [''])
        self.combo_xx.bind(
            "<<ComboboxSelected>>", self.choose_xx)
        self.combo_xx.grid(row = 5, column = 0)
        
        self.combo_i_xx = ttk.Combobox(self, value = [''])
        self.combo_i_xx.bind(
            "<<ComboboxSelected>>", self.choose_i_xx)
        self.combo_i_xx.grid(row = 5, column = 2)
        
        label_xy = tk.Label(self, text = 'Choose Uxy', font = LARGE_FONT)
        label_xy.grid(row = 6, column = 0, pady = 2)
        
        label_div2 = tk.Label(self, text = '/', font = LARGE_FONT)
        label_div2.grid(row = 6, column = 1, pady = 2)
        
        label_i_xy = tk.Label(self, text = 'choose Ixy', font = LARGE_FONT)
        label_i_xy.grid(row = 6, column = 2, pady = 2)
        
        self.combo_xy = ttk.Combobox(self, value = [''])
        self.combo_xy.bind(
            "<<ComboboxSelected>>", self.choose_xy)
        self.combo_xy.grid(row = 7, column = 0, pady = 2)
        
        self.combo_i_xy = ttk.Combobox(self, value = [''])
        self.combo_i_xy.bind(
            "<<ComboboxSelected>>", self.choose_i_xy)
        self.combo_i_xy.grid(row = 7, column = 2, pady = 2)
        
        self.button_start = tk.Button(self, text = 'Start', font = LARGE_FONT, command = self.start)
        self.button_start.grid(row = 8, column = 1, pady = 2)
        
    def explore_file(self):
        self.filenames = tk.filedialog.askopenfilenames(title='Select a file',
                                                                 filetypes=(('all files', '*.*'),
                                                                            ('CSV files', '*.csv*'), 
                                                                            ('TXT files', '*txt'),
                                                                            ('DAT files', '*dat')))
        self.entry_filename.delete(0, tk.END)
        self.entry_filename.insert(0, self.filenames[0])
        self.datas = []
        self.data = pd.read_csv(self.filenames[0])
        self.datas.append(self.data)
        self.columns = list(self.data.columns)
        for ind, file in enumerate(self.filenames[1:]):
            data = pd.read_csv(file)
            self.datas.append(data)
            if list(data.columns) != self.columns:
                tk.messagebox.showwarning('Columns warning', f'Columns in file "{file}" not correspond to another columns')
                return
            
        self.combo_field.config(value = self.columns)
        self.combo_xx.config(value = self.columns)
        self.combo_i_xx.config(value = self.columns)
        self.combo_xy.config(value = self.columns)
        self.combo_i_xy.config(value = self.columns)
    
    def choose_field(self, event):
        self.fields = []
        for data in self.datas:
            self.fields.append(data[self.columns[self.combo_field.current()]])
    
    def choose_xx(self, event):
        self.xxs = []
        for data in self.datas:
            self.xxs.append(data[self.columns[self.combo_xx.current()]])
        
    def choose_xy(self, event):
        self.xys = []
        for data in self.datas:
            self.xys.append(data[self.columns[self.combo_xy.current()]])
        
    def choose_i_xx(self, event):
        if self.combo_i_xx.current() != -1 and self.combo_xx.current() != -1:
            for i, data in enumerate(self.datas):
                self.xxs[i] = self.xxs[i] / data[self.columns[self.combo_i_xx.current()]]
            
    def choose_i_xy(self, event):
        if self.combo_i_xy.current() != -1 and self.combo_xy.current() != -1:
            for i, data in enumerate(self.datas):
                self.xys[i] = self.xys[i] / data[self.columns[self.combo_i_xy.current()]]
        
    def start(self):
        
        for i, _ in enumerate(self.filenames):
            self.run(self.filenames[i], self.fields[i], self.xxs[i], self.xys[i])
            print(f'File {i} processed')
            
    def run(self, filename, field, xx, xy):
        
        if field[0] < 0:
            ind_max = np.argmax(field)
        else:
            ind_max = np.argmin(field)
        field_forward = field[:ind_max].values
        field_back = field[ind_max:].values
        
        xx_forward = xx[:ind_max].values
        xx_back = xx[ind_max:].values
        
        xy_forward = xy[:ind_max].values
        xy_back = xy[ind_max:].values
        
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx
        
        idx_z_f = find_nearest(field_forward, 0)
        idx_z_b = find_nearest(field_back, 0)
        

        if field[0] < 0 and field[idx_z_f] < 0:
            idx_z_f += 1
        elif field[0] > 0 and field[idx_z_f] > 0:
            idx_z_f += 1
            
        if field[0] < 0 and field[idx_z_b] < 0:
            idx_z_b -= 1
        elif field[0] > 0 and field[idx_z_b] > 0:
            idx_z_b -= 1
        
        field_forward_negative = field_forward[:idx_z_f]
        field_forward_positive = field_forward[idx_z_f:]
        
        field_back_positive = field_back[:idx_z_b]
        field_back_negative = field_back[idx_z_b:]
        
        xx_forward_negative = xx_forward[:idx_z_f][::-1]
        xx_forward_positive = xx_forward[idx_z_f:]
        
        xx_back_positive = xx_back[:idx_z_b][::-1]
        xx_back_negative = xx_back[idx_z_b:]
        
        xy_forward_negative = xy_forward[:idx_z_f][::-1]
        xy_forward_positive = xy_forward[idx_z_f:]
        
        xy_back_positive = xy_back[:idx_z_b][::-1]
        xy_back_negative = xy_back[idx_z_b:]
        
        first_range = np.argsort(abs(field_forward_negative))
        second_range = np.argsort(abs(field_forward_positive))
        third_range = np.argsort(abs(field_back_positive))
        forth_range = np.argsort(abs(field_back_negative))
        
        min_num = min(first_range.shape[0], second_range.shape[0], third_range.shape[0], forth_range.shape[0])
        
        true_xx_forward_neg = []
        true_xx_forward_pos = []
        true_xx_back_pos = []
        true_xx_back_neg = []
        true_xy_forward_neg = []
        true_xy_forward_pos = []
        true_xy_back_pos = []
        true_xy_back_neg = []
        
        for i in range(min_num):
            true_xx_forward_neg.append((xx_forward_negative[i] + xx_back_positive[i]) / 2)
            true_xx_forward_pos.append((xx_forward_positive[i] + xx_back_negative[i]) / 2)
            true_xx_back_pos.append((xx_back_positive[i] + xx_forward_negative[i]) / 2)
            true_xx_back_neg.append((xx_back_negative[i] + xx_forward_positive[i]) / 2)
            true_xy_forward_neg.append((xy_forward_negative[i] - xy_back_positive[i]) / 2)
            true_xy_forward_pos.append((xy_forward_positive[i] - xy_back_negative[i]) / 2)
            true_xy_back_pos.append((xy_back_positive[i] - xy_forward_negative[i]) / 2)
            true_xy_back_neg.append((xy_back_negative[i] - xy_forward_positive[i]) / 2)
            
        data_xx_forward = np.nan * np.ones_like(xx)
        data_xx_back = np.nan * np.ones_like(xx)
        data_xy_forward = np.nan * np.ones_like(xy)
        data_xy_back = np.nan * np.ones_like(xy)
        
        data_xx_forward[first_range[:min_num]] = true_xx_forward_neg
        if (second_range.shape[0] - min_num) != 0:
            data_xx_forward[idx_z_f + second_range[: - (second_range.shape[0] - min_num)]] = true_xx_forward_pos
        else:
            data_xx_forward[idx_z_f + second_range] = true_xx_forward_pos
        data_xx_back[ind_max + third_range[:min_num]] = true_xx_back_pos
        if (forth_range.shape[0] - min_num) != 0:
            data_xx_back[idx_z_b + ind_max + forth_range[: - (forth_range.shape[0] - min_num)]] = true_xx_back_neg
        else:
            data_xx_back[idx_z_b + ind_max + forth_range] = true_xx_back_neg
        
        data_xy_forward[first_range[:min_num]] = true_xy_forward_neg
        if (second_range.shape[0] - min_num) != 0:
            data_xy_forward[idx_z_f + second_range[: - (second_range.shape[0] - min_num)]] = true_xy_forward_pos
        else:
            data_xy_forward[idx_z_f + second_range] = true_xy_forward_pos

        data_xy_back[ind_max + third_range[:min_num]] = true_xy_back_pos
        if (forth_range.shape[0] - min_num) != 0:
            data_xy_back[idx_z_b + ind_max + forth_range[: - (forth_range.shape[0] - min_num)]] = true_xy_back_neg
        else:
            data_xy_back[idx_z_b + ind_max + forth_range] = true_xy_back_neg
        
        data_xx_forward = data_xx_forward[~np.isnan(data_xx_forward)]
        data_xx_back = data_xx_back[~np.isnan(data_xx_back)][::-1]
        data_xy_forward = data_xy_forward[~np.isnan(data_xy_forward)]
        data_xy_back = data_xy_back[~np.isnan(data_xy_back)][::-1]
        
        sorted_field = np.sort(field[first_range.shape[0] - min_num : ind_max - (second_range.shape[0] - min_num)])
        
        #self.data = self.data.dropna(how = 'any')
        dataframe = pd.DataFrame(columns = ['field', 'xx_forward', 'xx_back', 'xy_forward', 'xy_back'])
        dataframe['field'] = sorted_field
        dataframe['xx_forward'] = data_xx_forward
        dataframe['xx_back'] = data_xx_back
        dataframe['xy_forward'] = data_xy_forward
        dataframe['xy_back'] = data_xy_back
        
        dataframe.to_csv(filename[:-4] + '_sym.csv', sep = ' ', index= False)
        
def main():
    app = Universal_frontend(classes=(StartPage,), start=StartPage)
    app.mainloop()
    while True:
        pass


if __name__ == '__main__':
    main()
    
    