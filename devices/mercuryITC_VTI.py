import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    return device.query(command)
    #return np.random.random(1)
    
class mercuryITC_VTI():
    def __init__(self, adress):
        self.device = rm.open_resource(adress)
        self.get_options = ['T_VTI', 'T_sample', 'Flow_perc_VTI', 'Flow_perc_sample']
        self.set_options = ['T_VTI', 'T_sample', 'T_VTI_rate', 'T_sample_rate']
        self.sweepable = [True, True, False, False]
        self.maxspeed = [20, 20, None, None]
        self.speed_VTI 
        self.speed_sample
        
    def T_VTI(self):
        answer = get(self.device, 'READ:DEV:MB1.T1 :TEMP:SIG:TEMP')
        return answer        
        
    def T_sample(self):
        answer = get(self.device, 'READ:DEV:DB8.T1 :TEMP:SIG:TEMP')
        return answer
    
    def Flow_perc_VTI(self):
        answer = get(self.device, 'READ:DEV:MB1.T1 :LOOP:FSET')
        return answer
    
    def Flow_perc_sample(self):
        answer = get(self.device, 'READ:DEV:DB8.T1 :LOOP:FSET')
        return answer
        
    def set_T_VTI(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('T_VTI')])
        if speed == None:
            self.set_T_VTI_rate(maxspeed)
            self.device.write(f'SET:DEV:MB1.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
        elif speed == 'SetGet':
            if hasattr(self, 'speed_VTI'):
                speed = self.speed_VTI
            else:
                speed = maxspeed
            self.set_T_VTI_rate(speed)
            self.device.write(f'SET:DEV:MB1.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
        else:
            speed = min(maxspeed, speed)
            self.speed_VTI = speed
            self.set_T_VTI_rate(speed)
            self.device.write(f'SET:DEV:MB1.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
    
    def set_T_sample(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('T_sample')])
        if speed == None:
            self.set_T_sample_rate(maxspeed)
            self.device.write(f'SET:DEV:DB8.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
        elif speed == 'SetGet':
            if hasattr(self, 'speed_sample'):
                speed = self.speed_sample
            else:
                speed = maxspeed
            self.set_T_sample_rate(speed)
            self.device.write(f'SET:DEV:DB8.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
        else:
            speed = min(speed, maxspeed)
            self.speed_sample = speed
            self.set_T_sample_rate(speed)
            self.device.write(f'SET:DEV:DB8.T1 :TEMP:LOOP:TSET:{round(float(value), 3)}')
    
    def set_T_VTI_rate(self, value):
        self.device.write(f'SET:DEV:MB1.T1 :TEMP:LOOP:RSET:{round(float(value), 3)}')
        
    def set_T_sample_rate(self, value):
        self.device.write(f'SET:DEV:DB8.T1 :TEMP:LOOP:RSET:{round(float(value), 3)}')
    
    
    
        
        