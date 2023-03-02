import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    # return np.round(np.random.random(1), 1)
    return device.query(command)

class keithley2400():
    
    def __init__(self, adress = 'GPIB0::7::INSTR'):
        self.sm = rm.open_resource(
            adress)
        
        self.sm.write(':SOUR:CLE:AUTO OFF') # auto on/off
        
        self.set_options = ['V', 'I', 'compl_curr', 'V_NPLC', 'I_NPLC', 'R_NPLC']
        
        self.get_options = ['V', 'I', 'R', 'compl_curr', 'V_NPLC', 'I_NPLC', 'R_NPLC', 'line_freq', 'Sdelay', 'TDelay']
        
    def IDN(self):
        return get(self.sm, '*IDN?')
    
    def V(self):
        try:
            answer = get(self.sm, ':MEAS:VOLT?').split(',')[0]
        except ValueError:
            answer = get(self.sm, ':MEAS:VOLT?').split(',')[0]
        return float(answer)
        
    def I(self):
        try:
            answer = get(self.sm, ':MEAS:CURR?').split(',')[1]
        except ValueError:
            answer = get(self.sm, ':MEAS:CURR?').split(',')[1]
        return float(answer)
        
    def R(self):
        try:
            answer = get(self.sm, ':MEAS:RES?').split(',')[2]
        except ValueError:
            answer = get(self.sm, ':MEAS:RES?').split(',')[2]
        return float(answer)

    def set_I_auto_range(self):
        self.sm.write(':SENS:CURR:RANGE:AUTO 1')
        
    def off_I_auto_range(self):
        self.sm.write(':SENS:CURR:RANGE:AUTO 0')
        
    def set_V_auto_range(self):
        self.sm.write(':SENS:VOLT:RANGE:AUTO 1')
        
    def off_V_auto_range(self):
        self.sm.write(':SENS:VOLT:RANGE:AUTO 0')
        
    def set_R_auto_range(self):
        self.sm.write(':SENS:RES:RANGE:AUTO 1')
        
    def off_R_auto_range(self):
        self.sm.write(':SENS:RES:RANGE:AUTO 0')
    
    def set_I(self, value = 0):
        self.sm.write(':SOUR:CURR:MODE FIXED')
        self.sm.write(':SOUR:CURR ' + str(round(float(value), 5))) 
        
    def set_V(self, value = 0, speed = None):
        self.sm.write(':SOUR:VOLT:MODE FIXED')
        self.sm.write(':SOUR:VOLT ' + str(round(float(value), 5))) 
        
    def set_compl_curr(self, value = 0):
        self.sm.write(f':SENS:CURR:PROT {str(round(float(value), 5))}')
        
    def V_NPLC(self):
        return float(get(self.sm, ':SENS:VOLT:NPLC?'))
        
    def set_V_NPLC(self, value = 1):
        self.sm.write(':SENS:VOLT:NPLC ' + str(round(float(value), 2)))
        
    def I_NPLC(self):
        return float(get(self.sm, ':SENS:CURR:NPLC?'))
        
    def set_I_NPLC(self, value = 1):
        self.sm.write(':SENS:CURR:NPLC ' + str(round(float(value), 2)))
        
    def R_NPLC(self):
        return float(get(self.sm, ':SENS:RES:NPLC?'))
        
    def set_R_NPLC(self, value = 1):
        self.sm.write(':SENS:RES:NPLC ' + str(round(float(value), 2)))
        
    def compl_curr(self):
        answer = get(self.sm, ':SENS:CURR:PROT?')
        return answer
        
    def line_freq(self):
        return float(get(self.sm, ':SYST:LFR?'))
    
    def Sdelay(self):
        return float(get(self.sm, ':SOUR:DEL?'))
    
    def Tdelay(self):
        return float(get(self.sm, ':TRIG:DEL?'))
    
def main():
    device = Keithley2400()
    device.set_compl_curr(1e-5)
    print(device.IDN())
    
if __name__ == '__main__':
    main()