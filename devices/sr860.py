from pymeasure.instruments.srs import SR860

import pyvisa as visa

rm = visa.ResourceManager()

# Write command to a device and get it's output
def get(device, command):
    '''device = rm.open_resource() where this function gets all devices initiaals such as adress, baud_rate, data_bits and so on; 
    command = string Standart Commands for Programmable Instruments (SCPI)'''
    #return np.round(np.random.random(1), 1) #to test the program without device it would return random numbers
    return device.query(command)

class my_SR860(SR860):
    
    from pymeasure.instruments import Instrument
    
    xnoize = Instrument.measurement("OUTP? 8",
                               """ Reads the Xnoise value in Volts """
                               )
    
    ynoize = Instrument.measurement("OUTP? 9",
                               """ Reads the Xnoise value in Volts """
                               )
    
    FFT = Instrument.measurement("FCRY?",
                               """ Reads the amplitude of FFT on the cursor position """
                               )
    
    DC_bias = Instrument.control(
        "SOFF?", "SOFF %0.9e",
        """A floating property that represents the internal lock-in frequency in Hz
        This property can be set.""")

class sr860():

    def __init__(self, adress='GPIB0::3::INSTR'):

        self.sr860 = my_SR860(adress)
        
        self.set_options = ['amplitude', 'frequency', 'phase', 'sensitivity', 
                            'time_constant', 'input_range', 'low_pass_filter_slope', 'synchronous_filter_status',
                            'AUX1_output', 'AUX2_output', 'AUX3_output', 'AUX4_output', 'dc_bias', 'Write']

        self.get_options = ['x', 'y', 'r', 'Θ', 'xnoize', 'ynoize', 'FFT', 'sensitivity', 
                            'time_constant', 'input_range', 'low_pass_filter_slope', 'synchronous_filter_status',
                            'AUX1_input', 'AUX2_input', 'AUX3_input', 'AUX4_input', 
                            'amplitude', 'frequency', 'phase', 'dc_bias', 'Read']

    def IDN(self):
        device = rm.open_resource(
            self.adress)
        answer = get(device, '*IDN?')
        device.close()
        return answer
    
    def Write(self):
        return self.Read()
    
    def Read(self):
        device = rm.open_resource(
            self.adress)
        answer = device.read()
        device.close()
        return answer

    def x(self):
        return self.sr860.x

    def y(self):
        return self.sr860.y

    def r(self):
        return self.sr860.magnitude

    def Θ(self):
        return self.sr860.theta
    
    def FFT(self):
        return self.sr860.FFT
    
    def xnoize(self):
        return self.sr860.xnoize
    
    def ynoize(self):
        return self.sr860.ynoize

    def frequency(self):
        return self.sr860.frequency

    def phase(self):
        return self.sr860.phase

    def amplitude(self):
        return self.sr860.sine_voltage

    def sensitivity(self):
        return self.sr860.sensitivity

    def time_constant(self):
        return self.sr860.time_constant
    
    def input_range(self):
        return self.sr860.input_range

    def low_pass_filter_slope(self):
        return self.sr860.filter_slope

    def synchronous_filter_status(self):
        return self.sr860.filter_synchronous

    def AUX1_input(self):
        return self.sr860.aux_in_1

    def AUX2_input(self):
        return self.sr860.aux_in_2

    def AUX3_input(self):
        return self.sr860.aux_in_3

    def AUX4_input(self):
        return self.sr860.aux_in_4
    
    def dc_bias(self):
        return self.sr860.DC_bias
    
    def set_write(self, value):
        device = rm.open_resource(
            self.adress)
        device.write(value)
        device.close()

    def set_frequency(self, value=30.0):
        self.sr860.frequency = value

    def set_phase(self, value=0.0):
        self.sr860.phase = value

    def set_amplitude(self, value=0.5):
        self.sr860.sine_voltage = value

    def set_sensitivity(self, value=24):
        self.sr860.sensitivity = value

    def set_time_constant(self, value=19):
        self.sr860.time_constant = value
        
    def set_input_range(self, value = 3):
        self.sr830.input_range = value

    def set_low_pass_filter_slope(self, value=3):
        self.sr860.filter_slope = value

    def set_synchronous_filter_status(self, value=0):
        self.sr860.filter_synchronous = value

    def set_AUX1_output(self, value=0):
        self.sr860.aux_out_1 = value

    def set_AUX2_output(self, value=0):
        self.sr860.aux_out_2 = value

    def set_AUX3_output(self, value=0):
        self.sr860.aux_out_3 = value

    def set_AUX4_output(self, value=0):
        self.sr860.aux_out_4 = value
        
    def set_dc_bias(self, value):
        self.sr860.DC_bias = value
        
def main():
    device = sr860('GPIB0::2::INSTR')
    print(device.dc_bias())
    
if __name__ == '__main__':
    main()
    