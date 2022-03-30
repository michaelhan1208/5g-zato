# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.http_soap.url_data import URLData
    ParallelServer = ParallelServer
    URLData = URLData

# ################################################################################################################################
# ################################################################################################################################

class WorkerImpl:
    """ Base class for objects that implement worker functionality. Does not implement anything itself,
    instead serving as a common marker for all derived subclasses.
    """
    def __init__(self):
        self.server = None # type: ParallelServer
        self.worker_idx = None # type: int
        self.url_data = None # type: URLData

# ################################################################################################################################
# ################################################################################################################################
