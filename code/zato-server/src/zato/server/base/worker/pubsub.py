# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore
    from zato.server.pubsub import PubSub as ServerPubSub
    ServerPubSub = ServerPubSub

# ################################################################################################################################
# ################################################################################################################################

class PubSub(WorkerImpl):
    """ Publish/subscribe-related functionality for worker objects.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pubsub = self.pubsub # type: ServerPubSub

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_topic_object(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.pubsub.edit_topic(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.delete_topic(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_EDIT(self, msg):
        self.pubsub.edit_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.delete_endpoint(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_subscription_object(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        msg.pop('action') # Not needed by pub/sub
        self.pubsub.edit_subscription(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.unsubscribe(msg.topic_sub_keys)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUB_KEY_SERVER_SET(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.set_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_WSX_CLIENT_SUB_KEY_SERVER_REMOVE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.remove_ws_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_DELIVERY_SERVER_CHANGE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.old_delivery_server_id == self.server.id:
            old_server = self.pubsub.get_delivery_server_by_sub_key(msg.sub_key)
            if old_server:
                if old_server.server_pid == self.server.pid:
                    self.pubsub.migrate_delivery_server(msg)

# ################################################################################################################################
