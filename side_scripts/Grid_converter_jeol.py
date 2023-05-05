import tkinter as tk
import tkinter.filedialog
import numpy as np

LARGE_FONT = ('Verdana', 12)
SUPER_LARGE = ('Verdana', 16)

class Universal_frontend(tk.Tk):

    def __init__(self, classes, start, size = '350x300', title = 'Grid', *args, **kwargs):
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
        
        label_x1 = tk.Label(self, text = r'X_ref1', font = LARGE_FONT)
        label_x1.grid(row = 0, column = 0, pady = 2)
        
        label_y1 = tk.Label(self, text = r'Y_ref1', font = LARGE_FONT)
        label_y1.grid(row = 0, column = 1, pady = 2)
        
        self.entry_x1 = tk.Entry(self)
        self.entry_x1.grid(row = 1, column = 0, pady = 2)
        
        self.entry_y1 = tk.Entry(self)
        self.entry_y1.grid(row = 1, column = 1, pady = 2)
        
        label_x2 = tk.Label(self, text = r'X_ref2', font = LARGE_FONT)
        label_x2.grid(row = 2, column = 0, pady = 2)
        
        label_y2 = tk.Label(self, text = r'Y_ref', font = LARGE_FONT)
        label_y2.grid(row = 2, column = 1, pady = 2)
        
        self.entry_x2 = tk.Entry(self)
        self.entry_x2.grid(row = 3, column = 0, pady = 2)
        
        self.entry_y2 = tk.Entry(self)
        self.entry_y2.grid(row = 3, column = 1, pady = 2)
        
        label_x = tk.Label(self, text = r'X_point', font = LARGE_FONT)
        label_x.grid(row = 4, column = 0, pady = 2)
        
        label_y = tk.Label(self, text = r'Y_point', font = LARGE_FONT)
        label_y.grid(row = 4, column = 1, pady = 2)
        
        self.entry_x = tk.Entry(self)
        self.entry_x.grid(row = 5, column = 0, pady = 2)
        
        self.entry_y = tk.Entry(self)
        self.entry_y.grid(row = 5, column = 1, pady = 2)
        
        button_get = tk.Button(self, text = 'Get coordinates', command = self.start)
        button_get.grid(row = 5, column = 2, pady = 2)
        
        filler = tk.Label(self, text = ' ')
        filler.grid(row = 8, column = 0)
        
    def start(self):
        try:
            
            self.x1 = float(self.entry_x1.get())
            self.x2 = float(self.entry_x2.get())
            self.x3 = float(self.entry_x.get())
            self.y1 = float(self.entry_y1.get())
            self.y2 = float(self.entry_y2.get())
            self.y3 = float(self.entry_y.get())
            
            a = np.sqrt((self.x3 - self.x1)**2 + (self.y3 - self.y1)**2)
            b = np.sqrt((self.x3 - self.x2)**2 + (self.y3 - self.y2)**2)
            c = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
            
            cos_theta = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
            if self.x3 > - (self.y2 - self.y1) / (self.x2 - self.x1) * (self.y3 - self.y1) + self.x1:
                self.l = a * cos_theta
            else:
                self.l = -a * cos_theta
            
            if self.y3 > (self.y2 - self.y1) / (self.x2 - self.x1) * (self.x3 - self.x1) + self.y1:
                self.h = - a * np.sqrt(1 - cos_theta ** 2)
            else:
                self.h =  a * np.sqrt(1 - cos_theta ** 2)
            
            if not hasattr(self, 'label_x_point'):
                self.label_x_point = tk.Label(self, text = 'X_new = {:.6e}'.format(self.l), font = LARGE_FONT)
                self.label_x_point.grid(row = 6, column = 0, pady = 2, columnspan = 2)
            else:
                self.label_x_point.configure(text = 'X_new = {:.6e}'.format(self.l))
                
            if not hasattr(self, 'label_y_point'):
                self.label_y_point = tk.Label(self, text = 'Y_new = {:.6e}'.format(self.h), font = LARGE_FONT)
                self.label_y_point.grid(row = 7, column = 0, pady = 2, columnspan = 2)
            else:
                self.label_y_point.configure(text = 'Y_new = {:.6e}'.format(self.h))
                
            if not hasattr(self, 'label_x_jeol'):
                self.label_x_jeol = tk.Label(self, text = 'X_jeol = {:.6e}'.format((-10000 + self.l)), font = LARGE_FONT)
                self.label_x_jeol.grid(row = 9, column = 0, pady = 2, columnspan = 2)
            else:
                self.label_x_jeol.configure(text = 'X_jeol = {:.6e}'.format((-10000 + self.l)))
                
            if not hasattr(self, 'label_y_jeol'):
                self.label_y_jeol = tk.Label(self, text = 'Y_jeol = {:.6e}'.format((10000 - self.h)), font = LARGE_FONT)
                self.label_y_jeol.grid(row = 10, column = 0, pady = 2, columnspan = 2)
            else:
                self.label_y_jeol.configure(text = 'Y_jeol = {:.6e}'.format((10000 - self.h)))
            
        except Exception as e:
            tk.messagebox.showwarning(title='Warning', message=e)
        
        
        
def main():
    app = Universal_frontend(classes=(StartPage,), start=StartPage)
    app.mainloop()
    while True:
        pass


if __name__ == '__main__':
    main()
    
    