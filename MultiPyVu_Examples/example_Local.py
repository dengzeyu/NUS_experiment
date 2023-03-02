# -*- coding: utf-8 -*-
'''
example_Local.py - This example tests local operation on the MultiVu PC.
'''

# Package used to insert a short wait time between data polls
import time

# Both the client and server must be running on the same machine 
# for 'local' operation.
from MultiPyVu import MultiVuClient as mvc
from MultiPyVu import MultiVuServer as mvs


# Start the server.
with mvs.MultiVuServer() as server:

    # Start the client
    with mvc.MultiVuClient() as client:

        # A basic loop that demonstrates communication between 
        # client/server
        for t in range(5):
            # Polls MultiVu for the temperature, field, and their
            #  respective states
            T, sT = client.get_temperature()
            F, sF = client.get_field()

            # Relay the information from MultiVu
            message = f'The temperature is {T}, status is {sT}; '
            message += f'the field is {F}, status is {sF}. '
            print(message)

            # collect data at roughly 2s intervals
            time.sleep(2)
            