import pyvisa as visa
from pymeasure.instruments.ami import AMI430

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    return device.query(command)

class ami430():
    def __init__(self, adress = 'ASRL13::INSTR'):
        self.adress = adress
        
        self.AMI430 = AMI430(self.adress)
        
        self.set_options = ['field', 'current', 'ramp_field_speed', 'ramp_current_speed', 'voltage_lim', 'coil_const']
        self.sweepable = [True, True, False, False, False, False]
        self.max_speed = [0.0357, 0.05, None, None, None, None]
        
        self.get_options = ['field', 'current']
        
    def set_field(self, value, speed = None):
        if speed == None:
            self.AMI430.ramp_to_field(value, self.maxspeed[self.set_options.index('field')])
        else:
            self.AMI430.ramp_to_field(value, speed)
            
    def set_current(self, value, speed = None):
        if speed == None:
            self.AMI430.ramp_to_current(value, self.maxspeed[self.set_options.index('current')])
        else:
            self.AMI430.ramp_to_current(value, speed)
    
    def set_ramp_field_speed(self, value):
        self.AMI430.ramp_rate_field = round(float(value), 5)
        
    def set_ramp_current_speed(self, value):
        self.AMI430.ramp_rate_current = round(float(value), 5)
        
    def set_voltage_lim(self, value = 1.5):
        self.AMI430.voltage_limit = round(float(value), 5)
        
    def set_coil_const(self, value = 0.1108033):
        self.AMI430.coilconst = round(float(value), 6)
        
    def field(self):
        return self.AMI430.field
    
    def current(self):
        return self.AMI430.magnet_current
    
def main():
    device = ami430()
    print(device.field())
    
if __name__ == '__main__':
    main()
        
        