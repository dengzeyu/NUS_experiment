# -*- coding: utf-8 -*-
"""

@author: DbIXAHUEOKEAHA
"""

import numpy as np
from atto_device.atto_device import CRYO2100
from atto_device.atto_device.CRYO2100.ACS import AttoException

class ADry2100():
    def __init__(self, adress: str = "192.168.1.1"):
        self.device = CRYO2100(adress)
        self.device.connect()
        
        self.vti_ramp_rate = 10 #Default speed
        self.sample_ramp_rate = 10 #Default speed
        
        self.max_By = 2 #Tesla
        self.max_Bz = 6 #Tesla
        self.max_Bx = 0 #Tesla
        
        self.max_B = 3 #Field vector module max value
        
        self.set_options = ['T_VTI', 'T_sam', 'By', 'Bz', 'Btheta', 'VTI_ramp_rate', 'Sample_ramp_rate']
        self.get_options = ['T_VTI', 'T_sam', 'T_mag', 'By', 'Bz', 'Btheta', 'VTI_ramp_rate', 'Sample_ramp_rate']
        
        self.sweepable = [False, False, False, False, False, False, False]
        self.maxspeed = [None, None, None, None, None, None, None]
        self.eps = [0.02, 0.02, 0.001, 0.001, 0.1, None, None]
        
    def get_nan_answer(self, func):
        try:
            answer = func()
        except AttoException:
            answer = np.nan
        return answer
        
    def T_VTI(self):
        answer = self.get_nan_answer(self.device.vti.getTemperature)
        return answer
    
    def T_sam(self):
        answer = self.get_nan_answer(self.device.sample.getTemperature)
        return answer
    
    def T_mag(self):
        answer = self.get_nan_answer(self.device.magnet.getTemperature)
        return answer
    
    def VTI_ramp_rate(self): #Ramp rate in Kelvin / minute [0.1-100]
        answer = self.get_nan_answer(self.device.vti.getRampRate)
        return answer
    
    def set_T_VTI(self, value, speed = None):
        self.device.vti.setSetPoint(value)
        max_speed = self.maxspeed[self.set_options.index('T_VTI')]
        if max_speed == None:
            vti_ramp_rate = self.VTI_ramp_rate()
            if np.isnan(vti_ramp_rate):
                vti_ramp_rate = self.vti_ramp_rate
        else:
            if speed == 'SetGet':
                vti_ramp_rate = max_speed
            else:
                vti_ramp_rate = min(max_speed, np.abs(speed))
        self.device.vti.setRampRate(vti_ramp_rate)
        self.device.vti.startRampControl()
        self.device.vti.startTempControl()
        
    def Sample_ramp_rate(self): #Ramp rate in Kelvin / minute [0.1-100]
        answer = self.get_nan_answer(self.device.sample.getRampRate)
        return answer
    
    def set_T_Sam(self, value, speed = None):
        self.device.sample.setSetPoint(value)
        max_speed = self.maxspeed[self.set_options.index('T_Sam')]
        if max_speed == None:
            sample_ramp_rate = self.Sample_ramp_rate()
            if np.isnan(sample_ramp_rate):
                sample_ramp_rate = self.sample_ramp_rate
        else:
            if speed == 'SetGet':
                sample_ramp_rate = max_speed
            else:
                sample_ramp_rate = min(max_speed, np.abs(speed))
        self.device.sample.setRampRate(sample_ramp_rate)
        self.device.sample.startRampControl()
        self.device.sample.startTempControl()
        
    
    def B(self):
        answer = self.get_nan_answer(self.device.magnet.getHSetPoint3D)
        if np.isnan(answer).any():
            answer = (np.nan, np.nan, np.nan. np.nan)
        return answer
            
    def Bx(self):
        return self.B()[2]
    
    def By(self):
        return self.B()[1]
    
    def Bz(self):
        return self.B()[0]
    
    def Btheta(self):
        Bz, By, Bx = self.B()
        if np.isnan(Bz) or np.isnan(By):
            return np.nan
        else:
            return (np.arctan2(Bz, By)) / (2 * np.pi) * 360
    
    def set_By(self, value):
        Bz, By, Bx = self.B()
        if np.isnan(Bz) or np.isnan(By):
            return 
        
        #if other components are non-zero
        if np.abs(Bz) < np.eps[self.set_options.index('Bz')]: #or np.abs(Bx) < np.eps[self.set_options.index('Bx')]:
            By = min(self.max_By, value)
        else:
            if np.sqrt(Bz**2 + value**2 + Bx**2) < np.abs(self.max_B):
                By = value
            else:
                if value < 0:
                    sign = - 1
                else:
                    sign = 1
                By = sign * np.sqrt(self.max_B**2 - Bz**2 - Bx**2)
        
        self.device.magnet.setHSetPoint3D(Bz, By, Bx)
        
    def set_Bz(self, value):
        Bz, By, Bx = self.B()
        if np.isnan(Bz) or np.isnan(By):
            return 
        
        #if other components are non-zero
        if np.abs(By) < np.eps[self.set_options.index('By')]: #or np.abs(Bx) < np.eps[self.set_options.index('Bx')]:
            Bz = min(self.max_Bz, value)
        else:
            if np.sqrt(By**2 + value**2 + Bx**2) < np.abs(self.max_B):
                Bz = value
            else:
                if value < 0:
                    sign = - 1
                else:
                    sign = 1
                Bz = sign * np.sqrt(self.max_B**2 - By**2 - Bx**2)
        
        self.device.magnet.setHSetPoint3D(Bz, By, Bx)
    
    def set_Btheta(self, value):
        """

        Parameters
        ----------
        value : int
            Angle between (Bz, By) in degrees. Consider Bz along vertical axis, By along horizontal axis.
        Returns
        -------
        None.

        """
        Bz, By, Bx = self.B()
        if np.isnan(Bz) or np.isnan(By):
            return 
        else:
            B = np.sqrt(Bx**2 + By**2 + Bz**2)
            Bz = B * np.sin(value)
            Bx = B * np.cos(value)
        
        self.device.magnet.setHSetPoint3D(Bz, By, Bx)
    
    
    
def main():
    device = ADry2100("192.168.1.1")
    print(device.B())
    
if __name__ == '__main__':
    main()