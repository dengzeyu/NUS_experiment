import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    # return np.round(np.random.random(1), 1)
    return device.query(command)

class SourceMeter():
    
    def __init__(self, adress = 'GPIB0::4::INSTR'):
        self.sm = rm.open_resource(
            adress, write_termination='\n', read_termination='\n')
        
        self.sm.write(':SOUR:CLE:AUTO OFF') # auto on/off
        
        self.set_options = ['V_fix', 'I_fix', 'V_sweap', 'I_sweap', 'V_NPLC', 'I_NPLC', 'R_NPLC']
        self.sweepable = [False, False, True, True, False, False, False]
        self.max_speed = [None, None, 100, 100, None, None, None]
        
        self.get_options = ['V', 'I', 'R', 'V_NPLC', 'I_NPLC', 'R_NPLC']
        
    def IDN(self):
        return get(self.sm, '*IDN?')
    
    def V_fix(self):
        self.V()
        
    def V_sweap(self):
        self.V()
        
    def I_fix(self):
        self.I()
        
    def I_sweap(self):
        self.I()
    
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
    
    def set_I_fix(self, value = 0):
        self.set_I_sweap(value)
        
    def set_V_fix(self, value = 0):
        self.set_V_sweap(value)
        
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
    
    def set_I_sweap(self, value = 0, speed = None):
        if speed == None:
            self.sm.write(':SOUR:CURR:MODE FIXED')
            self.sm.write(':SOUR:CURR ' + str(round(float(value), 5))) 
        else:
            self.sm.write(':SOUR:CURR:MODE SWE')
            self.set_I_auto_range()
            dv = float(value) - float(self.V())
            f = self.freq()
            NPLC = self.I_NPLC()
            self.set_I_speed(speed, dv, f, NPLC)
            self.sm.write(':SOUR:CURR ' + str(round(float(value), 5))) 
        
    def set_V_sweap(self, value = 0, speed = None):
        if speed == None:
            self.sm.write(':SOUR:VOLT:MODE FIXED')
            self.sm.write(':SOUR:VOLT ' + str(round(float(value), 5))) 
        else:
            self.sm.write(':SOUR:VOLT:MODE SWE')
            self.set_V_auto_range()
            dv = float(value) - float(self.V())
            f = self.freq()
            NPLC = self.V_NPLC()
            self.set_V_speed(speed, dv, f, NPLC)
            self.sm.write(':SOUR:VOLT ' + str(round(float(value), 5)))
        
    def set_V_speed(self, value, dv, f, nplc):
        self.sm.write(':SOUR:VOLT:START ' + str(self.V()))
        self.sm.write(':SOUR:VOLT:STOP ' + str(float(dv) + float(self.V())))
        step = value * (self.Sdelay() + self.Tdelay() + self.V_NPLC() / self.freq())
        self.sm.write(':SOUR:VOLT:STEP ' + str(step))
        
    def set_I_speed(self, value, di, f, nplc):
        self.sm.write(':SOUR:CURR:START ' + str(self.I()))
        self.sm.write(':SOUR:CURR:STOP ' + str(float(di) + float(self.I())))
        step = value * (self.Sdelay() + self.Tdelay() + self.I_NPLC() / self.freq())
        self.sm.write(':SOUR:CURR:STEP ' + str(step))
        
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
        
    def freq(self):
        return float(get(self.sm, ':SYST:LFR?'))
    
    def Sdelay(self):
        return float(get(self.sm, ':SOUR:DEL?'))
    
    def Tdelay(self):
        return float(get(self.sm, ':TRIG:DEL?'))