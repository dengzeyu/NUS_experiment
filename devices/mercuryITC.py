from mercuryitc import MercuryITC
import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    return device.query(command)
    #return np.random.random(1)
    
class mercuryITC():
    def __init__(self, adress):
        self.device = MercuryITC(adress)
        self.set_options = ['T']
        self.get_options = ['T']
        
    def T(self):
        return(self.device.temp())
    
    def set_T(self):
        # TODO: add command to set temp
        self.device.write('')
        
        
        