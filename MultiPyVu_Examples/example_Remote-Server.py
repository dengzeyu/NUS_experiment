# -*- coding: utf-8 -*-
'''
example_Remote-Server.py - For remote operation; this script must be 
running on the on the control PC along with the MultiVu executable.
'''

import sys

from MultiPyVu import MultiVuServer as mvs


def server(flags: str = ''):
    if sys.argv[1:]:
        user_flags = sys.argv[1:]

    else:
        msg = 'No flags detected; using hard-coded IP address'
        msg += 'for remote access.'
        print(msg)

        # This value comes from the server PC's self-identified IPV4 
        # address and needs to be manually input
        user_flags = ['-ip=172.00.00.1']

    # Opens the server connection
    s = mvs.MultiVuServer(user_flags, keep_server_open=True)
    s.open()


if __name__ == '__main__':
    server()
