# -*- coding: utf-8 -*-
"""

@author: DbIXAHUEOKEAHA
"""

import numpy as np
from matplotlib import pyplot as plt
from ASC500.lib import ASC500
import time

if __name__ == '__main__':
    binPath = "ASC500\\Installer\\ASC500CL-V2.7.13\\"
    dllPath = "ASC500\\64bit_lib\\ASC500CL-LIB-WIN64-V2.7.13\\daisybase\\lib\\"
else:
    binPath = "devices\\ASC500\\Installer\\ASC500CL-V2.7.13\\"
    dllPath = "devices\\ASC500\\64bit_lib\\ASC500CL-LIB-WIN64-V2.7.13\\daisybase\\lib\\"
    
class asc500():
    def __init__(self, adress = 'COM3'):
        
        self.device = ASC500(binPath, dllPath)
        self.device.base.startServer()
        
        self.get_options = ['gnd_x', 'gnd_y', 'gnd_z', 'volt_x', 'volt_y', 'volt_z', 'freq_x', 'freq_y', 'freq_z']
        self.set_options = ['gnd_x', 'gnd_y', 'gnd_z', 'step_up_x', 'step_up_y', 'step_up_z', 'step_down_x', 
                            'step_down_y', 'step_down_z', 'volt_x', 'volt_y', 'volt_z', 'freq_x', 'freq_y', 'freq_z']
        
        self.set_freq_x(400)
        self.set_freq_y(400)
        self.set_freq_z(40)
        
        self.set_volt_x(35)
        self.set_volt_y(35)
        self.set_volt_z(35)
        
        self.sweepable = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        
    def gnd_x(self) -> bool:
        """
        Returns mode of x-axis
        -------
        bool
        
        True = grounded
        False = ungrounded
        """
        axis = 4
        mode = self.device.coarse.getCoarseAxisMode(axis)
        if mode == 1:
            ans = False
        else:
            ans = True
        return ans
    
    def gnd_y(self) -> bool:
        """
        Returns mode of y-axis
        -------
        bool
        
        True = grounded
        False = ungrounded
        """
        axis = 5
        mode = self.device.coarse.getCoarseAxisMode(axis)
        if mode == 1:
            ans = False
        else:
            ans = True
        return ans
    
    def gnd_z(self) -> bool:
        """
        Returns mode of z-axis
        -------
        bool
        
        True = grounded
        False = ungrounded
        """
        axis = 6
        mode = self.device.coarse.getCoarseAxisMode(axis)
        if mode == 1:
            ans = False
        else:
            ans = True
        return ans
    
    def set_gnd_x(self, value):
        """
        If value == 1 or False: set x-axis ungrounded
        If value == 2 or True: set x-axis grounded
        
        Returns
        -------
        None.
        """
        axis = 4
        if value == 1 or value == False:
            set_mode = 1
        else:
            set_mode = 2
        self.device.coarse.setCoarseAxisMode(axis, set_mode)
        
    def set_gnd_y(self, value):
        """
        If value == 1 or False: set y-axis ungrounded
        If value == 2 or True: set y-axis grounded
        
        Returns
        -------
        None.
        """
        axis = 5
        if value == 1 or value == False:
            set_mode = 1
        else:
            set_mode = 2
        self.device.coarse.setCoarseAxisMode(axis, set_mode)
        
    def set_gnd_z(self, value):
        """
        If value == 1 or False: set z-axis ungrounded
        If value == 2 or True: set z-axis grounded
        
        Returns
        -------
        None.
        """
        axis = 6
        if value == 1 or value == False:
            set_mode = 1
        else:
            set_mode = 2
        self.device.coarse.setCoarseAxisMode(axis, set_mode)
    
    def set_steps_up_x(self, value: int = 1):
        """
        Makes 'value' number of steps up along x-axis
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 4
        self.device.coarse.stepCoarseUp(axis, value)
        
    def set_steps_down_x(self, value: int = 1):
        """
        Makes 'value' number of steps down along x-axis 
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 4
        self.device.coarse.stepCoarseDown(axis, value)
        
    def set_steps_up_y(self, value: int = 1):
        """
        Makes 'value' number of steps up along y-axis
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 5
        self.device.coarse.stepCoarseUp(axis, value)
        
    def set_steps_down_y(self, value: int = 1):
        """
        Makes 'value' number of steps down along y-axis 
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 5
        self.device.coarse.stepCoarseDown(axis, value)
        
    def set_steps_up_z(self, value: int = 1):
        """
        Makes 'value' number of steps up along z-axis
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 6
        self.device.coarse.stepCoarseUp(axis, value)
        
    def set_steps_down_z(self, value: int = 1):
        """
        Makes 'value' number of steps down along z-axis 
        
        Returns
        -------
        None.
        """
        
        try:
            value = int(value)
        except ValueError:
            value = 1
        
        axis = 4
        self.device.coarse.stepCoarseDown(axis, value)
        
    def volt_x(self):
        """
        Returns
        -------
        float: Voltage on x-axis

        """
        axis = 4
        ans = self.device.coarse.getCoarseVoltage(axis)
        return ans
    
    def volt_y(self):
        """
        Returns
        -------
        float: Voltage on y-axis

        """
        axis = 5
        ans = self.device.coarse.getCoarseVoltage(axis)
        return ans
    
    def volt_z(self):
        """
        Returns
        -------
        float: Voltage on z-axis

        """
        axis = 6
        ans = self.device.coarse.getCoarseVoltage(axis)
        return ans
    
    def set_volt_x(self, value):
        """
        set voltage on x-axis
        Returns
        -------
        None.

        """
        axis = 4
        self.device.coarse.setCoarseVoltage(axis, value)
        
    def set_volt_y(self, value):
        """
        set voltage on y-axis
        Returns
        -------
        None.

        """
        axis = 5
        self.device.coarse.setCoarseVoltage(axis, value)
        
    def set_volt_z(self, value):
        """
        set voltage on z-axis
        Returns
        -------
        None.

        """
        axis = 6
        self.device.coarse.setCoarseVoltage(axis, value)
        
    def freq_x(self):
        """
        Returns
        -------
        float: Frequency on x-axis

        """
        axis = 4
        ans = self.device.coarse.getCoarseFrequency(axis)
        return ans
    
    def freq_y(self):
        """
        Returns
        -------
        float: Frequency on y-axis

        """
        axis = 5
        ans = self.device.coarse.getCoarseFrequency(axis)
        return ans
    
    def freq_z(self):
        """
        Returns
        -------
        float: Frequency on z-axis

        """
        axis = 6
        ans = self.device.coarse.getCoarseFrequency(axis)
        return ans
    
    def set_freq_x(self, value):
        """
        set Frequency on x-axis
        Returns
        -------
        None.

        """
        axis = 4
        self.device.coarse.setCoarseFrequency(axis, value)
        
    def set_freq_y(self, value):
        """
        set Frequency on y-axis
        Returns
        -------
        None.

        """
        axis = 5
        self.device.coarse.setCoarseFrequency(axis, value)
        
    def set_freq_z(self, value):
        """
        set Frequency on z-axis
        Returns
        -------
        None.

        """
        axis = 6
        self.device.coarse.setCoarseFrequency(axis, value)
    
    def close(self):
        #self.device.base.stopServer()
        pass

def main():
    device = ASC500(binPath, dllPath)
    device.base.startServer()
    axis = 6
    device.coarse.setCoarseAxisMode(axis, 1)
    print(device.coarse.getCoarseAxisMode(axis))
    #device.base.stopServer()
    #device.base.startServer()
    #device.base.stopServer()
    
        
        
if __name__ == '__main__':
    main()
