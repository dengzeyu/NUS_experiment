# -*- coding: utf-8 -*-
"""
example_Command-Demos.py - Demonstrates the use of various commands to set temp/field/chamber,
read back their present value and status, and wait for stability
criteria to be met.  This script should run on the MultiVu PC, as it
is configured for local operation.
"""

import time

from MultiPyVu import MultiVuServer as mvs
from MultiPyVu import MultiVuClient as mvc


def save_temp_field_chamber():
    T, sT = client.get_temperature()
    F, sF = client.get_field()
    C = client.get_chamber()
    print(f'{T:{7}.{3}f} {sT:{10}} {F:{7}} {sF:{20}} {C:{15}}')


# Start the server.
with mvs.MultiVuServer() as server:

    # start the client
    with mvc.MultiVuClient() as client:

        # Allow the connection to complete initialization
        time.sleep(5)

        # Set 300 K and 0 Oe
        print('Setting 300 K and 0 Oe')
        client.set_temperature(300,
                               20, 
                               client.temperature.approach_mode.fast_settle)
        client.set_field(0.0,
                         200, 
                         client.field.approach_mode.linear,
                         client.field.driven_mode.driven)

        # Wait for 10 seconds after temperature and field are stable
        print('Waiting ')
        client.wait_for(10,
                        timeout_sec=0,
                        bitmask=client.subsystem.temperature | client.subsystem.field)

        # Purge/Seal the chamber; wait to continue
        print('Change the chamber state to Purge/Seal')
        client.set_chamber(client.chamber.mode.purge_seal)
        client.wait_for(10, timeout_sec=0, bitmask=client.subsystem.chamber)

        # print a header
        print('')
        hdr = '______ T ______     __________ H __________\t______ Chamber Status ______'
        print(hdr)

        # Polling temperature/field during a temperature ramp to 296 K
        CurrentTemp, sT = client.get_temperature()
        points = 10
        setpoint = 296
        rate = 2
        wait = abs(CurrentTemp-setpoint)/points/rate*60
        message = f'Set the temperature {setpoint} K and then '
        message += f'collect {points} data points while ramping'
        print('')
        print(message)
        print('')
        client.set_temperature(setpoint,
                               rate,
                               client.temperature.approach_mode.no_overshoot)
        for t in range(points):
            save_temp_field_chamber()
            # poll data at roughly equal intervals based on points/ramp
            time.sleep(wait)

        # Polling temperature/field during a field ramp to 1000 Oe
        CurrentField, sF = client.get_field()
        setpoint = 1000
        rate = 10
        wait = abs(CurrentField-setpoint)/points/rate
        message = f'Set the field to {setpoint} Oe and then collect data '
        message += 'while ramping'
        print('')
        print(message)
        print('')
        client.set_field(setpoint,
                         rate,
                         client.field.approach_mode.linear,
                         client.field.driven_mode.driven)
        for t in range(10):
            save_temp_field_chamber()
            # poll data at roughly equal intervals based on points/ramp
            time.sleep(wait)

        # print a blank line
        print('')
        field, status = client.get_field()
        fieldUnits = client.field.units
        print(f'Field = {field} {fieldUnits}')
        deltaH = 100.0
        newH = field + deltaH
        rateH = 250.0
        print(f'Raising the field to {newH} {fieldUnits}')
        client.set_field(newH, rateH, client.field.approach_mode.linear)

        temperature, status = client.get_temperature()
        tempUnits = client.temperature.units
        print(f'\nTemperature = {temperature} {tempUnits}')
        deltaT = 2.0
        newT = temperature + deltaT
        rateT = 5.0
        delay = deltaT / rateT * 60.0
        msg = f'Raising the temperature by {deltaT} {tempUnits}.  Should '
        msg += f'take about {delay} seconds to reach the temperature, but '
        msg += 'could take additional time to stabilize.'
        print(msg)
        client.set_temperature(newT,
                               rateT, 
                               client.temperature.approach_mode.no_overshoot)
        start = time.time()
        client.wait_for(0, 0, client.subsystem.temperature)
        end = time.time()
        temperature, status = client.get_temperature()
        print(f'Temperature = {temperature} {tempUnits}')
        print(f'The ramp took {end - start:.3f} sec')

        field, status = client.get_field()
        print(f'\nField = {field} {fieldUnits}')
        deltaH = 500.0
        newH = field + deltaH
        rateH = 50.0
        delay = deltaH / rateH
        pause_time = 10.0
        msg = f'Raising the field by {deltaH} {fieldUnits}.  Should take '
        msg += f'about {delay} seconds to reach the set point, but could take '
        msg += 'additional time to stabilize. Once stable, adding another '
        msg += f'{pause_time} seconds before moving on.'
        print(msg)
        client.set_field(newH, rateH, client.field.approach_mode.linear)
        start = time.time()
        client.wait_for(pause_time, 0, client.subsystem.field)
        end = time.time()
        field, status = client.get_field()
        print(f'Field = {field} {fieldUnits}')
        print(f'The ramp took {end - start:.3f} sec')

        newT = 300
        newH = 0.0
        msg = f'\nWait for the temperature to reach {newT} and '
        msg += f'the field to reach {newH}'
        print(msg)
        client.set_temperature(newT,
                               rateT, 
                               client.temperature.approach_mode.fast_settle)
        client.set_field(newH, rateH, client.field.approach_mode.linear)
        start = time.time()
        client.wait_for(0,
                        0,
                        client.subsystem.temperature | client.subsystem.field)
        end = time.time()
        temperature, status = client.get_temperature()
        field, status = client.get_field()
        print(f'Temperature = {temperature} {tempUnits}')
        print(f'Field = {field} {fieldUnits}')
        print(f'The ramp took {end - start:.3f} sec')

        time.sleep(5)

        # For PPMS systems, the magnet can be put in persistent mode, but not for VL/DC/OC/M3
        # try:
        #     print('\nTry to put the magnet in persistent mode:')
        #     client.set_field(100,
        #                      100,
        #                      client.field.approach_mode.oscillate,
        #                      client.field.driven_mode.persistent)
        #     print('The above command will only work for a PPMS')
        # except Exception as e:
        #     print(e.message)
        #     notice = '\nThe above command failed because only the PPMS '
        #     notice += 'platform can drive the magnet in persistent mode.'
        #     print(notice)
