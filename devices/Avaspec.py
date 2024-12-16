"""
Example showing how to communicate with an AvaSpec-2048L spectrometer.
"""
import time

# if matplotlib is available then plot the data
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)

class Avaspec():
    def __init__(self, adress):
        
        serial = '1801230U1'
        
        record = EquipmentRecord(
            manufacturer='Avantes',
            model='AvaSpec-2048L',  # update for your device
            serial=serial,
            connection=ConnectionRecord(
                address='SDK::C:/AvaSpecX64-DLL_9.14.0.0/avaspecx64.dll',  # update the path to the DLL file
                backend=Backend.MSL,
            )
        )
        
        self.device = record.connect()
        self.use_high_res_adc(False)
        
        self._dark_data = None
        
        num_pixels = self.num_pixels()
        cfg = self.device.MeasConfigType()
        cfg.m_StopPixel = num_pixels - 1
        cfg.m_IntegrationTime = 5  # in milliseconds
        cfg.m_NrAverages = 1  # number of averages
        self.device.prepare_measure(cfg)
        
        self.set_options = ['integration_time', 'n_average']
        self.get_options = ['num_pixels', 'integration_time', 'n_average', 'wavelength', 'data', 'dark_data']
        
        self.sweepable = ['False', 'False']
        self.maxspeed = [None, None]
        
    def num_pixels(self):
        ans = self.device.get_num_pixels()
        return ans
    
    def integration_time(self):
        cfg = self.device.MeasConfigType()
        ans = cfg.m_IntegrationTime
        return ans
    
    def n_average(self):
        cfg = self.device.MeasConfigType()
        ans = cfg.m_NrAverages
        return ans
    
    def wavelength(self):
        ans = self.device.get_lambda()
        return ans
    
    def data(self):
        # start 1 measurement, wait until the measurement is finished, then get the data
        self.device.measure(1)
        while not self.device.poll_scan():
            time.sleep(0.01)
        _, data = self.device.get_data()
        
        self._dark_data = self.device.get_dark_pixel_data()
        
    def dark_data(self):
        return self._dark_data
    
    def set_integration_time(self, value: float, speed: float = None):
        cfg = self.device.MeasConfigType()
        cfg.m_IntegrationTime = value  # in milliseconds
        self.device.prepare_measure(cfg)
        
    def set_n_average(self, value: int, speed: float = None):
        cfg = self.device.MeasConfigType()
        cfg.m_NrAverages = value
        self.device.prepare_measure(cfg)
        