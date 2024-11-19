# -*- coding: utf-8 -*-
"""

@author: DbIXAHUEOKEAHA
"""

import numpy as np
from atto_device.atto_device import AMC
from atto_device.atto_device.AMC.ACS import AttoException

class amc():
    def __init__(self, adress: str = "192.168.1.4"):
        self.device = AMC(adress)
        self.device.connect()
        
        self.set_options = ['gnd_1', 'gnd_2', 'gnd_3', 'step_up_1', 'step_down_1', 'step_up_2', 'step_down_2',
                            'step_up_3', 'step_down_3', 'volt_1', 'volt_2', 'volt_3', 'freq_1', 'freeq_2',
                            'freq_3', 'ampl_1', 'amplt_2', 'ampl_3', 'outp_active1', 'outp_active_2', 
                            'outp_active_3']
        self.get_options = ['position_1', 'position_2', 'position_3','gnd_1', 'gnd_2', 'gnd_3', 
                            'volt_1', 'volt_2', 'volt_3', 'freq_1', 'freq_2', 'freq_3', 
                            'outp_active_1', 'outp_active_2', 'outp_active_3']
        
        self.sweepable = []
        
        for i in self.set_options:
            self.sweepable.append(None)
        
        for i in range(3):
            self.__dict__[f'position_{i+1}'] = lambda: self.position(i+1)
            self.__dict__[f'gnd_{i+1}'] = lambda: self.gnd(i+1)
            self.__dict__[f'volt_{i+1}'] = lambda: self.volt(i+1)
            self.__dict__[f'freq_{i+1}'] = lambda: self.freq(i+1)
            self.__dict__[f'ampl_{i+1}'] = lambda: self.ampl(i+1)
            self.__dict__[f'outp_active_{i+1}'] = lambda: self.outp_active(i+1)
            self.__dict__[f'set_gnd_{i+1}'] = lambda value: self.set_gnd(i+1, value)
            self.__dict__[f'set_step_up_{i+1}'] = lambda value: self.set_step_up(i+1, value)
            self.__dict__[f'set_step_down_{i+1}'] = lambda value: self.set_step_down(i+1, value)
            self.__dict__[f'set_volt_{i+1}'] = lambda value: self.set_volt(i+1, value)
            self.__dict__[f'set_freq_{i+1}'] = lambda value: self.set_freq(i+1, value)
            self.__dict__[f'set_ampl_{i+1}'] = lambda value: self.set_ampl(i+1, value)
            self.__dict__[f'set_outp_active_{i+1}'] = lambda value: self.outp_active(i+1, value)
            
        
    def get_nan_answer(self, func):
        try:
            answer = func()
        except AttoException:
            answer = np.nan
        return answer
        
    def description(self):
        answer = self.get_nan_answer(self.device.description.getDeviceType)
        return answer
    
    def position(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.control.getPosition(axis))
        return answer
    
    def gnd(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.move.getGroundAxis(axis))
        return answer
    
    def volt(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.control.getCurrentOutputVoltage(axis))
        return answer
    
    def freq(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.control.getControlFrequency(axis))
        return answer
    
    def ampl(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.control.getControlAmplitude(axis))
        return answer
    
    def outp_active(self, axis: int):
        answer = self.get_nan_answer(lambda: self.device.control.getControlOutput(axis))
        return answer
    
    def set_gnd(self, axis: int, value: bool):
        '''

        Parameters
        ----------
        axis : int
            Axis count number (int).
        value : bool
            True: Enable ground
            False: Disable ground

        Returns
        -------
        None.

        '''
        self.device.move.setGroundAxis(axis, value)
    
    def set_step_up(self, axis: int, value: int):
        self.device.move.setNSteps(axis, False, value)
        
    def set_step_down(self, axis: int, value: int):
        self.device.move.setNSteps(axis, True, value)
        
    def set_volt(self, axis: int, value: int):
        self.device.control.setCurrentOutputVoltage(axis, value)
    
    def set_freq(self, axis: int, value: int):
        self.device.control.setControlFrequency(axis, value)
    
    def set_ampl(self, axis: int, value: int):
        self.device.control.setControlAmplitude(axis, value)
    
    def set_outp_active(self, axis: int, value: bool):
        self.device.control.getControlOutput(axis, value)
    
    def close(self):
        self.device.disconnect()
    
def main():
    try:
        device = amc('192.168.1.3')
        print(device.Volt1())
    except Exception as ex:
        print(ex)
        
if __name__ == '__main__':
    main()