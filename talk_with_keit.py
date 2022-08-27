import pyvisa as visa
from pyvisa import constants

#Check if everything connected properly
rm = visa.ResourceManager()
rm.list_resources()

print(rm.list_resources(), '\n')


sr = rm.open_resource('GPIB0::3::INSTR',
                      write_termination= '\n', read_termination='\n')
                              

################################################################################

sr.write('SENS15')

    