asc500 = list_of_devices[list_of_devices_addresses.index('COM3')]
keithley = list_of_devices[list_of_devices_addresses.index('GPIB6')]

n_steps_x = 50
n_probe_x = 5

n_steps_y = 50
n_probe_y = 5

n_steps_z = 20
n_probe_z = 2

def probe_move(n_probe: int = 5, axis: str = 'x'):
    """
    Make "n_probe" steps along "axis" to determine the sign of a gradient
    Parameters
    ----------
    n_probe : int
        number of steps to probe gradient. The default is 5.
    axis : str
        Axis alogn which to move. The default is 'x'.
    Returns
    -------
        True if grad_v >= 0
        False if grad_v < 0
    """
    init_v = getattr(keithley, 'Volt_DC')()
    getattr(asc500, f'set_step_up_{axis}')(n_probe)
    time.sleep(0.05)
    grad_v = getattr(keithley, 'Volt_DC')() - init_v
    if grad_v >= 0:
        return True
    else:
        return False
    
def move(n_steps: int = 50, n_probe: int = 5, axis: str = 'x'):
    """
    Parameters
    ----------
    n_steps : int
        max number of steps to go, if max is not found. The default is 50.
    n_probe : int
        number of steps to overshoot potential max. The default is 5.
    axis : str
        Axis alogn which to move. The default is 'x'.

    Returns
    -------
    None.

    """
    
    grad = probe_move(n_probe, axis)
    if grad:
        direction = 'up'
    else:
        direction = 'down'
    
    v = getattr(keithley, 'Volt_DC')()
    consecutive_counter = 0

    for i in n_steps:
        if consecutive_counter < n_probe: 
            getattr(asc500, f'set_step_{direction}_{axis}')(1)
            grad_v = getattr(keithley, 'Volt_DC')() - v
            if grad_v >= 0: #if still increasing, reset the consecutive_counter
                v += grad_v
                consecutive_counter = 0
            else:
                v += grad_v #if started to decrease, add +1 to consecutive counter
                consecutive_counter += 1
        else: #if peak is found and overshooted, go n_probe steps in the opposite direction
            if direction == 'up': #flip the direction
                direction = 'down'
            else:
                direction = 'up'
            getattr(asc500, f'set_step_{direction}_{axis}')(n_probe)
            break
            
while n_steps_x > n_probe_x + 2 and n_steps_y > n_probe_y + 2 and n_steps_z > n_probe_z + 2:
    move(n_steps_x, n_probe_x, 'x')
    move(n_steps_y, n_probe_y, 'y')
    move(n_steps_z, n_probe_z, 'z')
    
    n_steps_x -= n_probe_x
    n_steps_y -= n_probe_y
    n_steps_z -= n_probe_z    
            
    
    


