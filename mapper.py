import numpy as np

class mapper():
    def __init__(self, parameters_to_read, from_slave: float, to_slave: float, num: int):
        self.slave = np.array([])
        self.master = np.array([])
        self.from_slave = from_slave
        self.to_slave = to_slave
        self.num = num
        self.scattered_slave = np.linspace(self.from_slave, self.to_slave, 100)
        self.parameters_to_read = parameters_to_read
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])

    def append_slave(self, value):
        self.slave = np.concatenate((self.slave, [value]))
    
    def append_master(self, value):
        self.master = np.concatenate((self.master, [value]))
        
    def append_parameter(self, parameter: str, value):
        if hasattr(self, parameter):
            self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [value]))
    
    def concatenate_all(self):
        
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
    
    def concatenate_parameters(self):
        
        def concat(parameter):
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
        
        for parameter in self.parameters_to_read:
            concat(parameter)
            
    def check_sizes(self):
        
        def stack(parameter):
            self.__dict__[f'map_{parameter}'] = np.hstack([self.__dict__[f'map_{parameter}'], np.nan * np.ones(self.__dict__[f'map_{parameter}'].shape[0])])
        
        args = np.argsort(self.slave)
        if self.to_slave < self.from_slave:
            args = args[::-1]
        self.slave = self.slave[args]
        
        dif = self.slave.shape[0] - self.map_slave.shape[1]
        
        if dif > 0: #current measurment has more points than the previous:
            for i in range(dif):
                self.map_slave = np.hstack([self.map_slave, np.nan * np.ones(self.map_slave.shape[0])])
                self.map_master = np.hstack([self.map_master, np.nan * np.ones(self.map_master.shape[0])])
                for parameter in self.parameters_to_read:
                    stack(parameter)
                    
        if dif < 0: #current measurment has less points than the previous
            for i in range(abs(dif)):
                self.slave = np.concatenate((self.slave, [np.nan]))
                for parameter in self.parameters_to_read:
                    self.__dict__[parameter] = self.__dict__[parameter][args]
                    self.__dict__[parameter] = np.concatenate((self.__dict__[parameter], [np.nan]))
    
    def clear_slave(self):
        self.slave = np.array([])
        
    def clear_parameters(self):
        for parameter in self.parameters_to_read:
            self.__dict__[parameter] = np.array([])
