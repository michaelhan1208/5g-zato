# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.test import CommandLineTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.server.generic.api.outconn_wsx import OutconnWSXWrapper, _ZatoWSXClientImpl

# ################################################################################################################################
# ################################################################################################################################

ExtraProperties = WEB_SOCKET.ExtraProperties

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnBaseCase(CommandLineTestCase):

    def _get_config(
        self,
        name:'str',
        wsx_channel_address:'str',
        username:'str' = '',
        secret:'str' = '',
        queue_build_cap:'float' = 30.0
    ) -> 'stranydict':

        config = {}
        config['name'] = name
        config['username'] = username
        config['secret'] = secret
        config['pool_size'] = 1
        config['is_zato'] = True
        config['is_active'] = True
        config['needs_spawn'] = False
        config['queue_build_cap'] = queue_build_cap
        config['subscription_list'] = ''
        config['has_auto_reconnect'] = False

        config['auth_url'] = config['address'] = wsx_channel_address

        return config

# ################################################################################################################################

    def _check_connection_result(
        self,
        wrapper:'OutconnWSXWrapper',
        wsx_channel_address:'str',
        *,
        needs_credentials:'bool',
        should_be_authenticated:'bool',
    ) -> 'None':

        outconn_wsx_queue = wrapper.client.queue.queue
        self.assertEqual(len(outconn_wsx_queue), 1)

        impl = outconn_wsx_queue[0].impl
        zato_client = impl._zato_client # type: _ZatoWSXClientImpl

        self.assertEqual(zato_client.config.address, wsx_channel_address)

        if should_be_authenticated:
            self.assertTrue(zato_client.auth_token.startswith('zwsxt'))
            self.assertTrue(zato_client.is_connected)
            self.assertTrue(zato_client.is_authenticated)
            self.assertTrue(zato_client.keep_running)
        else:
            self.assertEqual(zato_client.auth_token, '')
            self.assertFalse(zato_client.is_connected)
            self.assertFalse(zato_client.is_authenticated)
            self.assertFalse(zato_client.keep_running)

        if needs_credentials:
            self.assertTrue(zato_client.needs_auth)
            self.assertTrue(zato_client.is_auth_needed)
        else:
            self.assertFalse(zato_client.needs_auth)
            self.assertFalse(zato_client.is_auth_needed)

# ################################################################################################################################
# ################################################################################################################################

class WSXChannelManager:

    test_case: 'CommandLineTestCase'
    username: 'str'
    password: 'str'
    channel_id: 'str'
    security_id: 'str'
    security_name: 'str'
    pubsub_endpoint_id: 'str'
    needs_credentials: 'bool'
    wsx_channel_address: 'str'
    run_cli: 'bool'

    def __init__(
        self,
        test_case:'CommandLineTestCase',
        username:'str' = '',
        password:'str' = '',
        needs_credentials:'bool' = False,
        needs_pubsub:'bool' = False,
        run_cli:'bool' = True
    ) -> 'None':
        self.test_case = test_case
        self.username = username
        self.password = password
        self.needs_pubsub = needs_pubsub
        self.needs_credentials = needs_credentials
        self.run_cli = run_cli

        self.channel_id = ''
        self.security_id = ''
        self.security_name = ''
        self.wsx_channel_address = ''

# ################################################################################################################################

    def create_basic_auth(self):

        # Command to invoke ..
        cli_params = ['create', 'basic-auth', '--username', self.username, '--password', self.password]

        # .. always run in verbose mode ..
        cli_params.append('--verbose')

        # .. get the command's response as a dict ..
        if self.run_cli:

            out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

            # .. and store the security definition's details for later use.
            self.security_id = out['id']
            self.security_name = out['name']

# ################################################################################################################################

    def create_pubsub_endpoint(self, wsx_id:'str') -> 'None':

        # Command to invoke ..
        cli_params = ['pubsub', 'create-endpoint', '--wsx-id', wsx_id]

        # .. always run in verbose mode ..
        cli_params.append('--verbose')

        # .. get the command's response as a dict ..
        if self.run_cli:

            out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

            # .. and store the endpoint's details for later use.
            self.pubsub_endpoint_id = out['id']

# ################################################################################################################################

    def __enter__(self) -> 'WSXChannelManager':

        # Command to invoke ..
        cli_params = ['wsx', 'create-channel']

        # .. credentials are optional ..
        if self.needs_credentials:

            # .. first, we need a Basic Auth definition for the WSX channel ..
            self.create_basic_auth()

            # .. now, we can make use of that definition ..
            cli_params.append('--security')
            cli_params.append(self.security_name)

        # .. we want for the channel to store the runtime context for later use ..
        extra_properties = dumps({
            ExtraProperties.StoreCtx: True
        })

        cli_params.append('--extra-properties')
        cli_params.append(extra_properties)

        # .. always run in verbose mode ..
        cli_params.append('--verbose')

        # .. get the command's response as a dict ..
        if self.run_cli:

            out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

            # .. store for later use ..
            self.channel_id = out['id']
            self.wsx_channel_address = out['address']

            # .. pub/sub is optional ..
            if self.needs_pubsub:
                self.create_pubsub_endpoint(self.channel_id)

        # .. and return control to the caller.
        return self

# ################################################################################################################################

    def delete_basic_auth(self):

        # Command to invoke ..
        cli_params = ['delete', 'basic-auth', '--id', self.security_id]

        # .. now, invoke the command, ignoring the result.
        if self.run_cli:
            _ = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################

    def __exit__(self, type_:'any_', value:'any_', traceback:'any_'):

        if self.needs_credentials:
            self.delete_basic_auth()

        # Note that deleting the channel below will also cascade to delete its endpoint
        # which means that, if we did create an endpoint earlier on, we do not need
        # to delete it explicitly.

        # Command to invoke ..
        cli_params = ['wsx', 'delete-channel', '--id', self.channel_id, '--verbose']

        # .. get its response as a dict ..
        if self.run_cli:
            self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################
# ################################################################################################################################
