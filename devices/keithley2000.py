from pymeasure.instruments.keithley import Keithley2000

class keithley2000():
    def __init__(self, adress):
        self.adress = adress
        self.meter = Keithley2000(adress)
        
        self.set_options = ['Volt_DC_range', 'Volt_AC_range', 'Curr_DC_range', 'Curr_AC_range',
                            'Res_2W_range', 'Res_4W_range']
        self.get_options = ['Volt_DC', 'Volt_AC', 'Curr_DC', 'Curr_AC', 'Res_2W', 'Res_4W', 'Period',
                            'Frequency', 'Temperature']
        
    def Volt_DC(self):
        self.meter.mode = 'voltage'
        return self.meter.voltage
    
    def Volt_AC(self):
        self.meter.mode = 'voltage ac'
        return self.meter.voltage
    
    def Curr_DC(self):
        self.meter.mode = 'current'
        return self.meter.current
    
    def Curr_AC(self):
        self.meter.mode = 'current ac'
        
    def Res_2W(self):
        self.meter.mode = 'resistance'
        return self.meter.resistance
        
    def Res_4W(self):
        self.meter.mode = 'resistance 4W'
        return self.meter.resistance
    
    def Period(self):
        self.meter.mode = 'PER'
        return self.meter.period
    
    def Frequency(self):
        self.meter.mode = 'FREQ'
        return self.meter.frequency
    
    def set_Volt_DC_range(self, value=1):
        "[0, 1010]"
        
        self.meter.voltage_range = round(float(value), 2)
        
    def set_Volt_AC_range(self, value = 1):
        "[0, 757.5]"
        
        self.meter.voltage_ac_range = round(float(value), 2)
        
    def set_Curr_DC_range(self, value = 1):
        "[0, 3.1]"
        
        self.meter.current_range = round(float(value), 2)
        
    def set_Curr_AC_range(self, value = 1):
        "[0, 3.1]"
        
        self.meter.current_ac_range = round(float(value), 2)
        
        
    def set_Res_2W_range(self, value = 1):
        "[0, 120e6]"
        
        self.meter.resistance_range = round(float(value), 2)
        
    def set_Res_4W_range(self, value = 1):
        "[0, 120e6]"
        
        self.meter.resistance_4W_range = round(float(value), 2)
    
        
        