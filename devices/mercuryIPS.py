import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    return device.query(command)
    #return np.random.random(1)
    
class mercuryIPS():
    def __init__(self, adress):
        self.device = rm.open_resource(adress)
        self.get_options = ['field', 'current', 'field_rate', 'current_rate', 'T']
        self.set_options = ['field', 'current', 'field_rate', 'current_rate']
        self.sweepable = [True, True, False, False]
        self.maxspeed = [0.0357, 0.01, None, None]
        
    def field(self):
        answer = get(self.device, 'READ:DEV:GRPZ :PSU:SIG:FLD')
        return answer        
        
    def current(self):
        answer = get(self.device, 'READ:DEV:GRPZ :PSU:SIG:CURR')
        return answer
    
    def field_rate(self):
        answer = get(self.device, 'READ:DEV:GRPZ :PSU:SIG:RFLD')
        return answer  
    
    def current_rate(self):
        answer = get(self.device, 'READ:DEV:GRPZ :PSU:SIG:RCUR')
        return answer
    
    def T(self):
        answer = get(self.device, 'READ:DEV:MB1.T1 :TEMP:SIG:TEMP')
        return answer
        
    def set_field(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('field')])
        if speed > maxspeed:
            speed = maxspeed
        if speed == None:
            self.set_field_rate(maxspeed)
            self.device.write(f'SET:DEV:GRPZ :PSU:SIG:FSET:{round(float(value), 3)}')
        else:
            self.set_field_rate(speed)
            self.device.write(f'SET:DEV:GRPZ :PSU:SIG:FSET:{round(float(value), 3)}')
            
    def set_current(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('current')])
        if speed > maxspeed:
            speed = maxspeed
        if speed == None:
            self.set_field_rate(maxspeed)
            self.device.write(f'SET:DEV:GRPZ :PSU:SIG:CSET:{round(float(value), 3)}')
        else:
            self.set_field_rate(speed)
            self.device.write(f'SET:DEV:GRPZ :PSU:SIG:CSET:{round(float(value), 3)}')
            
    def set_field_rate(self, value):
        self.device.write(f'SET:DEV:GRPZ :PSU:SIG:RFST:{round(float(value), 3)}')
        
    def set_current_rate(self, value):
        self.device.write(f'SET:DEV:GRPZ :PSU:SIG:RCST:{round(float(value), 3)}')
        
    
    
    
        
        