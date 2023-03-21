import numpy as np
import numpy.ma as ma

class mapper():
    def __init__(self):
        self.slave = []
        self.master = []
        
        self.map_slave = np.array([[]])
        self.map_master = np.array([[]])

    def append_slave(self, value):
        self.slave.append(value)
        return
    
    def append_master(self, value):
        self.master.append(value)
        return
    
    def mesh(self, master, slave):
        return
    
    def interpolate_slave(self):
        return
    
    def rescale_slave(self):
        return
        