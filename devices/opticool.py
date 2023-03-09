from MultiPyVu import MultiVuClient as mvc

class opticool():
    def __init__(self, adress = '192.168.1.207'):
        self.device = mvc.MultiVuClient(host=adress)
        self.device.open()
        self.T_states = self.device.temperature.state_code_dict()
        self._T_approach = self.device.temperature.set_approach
        self._field_approach = self.device.field.set_approach
        self._field_driven = self.device.field.set_driven
        self._chamber_state = self.device.chamber.set_mode
        self.set_options = ['T', 'field', 'T_approach', 'field_approach', 'field_driven', 'chamber_state']
    
    def field(self):
        self.field, self.state_field = self.device.get_field()
        result = self.field
        return result

    def field_approach(self):
        
        """
        linear = 0
        no_overshoot = 1
        oscillate = 2
        """
        
        return self._field_approach
    
    def field_driven_mode(self):
        
        """
        persistent = 0
        driven = 1
        """
        
        return self._field_driven

    def T_approach(self):
        
        """
        fast_settle = 0
        no_overshoot = 1
        """
        
        return self._T_approach

    def T(self):
       self.temperature, self.state_temperature = self.device.get_temperature()
       result = self.temperature
       return result
   
    def chamber_state(self):
        
        """
        seal = 0
        purge_seal = 1
        vent_seal = 2
        pump_continuous = 3
        vent_continuous = 4
        high_vacuum = 5
        """
        
        return self.device.get_chamber()
    
    def set_chamber_state(self, value):
        value = int(value)
        if value in range(5):
            raise UserWarning(f'Chamber state is wrong. Used {value}, please use: seal = 0\npurge_seal = 1\nvent_seal = 2\npump_continuous = 3\nvent_continuous = 4\nhigh_vacuum = 5\n')
        else:
            self._chamber_state = value
   
    def field_state(self):
        if hasattr(self, 'state_field'):
            result = self.state_field
        else:
            self.field()
            result = self.state_field
        return result
    
    def T_state(self):
        if hasattr(self, 'state_temperature'):
            result = self.state_temperature
        else:
            self.T()
            result = self.state_temperature
        return result
    
    def set_T(self, value, speed = 1):
        """

        Parameters
        ----------
        value : float, target temperature
        speed : rate per minute
        Units: K
        max is 1.

        """
        
        self.device.set_temperature(value, speed, self._T_approach)
        
    def set_T_approach(self, value):
        value = int(value)
        self._T_approach = value
        
    def set_field(self, value, speed = 1):
        """

        Parameters
        ----------
        value : float, target temperature
        speed : rate per second
        Units : Oe
        max is 1.

        """
        
        self.device.set_field(value, speed, self._feild_approach)
    
    def set_field_approach(self, value):
        value = int(value)
        self._field_approach = value
        
    def set_field_driven(self, value):
        value = int(value)
        self._field_adriven = value
        
    def stop(self):
        self.device.close_client()
    
def main():
    device = opticool()
    print(device.T())
    print(device.T_approach())
    print(device.field())
    print(device.chamber_state())
    device.stop()
    
if __name__ == '__main__':
    main()
