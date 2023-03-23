"""
Python rohdeschwarz VNA example
"""

import sys

if __name__ != "__main__":
    print("'{0}'\nis a script. Do not import!".format(__file__))
    print('Exiting...')
    sys.exit()
from rohdeschwarz import *
from rohdeschwarz.instruments.vna import *
import numpy as np

vna = Vna()

vna.open_tcp('169.254.82.39', 5025)

vna.bus._set_timeout_ms(10000)

#print(vna.reverse_sweep(100000, 500000, 500))
start_freq = int(50e+6)
stop_freq = int(100e+6)
num_points = 100
vna.set_start_freq(start_freq)
vna.set_stop_freq(stop_freq)
vna.set_num_points(num_points)
vna.start_sweep()

x = np.linspace(start_freq, stop_freq, num_points)
y = vna.trace_data()

y = [float(i) for i in y.split(',')]

print(vna.fit(x, y))

vna.set_bandwidth(100)

print(f'Bandwidth is {vna.bandwidth()}') 

filename = r'C:\NUS\Makar_and_Timofey\rohdeschwarz\examples\test.txt'

#vna.create_file(filename)

#vna.get_data(filename)

#print(vna.trace_im())

#print(vna.power())

# Close Log
vna.close_log()

# Close connection
vna.close()
