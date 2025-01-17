# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.api import wait_until_port_free

def wait_for_ports(*data): # type: ignore
    """ Blocks until input TCP ports are free.
    """
    for port, component in data:
        if not wait_until_port_free(port, 10):
            print(f'Port taken {port} ({component})')

if __name__ == '__main__':
    data = [
        [8183,  'Dashboard'],
        [11223, 'Load-balancer'],
        [20151, 'Load-balancer\'s agent'],
        [31530, 'Scheduler'],

        # Servers come last because they may be the last to stop
        # in case we are being called during an environment's restart.
        [17010, 'server1'],
        [17011, 'server2']
    ]

    wait_for_ports(*data)
