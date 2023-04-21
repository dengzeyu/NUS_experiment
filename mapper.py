import numpy as np
import os
import itertools
from scipy import interpolate

"""
A classes that helps to collect data from 2D and 3D sweeps
"""

class mapper2D():
    def __init__(self, parameter_to_sweep1: str, parameter_to_sweep2: str, 
                 parameters_to_read, cur_dir: str, _from: float, _to: float, 
                 nsteps: int, walks: int, interpolated = False, uniform = True):
        self.slave = np.array([])
        self.master = np.array([])
        self.parameters_to_read = parameters_to_read
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.cur_dir = cur_dir
        self._from = _from
        self._to = _to
        self.nsteps = nsteps
        self.walks = walks
        self.interpolated = interpolated
        self.uniform = uniform
        self.grid = np.linspace(_from, _to, nsteps)
        self.cur_walk = 0
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])

    def append_slave(self, value):
        if not hasattr(self, f'slave{self.cur_walk}'):
            self.__dict__[f'slave{self.cur_walk}'] = np.array([])
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
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                    
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.__dict__[parameter]])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
            
            else: #interpolated
                
                if not hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.array([self.interpolate(self.__dict__[parameter])])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.interpolate(self.__dict__[parameter])])
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
            
    def create_files(self, filename):
        
        filename = os.path.basename(filename)[:-4]
        filename = filename[(len(filename) - filename[::-1].find('-')):]
        
        if not os.path.exists(os.path.join(os.path.dirname(self.cur_dir), '2d_maps')):
            os.mkdir(os.path.join(os.path.dirname(self.cur_dir), '2d_maps'))
        for parameter in self.parameters_to_read:
            content = np.hstack((np.array([self.map_master[:, 0]]).T, self.__dict__[f'map_{parameter}']))
            slave = np.concatenate(([f'{self.parameter_to_sweep1} / {self.parameter_to_sweep2}'], self.map_slave[0, :]))
            content = np.vstack((np.array([slave]), content))
            parameter = parameter.replace(':', '')
            np.savetxt(os.path.join(os.path.dirname(self.cur_dir), '2d_maps', f'{os.path.basename(filename)}_{parameter}_map.csv'), content, fmt="%s", delimiter=',')
            
        print(f'2D maps are saved into {os.path.join(os.path.dirname(self.cur_dir), "2d_maps")} folder')

class mapper3D():
    def __init__(self, parameter_to_sweep1: str, parameter_to_sweep2: str, parameter_to_sweep3: str, 
                 parameters_to_read, cur_dir: str, _from: float, _to: float, 
                 nsteps: int, walks: int, interpolated = False, uniform = True):
        self.slave_slave = np.array([])
        self.slave = np.array([])
        self.master = np.array([])
        self.parameters_to_read = parameters_to_read
        self.parameter_to_sweep1 = parameter_to_sweep1
        self.parameter_to_sweep2 = parameter_to_sweep2
        self.parameter_to_sweep3 = parameter_to_sweep3
        self.cur_dir = cur_dir
        self._from = _from
        self._to = _to
        self.nsteps = nsteps
        self.walks = walks
        self.interpolated = interpolated
        self.uniform = uniform
        self.iteration = 0
        self.cur_walk = 0
        self.grid = np.linspace(_from, _to, nsteps)
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])

    def append_slave_slave(self, value):
        if not hasattr(self, f'slave_slave{self.cur_walk}'):
            self.__dict__[f'slave_slave{self.cur_walk}'] = np.array([])
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
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                    
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.__dict__[parameter]])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
            
            else: #interpolated
                
                if not hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.array([self.interpolate(self.__dict__[parameter])])
                    else:
                        self.__dict__[f'map_{parameter}'] = np.array([[]])
                        
                elif hasattr(self, f'map_{parameter}'):
                    if hasattr(self, parameter):
                        self.__dict__[f'map_{parameter}'] = np.vstack([self.__dict__[f'map_{parameter}'], self.interpolate(self.__dict__[parameter])])
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
