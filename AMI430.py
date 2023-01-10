import pyvisa as visa
from pyvisa import constants

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    return device.query(command)

class AMI430():
    def __init__(self, adress):
        self.adress = adress
        
        self.AMI430 = rm.open_resource(self.adress,
                                   write_termination=';', read_termination=';')
        
        self.set_options = ['field', 'ramp_field', 'voltage_lim', 'coil_const']
        self.sweepable = [True, False, False, False, False, False]
        self.max_speed = [0.00367, None, None, None, None, None]
        
        self.get_options = ['field']
        
    def set_field(self, value, speed = None):
        if speed == None:
            self.AMI430.write('CONF:FIELD:TARG ' + str(round(float(value), 5)))
        else:
            self.set_ramp_field(speed)
            self.AMI430.write('CONF:FIELD:TARG ' + str(round(float(value), 5)))
    
    def set_ramp_field(self, value):
        self.AMI430.write('CONF:RAMP:RATE:FIELD 1,' + str(round(float(value), 5)), + ', 40.0')
        
    def set_voltage_lim(self, value = 1.5):
        self.AMI430.write('CONF:VOLT:LIM ' + str(round(float(value), 5)))
        
    def set_coil_const(self, value = 0.1108033):
        self.AMI430.write('CONF:COIL ' + str(round(float(value), 6)))
        
    def field(self):
        return float(get(self.AMI430, 'FIELD:MAG? '))
        
        