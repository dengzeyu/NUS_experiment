from MultiPyVu import MultiVuClient as mvc
from enum import IntEnum

class opticool():
    def __init__(self, adress = '192.168.1.207:5000'):
        host, port = adress.split(':')
        port = int(port)
        
        self.device = mvc.MultiVuClient(host=host, port = port)
        self.device.open()
        self.T_states = self.device.temperature.state_code_dict()
        self._T_approach = self.device.temperature.approach_mode(1)
        self._Field_approach = self.device.field.approach_mode(2)
        self._Field_driven = self.device.field.driven_mode(1)
        self._chamber_state = self.device.chamber.mode(1)
        self._T_rate = self.device.temperature.set_rate_per_min
        self._Field_rate = self.device.field.set_rate_per_sec
        self.set_options = ['T', 'Field', 'T_rate', 'Field_rate', 'T_approach', 'Field_approach', 'Field_driven', 'chamber_state']
        self.get_options = ['T', 'Field', 'T_rate', 'Field_rate', 'T_approach', 'Field_approach', 'Field_driven', 'chamber_state']
        self.sweepable = [True, True, False, False, False, False, False, False]
        self.maxspeed = [5, self.max_Field_speed(), None, None, None, None, None, None]
    
    def max_Field_speed(self):
        if not hasattr(self, 'cur_field'):
            self.Field()
        if abs(self.cur_Field) < 60000 and abs(self.cur_Field) >= 0:
            return 110
        elif abs(self.cur_Field) < 65000 and abs(self.cur_Field) >= 60000:
            return 30
        elif abs(self.cur_Field) < 80000 and abs(self.cur_Field) >= 65000:
            return 10
    
    def Field(self):
        self.cur_Field, self.state_Field = self.device.get_field()
        result = self.cur_Field
        return result

    def Field_approach(self):
        
        """
        linear = 0
        no_overshoot = 1
        oscillate = 2
        """
        
        return self._Field_approach.value
    
    def Field_driven(self):
        
        """
        persistent = 0
        driven = 1
        """
        
        return self._Field_driven.value

    def T_approach(self):
        
        """
        fast_settle = 0
        no_overshoot = 1
        """
        
        return self._T_approach.value

    def T(self):
       self.temperature, self.state_temperature = self.device.get_temperature()
       result = self.temperature
       return result
   
    def T_rate(self):
        return self._T_rate
    
    def Field_rate(self):
        return self._Field_rate
   
    def set_T_rate(self, value):
        maxspeed = self.maxspeed[self.set_options.index('T')]
        if value > maxspeed:
            value = maxspeed
        self._T_rate = float(value)
        self.device.temperature.set_rate_per_min = self._T_rate
    
    def set_Field_rate(self, value):
        maxspeed = self.maxspeed[self.set_options.index('Field')]
        if value > maxspeed:
            value = maxspeed
        self._Field_rate = float(value)
        self.device.field.set_rate_per_sec = self._Field_rate
   
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
        
        class modeEnum(IntEnum):
            seal = 0
            purge_seal = 1
            vent_seal = 2
            pump_continuous = 3
            vent_continuous = 4
            high_vacuum = 5
            
        self._chamber_state = modeEnum(value)
        self.device.chamber_set_mode = self._chamber_state.value
   
    def Field_state(self):
        if hasattr(self, 'state_Field'):
            result = self.state_Field
        else:
            self.Field()
            result = self.state_Field
        return result
    
    def T_state(self):
        if hasattr(self, 'state_temperature'):
            result = self.state_temperature
        else:
            self.T()
            result = self.state_temperature
        return result
    
    def set_T(self, value, speed = None):
        """

        Parameters
        ----------
        value : float, target temperature
        speed : rate per minute
        Units: K
        max is 1.

        """
        
        if speed == None:
            speed = self.maxspeed[self.set_options.index('T')]
                
        elif speed == 'SetGet':
            speed = self._T_rate
        
        self.set_T_rate(speed)
        
        self.device.temperature.set_point = value
        self.device.set_temperature(value, self._T_rate, self._T_approach)
        
    def set_T_approach(self, value):
        
        value = int(value)
        
        class ApproachEnum(IntEnum):
            fast_settle = 0
            no_overshoot = 1
        
        self._T_approach = ApproachEnum(value)
        self.device.temperature.set_approach = self._T_approach.value
        
    def set_Field(self, value, speed = None):
        """

        Parameters
        ----------
        value : float, target temperature
        speed : rate per second
        Units : Oe
        max is 1.

        """
        
        if speed == None:
            speed = self.maxspeed[self.set_options.index('Field')]
            
        elif speed == 'SetGet':
            speed = self._T_rate
        
        self.set_Field_rate(speed)
        
        self.device.field.set_point = value
        self.device.set_field(value, self._Field_rate, self._Field_approach)
    
    def set_Field_approach(self, value):
        
        value = int(value)
        
        class ApproachEnum(IntEnum):
            linear = 0
            no_overshoot = 1
            oscillate = 2
        
        self._Field_approach = ApproachEnum(value)
        self.device.field.set_approach = self._Field_approach.value
        
    def set_Field_driven(self, value):
        
        value = int(value)
        
        class drivenEnum(IntEnum):
            persistent = 0
            driven = 1
        
        self._Field_driven = drivenEnum(value)
        self.device.field.set_driven = self._Field_driven.value
        
    def stop(self):
        self.device.close_client()
    
def main():
    device = opticool()
    print(device.T())
    import time
    device.stop()
    
if __name__ == '__main__':
    main()
