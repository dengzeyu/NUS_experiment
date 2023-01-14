import pandas as pd
import pyvisa as visa
import numpy as np
import time

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    #return np.round(np.random.random(1), 1) #to test the program without device it would return random numbers
    return device.query(command)

class SR830():

    def __init__(self, adress='GPIB0::11::INSTR'):

        self.sr830 = rm.open_resource(
            adress, write_termination='\n', read_termination='\n')

        self.modes_ch1_options = ['X', 'R', 'X noise', 'AUX in 1', 'AUX in 2']

        self.modes_ch2_options = ['Y', 'Θ', 'Y noise', 'AUX in 3', 'AUX in 4']

        self.sensitivity_options = ['2 nV/fA', '5 nV/fA', '10 nV/fA',
                                    '20 nV/fA', '50 nV/fA', '100 nV/fA',
                                    '200 nV/fA', '500 nV/fA', '1 μV/pA',
                                    '2 μV/pA', '5 μV/pA', '10 μV/pA',
                                    '20 μV/pA', '50 μV/pA', '100 μV/pA',
                                    '200 μV/pA', '500 μV/pA',
                                    '1 mV/nA', '2 mV/nA', '5 mV/nA', '10 mV/nA',
                                    '20 mV/nA', '50 mV/nA', '100 mV/nA',
                                    '200 mV/nA', '500 mV/nA', '1 V/μA']

        self.time_constant_options = ['10 μs', '30 μs', '100 μs',
                                      '300 μs', '1 ms', '3 ms',
                                      '10 ms', '30 ms', '100 ms',
                                      '300 ms', '1 s', '3 s',
                                      '10 s', '30 s', '100 s',
                                      '300 s', '1 ks', '3 ks',
                                      '10 ks', '30 ks']

        self.low_pass_filter_slope_options = ['6 dB/oct', '12 dB/oct',
                                              '18 dB/oct', '24 dB/oct']

        self.synchronous_filter_status_options = ['On', 'Off']

        self.remote_status_options = ['lock', 'Unlock']

        self.set_options = ['amplitude', 'frequency', 'phase', 'AUX1_output', 'AUX2_output', 'AUX3_output', 'AUX4_output']

        self.get_options = ['x', 'y', 'r', 'Θ', 'ch1', 'ch2',
                            'AUX1_input', 'AUX2_input', 'AUX3_input', 'AUX4_input', 'amplitude', 'frequency', 'phase']

    def IDN(self):
        answer = get(self.sr830, '*IDN?')
        return answer

    def x(self):
        try:
            answer = float(get(self.sr830, 'OUTP?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?1'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?1'))
        return answer

    def y(self):
        try:
            answer = float(get(self.sr830, 'OUTP?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?2'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?2'))
        return answer

    def r(self):
        try:
            answer = float(get(self.sr830, 'OUTP?3'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?3'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTP?3'))
        return answer

    def Θ(self):
        try:
            answer = float(get(self.sr830, 'OUTP?4'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTP?4'))
        return answer

    def frequency(self):
        try:
            answer = float(get(self.sr830, 'FREQ?'))
        except ValueError:
            answer = float(get(self.sr830, 'FREQ?'))
        return answer

    def phase(self):
        try:
            answer = float(get(self.sr830, 'PHAS?'))
        except ValueError:
            answer = float(get(self.sr830, 'PHAS?'))
        return answer

    def amplitude(self):
        try:
            answer = float(get(self.sr830, 'SLVL?'))
        except ValueError:
            answer = float(get(self.sr830, 'SLVL?'))
        return answer

    def sensitivity(self):
        try:
            answer = float(get(self.sr830, 'SENS?'))
        except ValueError:
            answer = float(get(self.sr830, 'SENS?'))
        return answer

    def time_constant(self):
        try:
            answer = int(get(self.sr830, 'OFLT?'))
        except ValueError:
            answer = int(get(self.sr830, 'OFLT?'))
        return answer

    def low_pass_filter_slope(self):
        try:
            answer = int(get(self.sr830, 'OFSL?'))
        except ValueError:
            answer = int(get(self.sr830, 'OFSL?'))
        return answer

    def synchronous_filter_status(self):
        try:
            answer = int(get(self.sr830, 'SYNC?'))
        except ValueError:
            answer = int(get(self.sr830, 'SYNC?'))
        return answer

    def remote(self):
        try:
            answer = int(get(self.sr830, 'OVRM?'))
        except ValueError:
            answer = int(get(self.sr830, 'OVRM?'))
        return answer

    def ch1(self):
        try:
            answer = float(get(self.sr830, 'OUTR?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTR?1'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTR?1'))
        return answer

    def ch2(self):
        try:
            answer = float(get(self.sr830, 'OUTR?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OUTR?2'))
        if str(answer)[-4:] == 'e-00' or str(answer)[-4:] == 'e+00':
            answer = float(get(self.sr830, 'OUTR?2'))
        return answer

    def parameter(self):
        dataframe = pd.DataFrame({'Sensitivity': [self.sensitivity()],
                                  'Time_constant': [self.time_constant()],
                                  'Low_pass_filter_slope': [self.low_pass_filter_slope()],
                                  'Synchronous_filter_status': [self.synchronous_filter_status()],
                                  'Remote': [self.remote()],
                                  'Amplitude': [self.amplitude()],
                                  'Frequency': [self.frequency()],
                                  'Phase': [self.phase()]})
        return dataframe

    def channels(self):
        dataframe = pd.DataFrame({'Ch1': [self.ch1()], 'Ch2': [self.ch2()]})
        return dataframe

    def data(self):
        try:
            return [time.perf_counter(), self.x, self.y]
        except:
            pass
        # return [time.perf_counter() - zero_time, float(np.random.randint(10)), float(np.random.randint(10))]

    def AUX1_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?1'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?1'))
        return answer

    def AUX2_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?2'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?2'))
        return answer

    def AUX3_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?3'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?3'))
        return answer

    def AUX4_input(self):
        try:
            answer = float(get(self.sr830, 'OAUX?4'))
        except ValueError:
            answer = float(get(self.sr830, 'OAUX?4'))
        return answer

    def set_ch1_mode(self, mode=0):
        line = 'DDEF1,' + str(mode) + ',0'
        self.sr830.write(line)

    def set_ch2_mode(self, mode=0):
        line = 'DDEF2,' + str(mode) + ',0'
        self.sr830.write(line)

    def set_frequency(self, value=30.0):
        if value < 1e-3:
            value = 1e-3
        line = 'FREQ' + str(value)
        self.sr830.write(line)

    def set_phase(self, value=0.0):
        line = 'PHAS' + str(value)
        self.sr830.write(line)

    def set_amplitude(self, value=0.5):
        if value < 4e-3:
            value = 4e-3
        line = 'SLVL' + str(value)
        self.sr830.write(line)

    def set_sensitivity(self, value=24):
        try: 
            value = int(value)
        except:
            try:
                value = self.sensitivity_options.index(value)
            except:
                value = 24
        
        line = 'SENS' + str(value)
        self.sr830.write(line)

    def set_time_constant(self, value=19):
        try: 
            value = int(value)
        except:
            try:
                value = self.time_constant_options.index(value)
            except:
                value = 219
        
        line = 'OFLT' + str(value)
        self.sr830.write(line)

    def set_low_pass_filter_slope(self, value=3):
        try: 
            value = int(value)
        except:
            try:
                value = self.low_pass_filter_slope_options.index(value)
            except:
                value = 3
        
        line = 'OFSL' + str(value)
        self.sr830.write(line)

    def set_synchronous_filter_status(self, value=0):
        try: 
            value = int(value)
        except:
            try:
                value = self.synchronous_filter_status_options.index(value)
            except:
                value = 0
        
        line = 'SYNC' + str(value)
        self.sr830.write(line)

    def set_remote(self, mode=1):
        line = 'OVRM' + str(mode)
        self.sr830.write(line)

    def set_AUX1_output(self, value=0):
        line = 'AUXV1,' + str(value)
        self.sr830.write(line)

    def set_AUX2_output(self, value=0):
        line = 'AUXV2,' + str(value)
        self.sr830.write(line)

    def set_AUX3_output(self, value=0):
        line = 'AUXV3,' + str(value)
        self.sr830.write(line)

    def set_AUX4_output(self, value=0):
        line = 'AUXV4,' + str(value)
        self.sr830.write(line)
        
def main():
    device = SR830()
    print(device.IDN())
    
if __name__ == '__main__':
    main()
    