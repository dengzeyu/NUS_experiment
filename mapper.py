import numpy as np
import os
from scipy import interpolate
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams.update({'figure.max_open_warning': 0})
import imageio

"""
A classes that helps to collect data from 2D and 3D sweeps
"""

int1, int2 = np.meshgrid(np.arange(0, 10), np.arange(0, 10))

possibilities = []
for i in range(0, int1.flatten().shape[0]):
    possibilities.append(f'{int1.flatten()[i]}.{int2.flatten()[i]}')

def unify_filename(filename: str, possibilities = possibilities):
    '''
    A function that removes "_......int1.int2_........int3.int4" from filename
    '''
    if any((match1 := num) in filename for num in possibilities):
        filename = (filename[:filename.index(match1)], filename[filename.index(match1) + 3:])
        idx_ = len(filename[0]) - filename[0][::-1].index('_') - 1
        name = filename[0][:idx_] + filename[1]
    else:
        name = filename
    if any((match2 := num) in name for num in possibilities):
        name = (name[:name.index(match2)], name[name.index(match2) + 3:])
        idx_ = len(name[0]) - name[0][::-1].index('_') - 1
        name = name[0][:idx_] + name[1]
    return name

def fix_unicode(filename: str):
    if ':' in filename and ':\\' not in filename:
        filename = filename.replace(':', ':\\')
    return filename

def save_map(path, min_z = None, max_z = None):
    
    '''
    Creates .png image from a table with filename 'path'
    '''
    
    image_filename = os.path.normpath(path).split(os.path.sep)
    image_filename[image_filename.index('tables')] = 'images'
    image_filename[-1] = image_filename[-1].replace('csv', 'png')
    filename = image_filename[-1]

    def fix_unicode(filename: str):
        if ':' in filename and ':\\' not in filename:
            filename = filename.replace(':', ':\\')
        return filename

    to_make = os.path.join(*image_filename[:-1])
    to_make = fix_unicode(to_make)
    if not os.path.exists(to_make):
        os.makedirs(to_make)

    image_filename = os.path.join(to_make, filename)

    parameter = os.path.normpath(path).split(os.path.sep)[-1]
    parameter = parameter.split('_')[1]

    data = pd.read_csv(path, sep = ',')

    fig, ax = plt.subplots()

    plt.ioff()

    names = data.columns.tolist()[0].split(' / ')

    y = data[data.columns.tolist()[0]]
    x = data.columns.tolist()[1:]

    z = [data[i].values for i in x]
    z = np.array(z, dtype = float).T
    z = np.ma.masked_invalid(z)
    
    if min_z == None and max_z == None:
        min_z, max_z = np.nanmin(z), np.nanmax(z)

    y = np.array(y, dtype = float)
    x = np.array(x, dtype = float)

    colormap = ax.pcolormesh(z, cmap = 'viridis', vmin = min_z, vmax = max_z, shading = 'flat')
    colorbar = ax.get_figure().colorbar(colormap, ax = ax)
    colorbar.ax.tick_params(labelsize=5, which = 'both')
    colorbar.set_label(parameter)

    title = f'Map {parameter}'
    xlabel = names[0]
    ylabel = names[1]

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    #ticks and ticklabels
    y_tick_labels = [round(i, 2) for i in y]

    x_tick_labels = [round(i, 2) for i in x]

    y_ticks = []

    for ind, _ in enumerate(y_tick_labels):
        if len(y_tick_labels) != 1 and ind != len(y_tick_labels) - 1:
            y_ticks.append(round((abs((y_tick_labels[ind + 1] - y_tick_labels[ind])) / 2), 2))
        elif len(y_tick_labels) == 1:
            y_ticks.append(round((y_tick_labels[0] + 0.5), 2))

    if len(y_tick_labels) != 1:
        y_ticks.append(round((abs((y_tick_labels[-1] - y_tick_labels[-2])) / 2), 2))

    x_ticks = []

    for ind, _ in enumerate(x_tick_labels):
        if len(x_tick_labels) != 1 and ind != len(x_tick_labels) - 1:
            x_ticks.append(round((((x_tick_labels[ind + 1] - x_tick_labels[ind])) / 2), 2))
        elif len(x_tick_labels) == 1:
            x_ticks.append(round((x_tick_labels[0] + 0.5), 2))

    if len(x_tick_labels) != 1:
        x_ticks.append(round((abs((x_tick_labels[-1] - x_tick_labels[-2])) / 2), 2))

    y_ticks = np.arange(len(y_ticks)) + 0.5

    if len(y_ticks) > 6:
        ax.set_yticks(y_ticks[::len(y_ticks) // 6])
        ax.set_yticklabels(y_tick_labels[::len(y_tick_labels) // 6])
    else:
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_labels)
        
    x_ticks = np.arange(len(x_ticks)) + 0.5
        
    if len(x_ticks) > 6:
        ax.set_xticks(x_ticks[::len(x_ticks) // 6])
        ax.set_xticklabels(x_tick_labels[::len(x_tick_labels) // 6], rotation=30)
    else:
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_tick_labels, rotation=30)
        
    fig.savefig(image_filename, dpi = 300, )

    plt.close(fig)

class mapper2D():
    def __init__(self, parameter_to_sweep1: str, parameter_to_sweep2: str, 
                 parameters_to_read, filename_sweep: str, _from: float, _to: float, 
                 nsteps: int, walks: int, index_filename: int,
                 interpolated = True, uniform = True):
        self.slave = np.array([])
        self.master = np.array([])
        self.parameters_to_read = parameters_to_read
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.filename_sweep = filename_sweep
        self._from = _from
        self._to = _to
        self.nsteps = nsteps
        self.walks = walks
        self.interpolated = interpolated
        self.uniform = uniform
        self.grid = np.linspace(_from, _to, nsteps)
        self.cur_walk = 0
        self.index_filename = index_filename
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])

    def append_slave(self, value):
        if not hasattr(self, f'slave{self.cur_walk}'):
            self.__dict__[f'slave{self.cur_walk}'] = np.array([value])
        else:
            self.__dict__[f'slave{self.cur_walk}'] = np.concatenate((self.__dict__[f'slave{self.cur_walk}'], [value]))
    
    def append_master(self, value):
        self.master = np.concatenate((self.master, [value]))
        
    def append_parameter(self, parameter: str, value):
        if hasattr(self, parameter):
            self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [value]))
            
    def add_sub_slave(self):
        self.cur_walk += 1
            
    def slave_done_walking(self):
        self.slave = np.array([])
        for i in range(self.cur_walk):
            self.slave = np.concatenate((self.slave, self.__dict__[f'slave{i}']))
            
    def clear_sub_slaves(self):
        for i in range(self.cur_walk):
            del self.__dict__[f'slave{i}']
        
        self.cur_walk = 0
        
    
    def concatenate_all(self):
        
        if not self.interpolated: #raw data
            
            if not hasattr(self, 'map_slave') and not hasattr(self, 'map_master'):  #first time
                print('Mapper concatenated at first time')
                self.map_slave = np.array([self.slave])
                self.map_master = np.array([np.ones_like(self.slave) * self.master[-1]])
                self.create_files()
            
            elif hasattr(self, 'map_slave') and hasattr(self, 'map_master'):
                print('Mapper concatenated')
                
                self.check_sizes()
                self.map_slave = np.vstack([self.map_slave, self.slave])
                self.map_master = np.vstack([self.map_master, np.ones_like(self.slave) * self.master[-1]])
            else:
                raise Exception(f'Map_slave status {hasattr(self, "map_slave")}, Map_master status {hasattr(self, "map_master")}')
        
            self.concatenate_parameters()
            
        else: #interpolated
            
            if not hasattr(self, 'map_slave') and not hasattr(self, 'map_master'):  #first time
                print('Mapper concatenated at first time')
                if self.uniform == True:
                    grid = []
                    for walk in range(self.walks):
                        grid = np.concatenate((grid, self.grid[::round(-2*(walk % 2 - 0.5))][round(walk % 2):]))
                    self.map_slave = np.array([grid])
                    self.map_master = np.array([np.ones_like(grid) * self.master[-1]]) 
                else:
                    self.reference_slave = []
                    for i in range(self.cur_walk):
                        self.reference_slave.append(self.__dict__[f'slave{i}'])
                    self.map_slave = np.array([self.slave])
                    self.map_master = np.array([np.ones_like(self.slave) * self.master[-1]]) 
                self.create_files()
                
            elif hasattr(self, 'map_slave') and hasattr(self, 'map_master'):
                print('Mapper concatenated')
                if self.uniform:
                    grid = []
                    for walk in range(self.walks):
                        grid = np.concatenate((grid, self.grid[::round(-2*(walk % 2 - 0.5))][round(walk % 2):]))
                    self.map_slave = np.vstack([self.map_slave, grid])
                    self.map_master = np.vstack([self.map_master, np.ones_like(grid) * self.master[-1]])
                else:
                    slave = np.concatenate(self.reference_slave)
                    self.map_slave = np.vstack([self.map_slave, slave])
                    self.map_master = np.vstack([self.map_master, np.ones_like(slave) * self.master[-1]])
        
            else:
                raise Exception(f'Map_slave status {hasattr(self, "map_slave")}, Map_master status {hasattr(self, "map_master")}')
        
            self.concatenate_parameters()
    
    def concatenate_parameters(self):
        
        def concat(parameter):
            if not self.interpolated: #raw
                
                if not hasattr(self, f'map_{parameter}'):
                    
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.array([self.__dict__[parameter]])
                        self.append_line_to_file(parameter, self.__dict__[parameter])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                    
                elif hasattr(self, f'map_{parameter}'):
                    
                    if hasattr(self, parameter):
                        diff = self.__dict__[f'map_{parameter}'].shape[1] - self.__dict__[parameter].shape[0]
                        if diff < 0:
                            for i in range(abs(diff)):
                                self.__dict__[parameter] =  np.concatenate(self.__dict__[parameter], [np.nan])
                        elif diff > 0:
                            def stack(parameter):
                                self.__dict__[f'map_{parameter}'] = np.hstack([self.__dict__[f'map_{parameter}'], np.array([np.nan * np.ones(self.__dict__[f'map_{parameter}'].shape[0])]).T])
                            for i in range(diff):
                                stack(parameter
                                      )
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.__dict__[parameter]])
                        self.append_line_to_file(parameter, self.__dict__[parameter])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
            
            else: #interpolated
                
                if not hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        interpolated_parameter = self.interpolate(self.__dict__[parameter])
                        self.__dict__[f'map_{parameter}'] = np.array([interpolated_parameter])
                        self.append_line_to_file(parameter, interpolated_parameter)
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        interpolated_parameter = self.interpolate(self.__dict__[parameter])
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], interpolated_parameter])
                        self.append_line_to_file(parameter, interpolated_parameter)
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
        
        for parameter in self.parameters_to_read:
            concat(parameter)
          
    def interpolate(self, parameter):
        res = []
        shape = 0
        
        if self.uniform:
            for ind in range(self.cur_walk):
                if ind != self.cur_walk:
                    x = self.__dict__[f'slave{ind}']
                    y = parameter[shape:shape + x.shape[0]]
                    shape += x.shape[0]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(self.grid[::round(-2*(ind % 2 - 0.5))][round(ind % 2):]))
                else:
                    x = self.__dict__[f'slave{ind}']
                    y = parameter[shape:]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(self.grid[::round(-2*(ind % 2 - 0.5))][round(ind % 2):]))
        else:
            for ind, sub in enumerate(self.reference_slave):
                if ind != self.cur_walk:
                    x = self.__dict__[f'slave{ind}']
                    y = parameter[shape:shape + x.shape[0]]
                    shape += x.shape[0]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(sub))
                else:
                    x = self.__dict__[f'slave{ind}']
                    y = parameter[shape:]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(sub))
                
        return np.concatenate(res)
          
    def check_sizes(self):
        
        def stack(parameter):
            self.__dict__[f'map_{parameter}'] = np.hstack([self.__dict__[f'map_{parameter}'], np.array([np.nan * np.ones(self.__dict__[f'map_{parameter}'].shape[0])]).T])
        
        dif = self.slave.shape[0] - self.map_slave.shape[1]
        
        if dif > 0: #current measurment has more points than the previous:
            for i in range(dif):
                self.map_slave = np.hstack([self.map_slave, np.array([np.nan * np.ones(self.map_slave.shape[0])]).T])
                self.map_master = np.hstack([self.map_master, np.array([np.nan * np.ones(self.map_master.shape[0])]).T])
                for parameter in self.parameters_to_read:
                    stack(parameter)
                    
        if dif < 0: #current measurment has less points than the previous
            for i in range(abs(dif)):
                self.slave = np.concatenate((self.slave, [np.nan]))
                for parameter in self.parameters_to_read:
                    self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [np.nan]))
    
    def clear_slave(self):
        self.slave = np.array([])
        
    def clear_parameters(self):
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])
            
    def append_line_to_file(self, parameter: str, value):
        
        def parameter_to_filename(parameter):
            
            parameter = parameter.replace(':', '')
            path = os.path.normpath(self.filename_sweep).split(os.path.sep)
            name = path[-1]
            try:
                name = name[:len(name) - name[::-1].index('.') - 1]
            except ValueError:
                pass
            name = unify_filename(name)
            name = name[:(len(name) - name[::-1].find('-') - 1)]
            cur_dir = os.path.join(*path[:path.index('data_files')])
            cur_dir = fix_unicode(cur_dir)
            filename = f'{self.index_filename}_{parameter}_map.csv'
            filename = os.path.join(cur_dir, '2d_maps', 'tables', f'{name}_{self.index_filename}', f'{filename}')
            filename = fix_unicode(filename)
            return filename
        
        filename = parameter_to_filename(parameter)
        line = np.concatenate(([self.master[-1]], value))
        line = ','.join(map(str, line))
        with open(filename, 'a') as file:
            try:
                file.write(f'\n{line}')
            except:
                file.close()
            finally:
                file.close()
                
        save_map(filename)
            
    def create_files(self):
        
        path = os.path.normpath(self.filename_sweep).split(os.path.sep)
        name = path[-1]
        try:
            name = name[:len(name) - name[::-1].index('.') - 1]
        except ValueError:
            pass
        name = unify_filename(name)
        name = name[:(len(name) - name[::-1].find('-') - 1)]
        cur_dir = os.path.join(*path[:path.index('data_files')])
        cur_dir = fix_unicode(cur_dir)
        to_make = os.path.join(cur_dir, '2d_maps', 'tables', f'{name}_{self.index_filename}')
        
        if not os.path.exists(to_make):
            os.makedirs(to_make)
        for parameter in self.parameters_to_read:
            slave = np.concatenate(([f'{self.parameter_to_sweep1} / {self.parameter_to_sweep2}'], self.map_slave[0, :]))
            slave = ','.join(map(str, slave))
            parameter = parameter.replace(':', '')
            filename = os.path.join(to_make, f'{self.index_filename}_{parameter}_map.csv')
            fix_unicode(filename)
            
            with open(filename, 'w') as file:
                try:
                    file.write(f'{slave}')
                except:
                    file.close()
                finally:
                    file.close()
        
class mapper3D():
    def __init__(self, parameter_to_sweep1: str, parameter_to_sweep2: str, parameter_to_sweep3: str, 
                 parameters_to_read, filename_sweep: str, _from: float, _to: float, 
                 nsteps: int, walks: int, index_filename: str, 
                 interpolated = True, uniform = True):
        self.slave_slave = np.array([])
        self.slave = np.array([])
        self.master = np.array([])
        self.parameters_to_read = parameters_to_read
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.parameter_to_sweep3 = parameter_to_sweep3
        self.filename_sweep = filename_sweep
        self._from = _from
        self._to = _to
        self.nsteps = nsteps
        self.walks = walks
        self.interpolated = interpolated
        self.uniform = uniform
        self.iteration = 0
        self.cur_walk = 0
        self.index_filename = index_filename
        self.grid = np.linspace(_from, _to, nsteps)
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])

    def append_slave_slave(self, value):
        if not hasattr(self, f'slave_slave{self.cur_walk}'):
            self.__dict__[f'slave_slave{self.cur_walk}'] = np.array([value])
        else:
            self.__dict__[f'slave_slave{self.cur_walk}'] = np.concatenate((self.__dict__[f'slave_slave{self.cur_walk}'], [value]))
    
    def append_slave(self, value):
        self.slave = np.concatenate((self.slave, [value]))
    
    def append_master(self, value):
        self.master = np.concatenate((self.master, [value]))
        
    def append_parameter(self, parameter: str, value):
        if hasattr(self, parameter):
            self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [value]))
    
    def add_sub_slave_slave(self):
        self.cur_walk += 1
            
    def slave_slave_done_walking(self):
        self.slave_slave = np.array([])
        for i in range(self.cur_walk):
            self.slave_slave = np.concatenate((self.slave_slave, self.__dict__[f'slave_slave{i}']))
            
    def clear_sub_slave_slaves(self):
        for i in range(self.cur_walk):
            del self.__dict__[f'slave_slave{i}']
        
        self.cur_walk = 0
    
    def concatenate_all(self):
        
        if not self.interpolated: #raw data
            
            if not hasattr(self, 'map_slave_slave') and not hasattr(self, 'map_slave'):  #first time
                print('Mapper concatenated at first time')
                self.map_slave_slave = np.array([self.slave_slave])
                self.map_slave = np.array([np.ones_like(self.slave_slave) * self.slave[-1]])
                self.create_files()
            
            elif hasattr(self, 'map_slave_slave') and hasattr(self, 'map_slave'):
                print('Mapper concatenated')
                self.check_sizes()
                self.map_slave_slave = np.vstack([self.map_slave_slave, self.slave_slave])
                self.map_slave = np.vstack([self.map_slave, np.ones_like(self.slave_slave) * self.slave[-1]])
                
            else:
                raise Exception(f'Map_slave_slave status {hasattr(self, "map_slave_slave")}, Map_slave status {hasattr(self, "map_slave")}')
        
            self.concatenate_parameters()
            
        else: #interpolated
            
            if not hasattr(self, 'map_slave_slave') and not hasattr(self, 'map_slave'):  #first time
                print('Mapper concatenated at first time')
                if self.uniform == True:
                    grid = []
                    for walk in range(self.walks):
                        grid = np.concatenate((grid, self.grid[::round(-2*(walk % 2 - 0.5))][round(walk % 2):]))
                    self.map_slave_slave = np.array([grid])
                    self.map_slave = np.array([np.ones_like(grid) * self.slave[-1]]) 
                else:
                    self.reference_slave_slave = []
                    for i in range(self.cur_walk):
                        self.reference_slave_slave.append(self.__dict__[f'slave_slave{i}'])
                    self.map_slave_slave = np.array([self.slave_slave])
                    self.map_slave = np.array([np.ones_like(self.slave_slave) * self.slave[-1]]) 
                self.create_files()
                
            elif hasattr(self, 'map_slave_slave') and hasattr(self, 'map_slave'):
                print('Mapper concatenated')
                if self.uniform:
                    grid = []
                    for walk in range(self.walks):
                        grid = np.concatenate((grid, self.grid[::round(-2*(walk % 2 - 0.5))][round(walk % 2):]))
                    self.map_slave_slave = np.vstack([self.map_slave_slave, grid])
                    self.map_slave = np.vstack([self.map_slave, np.ones_like(grid) * self.slave[-1]])
                else:
                    slave_slave = np.concatenate(self.reference_slave_slave)
                    self.map_slave_slave = np.vstack([self.map_slave_slave, slave_slave])
                    self.map_slave = np.vstack([self.map_slave, np.ones_like(slave_slave) * self.slave[-1]])
        
            else:
                raise Exception(f'Map_slave_slave status {hasattr(self, "map_slave_slave")}, Map_slave status {hasattr(self, "map_slave")}')
        
            self.concatenate_parameters()
    
    def concatenate_parameters(self):
        
        def concat(parameter):
            if not self.interpolated: #raw
                
                if not hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.array([self.__dict__[parameter]])
                        self.append_line_to_file(parameter, self.__dict__[parameter])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                    
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.__dict__[parameter]])
                        self.append_line_to_file(parameter, self.__dict__[parameter])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
            
            else: #interpolated
                
                if not hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        interpolated_parameter = self.interpolate(self.__dict__[parameter])
                        self.__dict__[f'map_{parameter}'] = np.array([interpolated_parameter])
                        self.append_line_to_file(parameter, interpolated_parameter)
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        interpolated_parameter = self.interpolate(self.__dict__[parameter])
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], interpolated_parameter])
                        self.append_line_to_file(parameter, interpolated_parameter)
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
        
        for parameter in self.parameters_to_read:
            concat(parameter)
          
    def interpolate(self, parameter):
        res = []
        shape = 0
        
        if self.uniform:
            for ind in range(self.cur_walk):
                if ind != self.cur_walk:
                    x = self.__dict__[f'slave_slave{ind}']
                    y = parameter[shape:shape + x.shape[0]]
                    shape += x.shape[0]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(self.grid[::round(-2*(ind % 2 - 0.5))][round(ind % 2):]))
                else:
                    x = self.__dict__[f'slave_slave{ind}']
                    y = parameter[shape:]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(self.grid[::round(-2*(ind % 2 - 0.5))][round(ind % 2):]))
        else:
            for ind, sub in enumerate(self.reference_slave):
                if ind != self.cur_walk:
                    x = self.__dict__[f'slave_slave{ind}']
                    y = parameter[shape:shape + x.shape[0]]
                    shape += x.shape[0]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(sub))
                else:
                    x = self.__dict__[f'slave_slave{ind}']
                    y = parameter[shape:]
                    func = interpolate.interp1d(x, y, kind = 'nearest', fill_value="extrapolate")
                    res.append(func(sub))
                
        return np.concatenate(res)
            
    def check_sizes(self):
        
        def stack(parameter):
            self.__dict__[f'map_{parameter}'] = np.hstack([self.__dict__[f'map_{parameter}'], np.array([np.nan * np.ones(self.__dict__[f'map_{parameter}'].shape[0])]).T])
        
        dif = self.slave_slave.shape[0] - self.map_slave_slave.shape[1]
        
        if dif > 0: #current measurment has more points than the previous:
            for i in range(dif):
                self.map_slave_slave = np.hstack([self.map_slave_slave, np.array([np.nan * np.ones(self.map_slave_slave.shape[0])]).T])
                self.map_slave = np.hstack([self.map_slave, np.array([np.nan * np.ones(self.map_slave.shape[0])]).T])
                for parameter in self.parameters_to_read:
                    stack(parameter)
                    
        if dif < 0: #current measurment has less points than the previous
            for i in range(abs(dif)):
                self.slave_slave = np.concatenate((self.slave_slave, [np.nan]))
                for parameter in self.parameters_to_read:
                    self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [np.nan]))
    
    def clear_slave_slave(self):
        self.slave_slave = np.array([])
        
    def clear_slave(self):
        self.slave = np.array([])
        
    def clear_parameters(self):
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])
            
    def append_line_to_file(self, parameter: str, value):
        
        def parameter_to_filename(parameter):
            
            parameter = parameter.replace(':', '')
            path = os.path.normpath(self.filename_sweep).split(os.path.sep)
            name = path[-1]
            try:
                name = name[:len(name) - name[::-1].index('.') - 1]
            except ValueError:
                pass
            name = unify_filename(name)
            name = name[:(len(name) - name[::-1].find('-') - 1)]
            cur_dir = os.path.join(*path[:path.index('data_files')])
            cur_dir = fix_unicode(cur_dir)
            filename = f'{self.index_filename}_{parameter}_map_{self.iteration}.csv'
            filename = os.path.join(cur_dir, '2d_maps', 'tables', 
                                    f'{name}_{self.index_filename}',
                                    f'{self.parameter_to_sweep1}_{self.master[-1]}', filename)
            filename = fix_unicode(filename)
            return filename
        
        filename = parameter_to_filename(parameter)
        line = np.concatenate(([self.slave[-1]], value))
        line = ','.join(map(str, line))
        with open(filename, 'a') as file:
            try:
                file.write(f'\n{line}')
            except:
                file.close()
            finally:
                file.close()
                
        if hasattr(self, f'min_{parameter}') and hasattr(self, f'max_{parameter}'):
            save_map(filename, min_z = self.__dict__[f'min_{parameter}'], max_z = self.__dict__[f'max_{parameter}'])
        else:
            save_map(filename)
        
    def create_files(self):
        
        path = os.path.normpath(self.filename_sweep).split(os.path.sep)
        name = path[-1]
        try:
            name = name[:len(name) - name[::-1].index('.') - 1]
        except ValueError:
            pass
        name = unify_filename(name)
        name = name[:(len(name) - name[::-1].find('-') - 1)]
        cur_dir = os.path.join(*path[:path.index('data_files')])
        cur_dir = fix_unicode(cur_dir)
        to_make = os.path.join(cur_dir, '2d_maps', 'tables', f'{name}_{self.index_filename}', 
                               f'{self.parameter_to_sweep1}_{self.master[-1]}')
        
        if not os.path.exists(to_make):
            os.makedirs(to_make)
        for parameter in self.parameters_to_read:
            slave_slave = np.concatenate(([f'{self.parameter_to_sweep2} / {self.parameter_to_sweep3}'], self.map_slave_slave[0, :]))
            slave_slave = ','.join(map(str, slave_slave))
            parameter = parameter.replace(':', '')
            filename = os.path.join(to_make, f'{self.index_filename}_{parameter}_map_{self.iteration}.csv')
            
            with open(filename, 'w') as file:
                try:
                    file.write(f'{slave_slave}')
                except:
                    file.close()
                finally:
                    file.close()
    
    def create_gif(self):
        
        path = os.path.normpath(self.filename_sweep).split(os.path.sep)
        name = path[-1]
        try:
            name = name[:len(name) - name[::-1].index('.') - 1]
        except ValueError:
            pass
        name = unify_filename(name)
        name = name[:(len(name) - name[::-1].find('-') - 1)]
        cur_dir = os.path.join(*path[:path.index('data_files')])
        cur_dir = fix_unicode(cur_dir)
        tomake_gif = os.path.join(cur_dir, '2d_maps', 'images', f'{name}_{self.index_filename}', 
                               'gifs')

        tomake_gif = fix_unicode(tomake_gif)

        if not os.path.exists(tomake_gif):
            os.makedirs(tomake_gif)

        path_files = os.path.join(cur_dir, '2d_maps', 'images', f'{name}_{self.index_filename}')
        path_files = fix_unicode(path_files)

        image_files = []
        for (root, dir_names, file_names) in os.walk(path_files):
            for i in file_names:
                if '.png' in i:
                    file = os.path.join(root, i)
                    image_files.append(fix_unicode(file))
            
        for parameter in self.parameters_to_read:
            parameter_files = []
            parameter_idx = []
            for filename in image_files:
                if parameter in filename:
                    parameter_files.append(filename)
                    name = os.path.normpath(filename).split(os.path.sep)[-1]
                    parameter_idx.append(name[:name.index('_')])
            dat = zip(parameter_idx, parameter_files)
            parameter_files = sorted(dat, key = lambda tup: tup[0])
            parameter_files = [i[1] for i in parameter_files]
            parameter_images = [imageio.imread(i, format = 'PNG') for i in parameter_files]
            gif_name = os.path.join(tomake_gif, f'{self.index_filename}_{parameter}_gif.gif')
            gif_name = fix_unicode(gif_name)
            imageio.mimsave(gif_name, parameter_images, fps = 3, loop = 0)
            
           
    def stack_iteration(self):
        for parameter in self.parameters_to_read:
            if not hasattr(self, f'max_{parameter}'):
                self.__dict__[f'max_{parameter}'] = np.nanmax(self.__dict__[f'map_{parameter}'])
                self.__dict__[f'min_{parameter}'] = np.nanmin(self.__dict__[f'map_{parameter}'])
            else:
                if np.nanmax(self.__dict__[f'map_{parameter}']) > self.__dict__[f'max_{parameter}']:
                    self.__dict__[f'max_{parameter}'] = np.nanmax(self.__dict__[f'map_{parameter}'])
                if np.nanmin(self.__dict__[f'map_{parameter}']) < self.__dict__[f'min_{parameter}']:
                    self.__dict__[f'min_{parameter}'] = np.nanmin(self.__dict__[f'map_{parameter}'])
                
            self.__dict__[f'map_{parameter}{self.iteration}'] = self.__dict__[f'map_{parameter}'] #copying a map of parameter into iterated instance
            del self.__dict__[f'map_{parameter}'] #delete the map_paremeter instance
            
        self.__dict__[f'map_slave_slave{self.iteration}'] = self.map_slave_slave #copying a map of slave_slave into iterated instance
        del self.map_slave_slave #delete the map_slave_slave instance
        
        self.__dict__[f'map_slave{self.iteration}'] = self.map_slave #copying a map of slave into iterated instance
        del self.map_slave #delete the map_slave instance
        
        if self.interpolated and not self.uniform:
            del self.reference_slave_slave
        
        self.iteration += 1
