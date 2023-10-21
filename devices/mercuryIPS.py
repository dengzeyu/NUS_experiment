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
        '''
        adress example '192.168.05:7020'
        '''
        ip, port = tuple(adress.split(':'))
        self.adress = f'TCPIP0::{ip}::{port}::SOCKET'
        self.device = rm.open_resource(self.adress, write_termination = '\n', read_termination = '\n')
        self.get_options = ['field', 'current', 'field_rate', 'current_rate', 'T']
        self.set_options = ['field', 'current', 'field_rate', 'current_rate']
        self.sweepable = [True, True, False, False]
        self.maxspeed = [self.TMin2OeSec(0.091), 1, None, None]
        self.eps = [0.1, 0.1, None, None]
        
    def Oe2T(self, value: float):
        answer = value * 1e-4
        return answer
    
    def T2Oe(self, value: float):
        answer = value * 1e4
        return answer
    
    def OeSec2TMin(self, value: float):
        answer = value * 1e-4 * 60
        return answer
    
    def TMin2OeSec(self, value: float):
        answer = value * 1e4 / 60
        return answer
        
    #def target_field(self) -> float:
    
    def field(self) -> float:
        answer = get(self.device, 'READ:DEV:GRPZ:PSU:SIG:FLD')
        answer = answer.split(':')[-1][:-1]
        answer = float(answer)
        answer = self.T2Oe(answer)
        return answer        
        
    def current(self) -> float:
        answer = get(self.device, 'READ:DEV:GRPZ:PSU:SIG:CURR')
        answer = answer.split(':')[-1][:-1]
        answer = float(answer)
        return answer 
    
    def field_rate(self) -> float:
        answer = get(self.device, 'READ:DEV:GRPZ:PSU:SIG:RFLD')
        answer = answer.split(':')[-1][:-5]
        answer = float(answer)
        answer = self.TMin2OeSec(answer)
        return answer  
    
    def current_rate(self) -> float:
        answer = get(self.device, 'READ:DEV:GRPZ:PSU:SIG:RCUR')
        answer = answer.split(':')[-1][:-5]
        answer = float(answer)
        return answer 
    
    def T(self) -> float:
        answer = get(self.device, 'READ:DEV:MB1.T1:TEMP:SIG:TEMP')
        answer = answer.split(':')[-1][:-1]
        answer = float(answer)
        return answer 
        
    def set_field(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('field')])
        value = float(value)
        value = self.Oe2T(value)
        if speed == None:
            speed = self.OeSec2TMin(maxspeed)
            self.set_field_rate(speed)
        elif speed == 'SetGet':
            pass
        else:
            speed = min(speed, maxspeed)
            speed = float(speed)
            speed = self.OeSec2TMin(speed)
            self.set_field_rate(speed)
        self.device.write('SET:DEV:GRPZ:PSU:ACTN:HOLD')
        self.device.write(f'SET:DEV:GRPZ:PSU:SIG:FSET:{round(float(value), 5)}')
        self.device.write('SET:DEV:GRPZ:PSU:ACTN:RTOS')
            
    def set_current(self, value, speed = None):
        maxspeed = float(self.maxspeed[self.set_options.index('current')])
        if speed == None:
            self.set_current_rate(maxspeed)
        elif speed == 'SetGet':
            pass
        else:
            speed = min(speed, maxspeed)
            self.set_current_rate(speed)
        self.device.write('SET:DEV:GRPZ:PSU:ACTN:HOLD')
        self.device.write(f'SET:DEV:GRPZ:PSU:SIG:CSET:{round(float(value), 5)}')
        self.device.write('SET:DEV:GRPZ:PSU:ACTN:RTOS')
            
    def set_field_rate(self, value):
        self.device.write(f'SET:DEV:GRPZ:PSU:SIG:RFST:{round(float(value), 5)}')
        
    def set_current_rate(self, value):
        self.device.write(f'SET:DEV:GRPZ:PSU:SIG:RCST:{round(float(value), 5)}')
        
    def close(self):
        self.device.close()
        
def main():
    device = mercuryIPS(adress = '192.168.0.5:7020')
    try:
        device.set_field(0)
    except Exception as e:
        print(f'Exception happened: {e}')
    finally:
        device.close()
    
if __name__ == '__main__':
    main()
    
    
    
        
        