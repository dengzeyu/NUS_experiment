import libximc
import tempfile
import urllib
import re
from libximc import *
from ctypes import *

class ZStage():
    def __init__(self, adress = 'COM4'):
        self.open_name = b'xi-com:\\\\.\\' + bytes(adress)
        self.device_id = lib.open_device(self.open_name)
        # Create engine settings structure
        self.eng = engine_settings_t()
        result_eng = lib.get_engine_settings(self.device_id, byref(self.eng))

        # Create user unit settings structure
        self.user_unit = calibration_t()
        self.user_unit.MicrostepMode = self.eng.MicrostepMode
        self.user_unit.A = 52623 / 10000000

        BorderFlags.BORDER_IS_ENCODER = True #Borders are defined by encoder position
        BorderFlags.BORDERS_SWAP_MISSET_DETECTION = True #Engine stops when reach both borders
        self.edge = edges_settings_calb_t()
        self.edge.LeftBorder = 0.1
        self.edge.RightBorder = 12.725

        result_edge = lib.set_edges_settings_calb(self.device_id, byref(self.edge), byref(self.user_unit))
        
        self.set_options = ['position', 'shift']
        self.get_options = ['position', 'I_pwr', 'U_pwr', 'T_proc']
        
    def set_position(self, target):
        try:
            target = cfloat(target)
            result = lib.command_move_calb(self.device_id, target, byref(self.user_unit))
        except:
            return None
    
    def set_shift(self):
        try:
            target = cfloat(target)
            result = lib.command_movr_calb(self.device_id, target, byref(self.user_unit))
        except:
            return None
        
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
        moveStatus = status_MvCmdSts(lib, self.device_id)
        # print("\nRead position")
        x_pos = get_position_calb_t()
        result = lib.get_position_calb(self.device_id, byref(x_pos), byref(self.user_unit))
        if result == Result.Ok:
            return x_pos.Position
        else:
            return None
        
    def I_pwr(self):
        '''
        Consumable current on a power part, A
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.Ipwr * 1e3
        
    def U_pwr(self):
        '''
        Consumable voltage on a power part, V
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.Upwr * 1e3
        
    def T_proc(self):
        '''
        Current temperature of CPU
        '''
        status = status_t()
        result_status = lib.get_status(self.device_id, byref(status))

        return status.CurT * 10
        
    
        
    
        
        