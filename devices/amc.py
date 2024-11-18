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
        
    def get_nan_answer(self, func):
        try:
            answer = func()
        except AttoException:
            answer = np.nan
        return answer
        
    def description(self):
        answer = self.get_nan_answer(self.device.description.getDeviceType)
        return answer
    
    def Volt1(self):
        answer = self.get_nan_answer(lambda: self.device.control.getCurrentOutputVoltage(1))
        return answer
    
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