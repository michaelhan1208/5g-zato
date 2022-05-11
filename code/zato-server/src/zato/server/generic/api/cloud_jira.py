# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.jira_ import JiraClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _JiraClient:
    def __init__(self, config:'stranydict') -> 'None':

        # The actual connection object
        self.impl = JiraClient.from_config(config)

    def ping(self):
        result = self.impl.conn.request(path='/rest/auth/latest/session')
        result

# ################################################################################################################################
# ################################################################################################################################

class CloudJiraWrapper(Wrapper):
    """ Wraps a queue of connections to Jira.
    """
    def __init__(self, config:'stranydict', server) -> 'None':
        config['auth_url'] = config['address']
        super(CloudJiraWrapper, self).__init__(config, 'Jira', server)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = _JiraClient(self.config)
            self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Jira client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('_JiraClient', client)
            client.ping()

# ################################################################################################################################

    def delete(self, ignored_reason=None):
        pass

# ################################################################################################################################
# ################################################################################################################################
