"""
This example shows how to communicate with Thorlabs
KDC101, KCube Stepper Motor.
"""
import os
import time

from msl.equipment import (
    EquipmentRecord,
    ConnectionRecord,
    Backend,
)
from msl.equipment.resources.thorlabs import MotionControl


class KDC101():
    def __init__(self, ser = '27004046', kinesis_path = 'C:/Program Files/Thorlabs/Kinesis'):
        
        # ensure that the Kinesis folder is available on PATH
        if kinesis_path not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + kinesis_path

        # if adress == 'COM5':
        #     ser = '27004046'
        # elif adress == 'COM11':
        #     ser = '27004883'
        # elif adress == 'COM3':
        #     ser = '27004770'
            
        record = EquipmentRecord(
            manufacturer='Thorlabs',
            model='KDC101',
            serial=ser,  # update for your device
            connection=ConnectionRecord(
                backend=Backend.MSL,
                address='SDK::Thorlabs.MotionControl.KCube.DCServo.dll',
            ),
        )

        MotionControl.build_device_list()
        
        self.record = record
        self.device = self.record.connect()
        self.device.start_polling(250)
        self.device.enable_channel()
        self.device.load_settings()
        
        self.set_options = ['position']
        self.get_options = ['position']
        
        self.error = 1#1.0072619075
    
    def restart(self):
        self.close()
        
        
        MotionControl.build_device_list()
        
        self.device = self.record.connect()
        self.device.start_polling(250)
        self.device.enable_channel()
        self.device.load_settings()
        
    
    def position(self):
        
        position = self.device.get_position()
        position = self.device.get_real_value_from_device_unit(position, 'DISTANCE')
        
        return position * self.error
    
    def set_position(self, value):
        """

        Parameters
        ----------
        value : Float
            Position to go in mm.
        """
    
        value /= self.error
        value = self.device.get_device_unit_from_real_value(value, 'DISTANCE')
        self.device.move_to_position(value)
    
    def close(self):
        
        self.device.stop_polling()
        self.device.close()
        
        

# def main():
#     try:
#         device = KDC101('COM10')
#         device.set_position(57)
#         print(device.position())
#     except Exception as ex:
#         print(f'Exception hapened in executing KCube: {ex}')
#     finally:
#         device.close()
        
# if __name__ == '__main__':
#     main()