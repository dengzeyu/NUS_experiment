import libximc
import tempfile
import urllib
import re
from libximc import *
from ctypes import *
import time

class ZStage():
    def __init__(self, adress = 'ASRL5::INSTR'):
        self.open_name = b'xi-com:\\\\.\\COM' + bytes(adress[4], encoding = 'utf-8')
        self.device_id = lib.open_device(self.open_name)
        self.open_device()
        
        print(f'Device id: {self.device_id}')
        # Create engine settings structure
        self.eng = engine_settings_t()
        result_eng = lib.get_engine_settings(self.device_id, byref(self.eng))

        # Create user unit settings structure
        self.user_unit = calibration_t()
        self.user_unit.MicrostepMode = self.eng.MicrostepMode
        self.user_unit.A = 1 / 200
        
        self.commands = [None]
        
        '''
        BorderFlags.BORDER_IS_ENCODER = True #Borders are defined by encoder position
        BorderFlags.BORDERS_SWAP_MISSET_DETECTION = True #Engine stops when reach both borders
        self.edge = edges_settings_calb_t()
        self.edge.LeftBorder = 0.1
        self.edge.RightBorder = 12.725

        result_edge = lib.set_edges_settings_calb(self.device_id, byref(self.edge), byref(self.user_unit))
        '''
        
        self.set_options = ['position', 'shift']
        self.get_options = ['position', 'I_pwr', 'U_pwr', 'T_proc']
        
    def open_device(self):
        if self.device_id <= 0:
            for device_id in [1, 2]:
                lib.close_device(byref(cast(device_id, POINTER(c_int))))
            self.device_id = lib.open_device(self.open_name)
        
    def status_running(self):
        """
    
        Returns True if motor is running
                False if motor is not running

        """
        def get_status():
            """
            A function of reading status information from the device
            You can use this function to get basic information about the device status.
            
            :param lib: structure for accessing the functionality of the libximc library.
            :param device_id:  device id.
            """
            
            x_status = status_t()
            result = lib.get_status(self.device_id, byref(x_status))
            if result == Result.Ok:
                return x_status
            else:
                return None
        
        currStatus = get_status()
        return (currStatus.MvCmdSts & MvcmdStatus.MVCMD_RUNNING) # 0x80) # 
    
    def set_position(self, value):
        if  not self.status_running():
            result = lib.command_move_calb(self.device_id, c_float(value), byref(self.user_unit))
    
    def set_shift(self, value):
        if  not self.status_MvCmdSts_MVCMD_RUNNING():
            result = lib.command_movr_calb(self.device_id, c_float(value), byref(self.user_unit))
        
    def position(self):
        """
        Obtaining information about the position of the positioner.
        
        This function allows you to get information about the current positioner coordinates,
        both in steps and in encoder counts, if it is set.
        Also, depending on the state of the mode parameter, information can be obtained in user units.
        
        :param lib: structure for accessing the functionality of the libximc library.
        :param device_id: device id.
        :param mode: mode in feedback counts or in user units. (Default value = 1)
        """
        x_pos = get_position_calb_t()
        result = lib.get_position_calb(self.device_id, byref(x_pos), byref(self.user_unit))
        if result == Result.Ok:
            return x_pos.Position
        else:
            return 'Could not get a position'
        
    def I_pwr(self):
        '''
        Consumable current on a power part, A
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.Ipwr * 1e-3
        
    def U_pwr(self):
        '''
        Consumable voltage on a power part, V
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.Upwr * 1e-3
        
    def T_proc(self):
        '''
        Current temperature of CPU
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.CurT / 10

    def close(self):
        lib.close_device(byref(cast(self.device_id, POINTER(c_int))))

def main():
    adress = 'ASRL5::INSTR'
    stage = ZStage(adress)  
    
    try:
        stage.set_position(3)
        while stage.status_running():
            time.sleep(0.01)
        print(f'Current position is {stage.position()}')
    except:
        stage.close()
    finally:
        stage.close()
        
if __name__ == '__main__':
    main()