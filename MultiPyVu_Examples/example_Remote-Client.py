# -*- coding: utf-8 -*-
'''
example_Remote-Client.py - This minimum working example will test that
the client PC can successfully contact the remote server PC.
'''

# Package used to insert a short wait time between data polls
import time

# Both the client and server must be running on the same machine for 'local' operation.
from MultiPyVu import MultiVuClient as mvc

host = "172.00.00.1"
port = 5000

# Start the client
with mvc.MultiVuClient(host, port) as client:

    # A basic loop that demonstrates communication between client/server
    for t in range(5):
        # Polls MultiVu for the temperature, field, and their respective states
        T, sT = client.get_temperature()
        F, sF = client.get_field()

        # Relay the information from MultiVu
        message = f'The temperature is {T}, status is {sT}; the field is {F}, status is {sF}. '
        print(message)

        # collect data at roughly 2s intervals
        time.sleep(2)

    # This command is used to close the client, but keep the server running.
    # Note: it occurs automatically at the termination of the 'with' block
    # client.close_client()

    # This command will close the client AND server.
    # client.close_server()
