#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
example_MVDataFile-VISA.py - Demonstrates a simple use case of
MultiVuDataFile to build a .dat file which includes temperature
and field values collected via the server-client link.  Further,
a simple implementation for pulling in external values to the .dat
file using PyVISA is outlined.  This script should run on the
MultiVu PC, as it is configured for local operation.
NOTE: the VISA parameters for the resource and query command need
to be updated to match the user's hardware before this script will
properly execute.
"""

import time
import pyvisa

from MultiPyVu import MultiVuClient as mvc
from MultiPyVu import MultiVuServer as mvs
from MultiVuDataFile import MultiVuDataFile as mvd


def save_data():
    T, sT = client.get_temperature()
    data.set_value('Temperature', T)
    F, sF = client.get_field()
    data.set_value('Field', F)
    # This example serial command polls the external instrument using
    # the 'TALKEDATA? 1' command. See the instrument's manual for a
    # listing of relevant commands.
    ep = inst.query_ascii_values('TAKEDATA? 1')[0]
    data.set_value('External Parameter (AU)', ep)
    data.write_data()
    print(f'{T:{7}.{3}f} {sT:{10}}{F:{5}} ({sF})\t{ep:{5}}')

# Configure the VISA connection
# the PyVISA module needs to be installed/imported
rm = pyvisa.ResourceManager()

print('Confirm the resources are the expected ones:')
resources = rm.list_resources()
print(f'{resources = }')

# Our example instrument is on GPIB0 at the address 18
inst = rm.open_resource('GPIB0::18::INSTR')
# A common serial command asking the instrument to identify itself
# which confirms communication.
print(f'Instrument ID = {inst.query("*IDN?")}')

# configure the MultiVu columns
data = mvd.MultiVuDataFile()
data.add_multiple_columns(['Temperature', 'Field', 'External Parameter (AU)'])
data.create_file_and_write_header('myMultiVuFile.dat', 'Collecting VISA Data')

# Start the server.
with mvs.MultiVuServer() as server:

    # start the client
    with mvc.MultiVuClient() as client:

        time.sleep(5)

        points = 11
        interval = 2
        message = f'Collect {points} data points, one every '
        message += f'{interval} seconds.'
        print(message)

        # print a header
        print('')
        hdr = '______ T ______     __________ H __________\t______ Ext Param ______'
        print(hdr)

        for t in range(points):
            save_data()
            # collect data about every 2 s
            time.sleep(interval)
