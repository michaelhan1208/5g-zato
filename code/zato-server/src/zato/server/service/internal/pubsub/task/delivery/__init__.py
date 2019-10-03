'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Zato
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO

# ################################################################################################################################

# Type checking
if 0:
    from zato.server.pubsub.task import DeliveryTask, PubSubTool

# ################################################################################################################################

class _GetListSIO(object):
    output_required = ('server_name', 'server_pid', 'sub_key', 'topic_id', 'topic_name',
        'endpoint_id', 'endpoint_name', 'py_object', Int('messages'), Int('delivery_counter'))
    output_optional = 'last_sync', 'last_sync_sk', 'last_iter_run', AsIs('ext_client_id')
    output_repeated = True
    output_elem = None

# ################################################################################################################################
# ################################################################################################################################

class GetServerDeliveryTaskList(AdminService):
    """ Returns all delivery tasks for a particular server process (must be invoked on the required one).
    """
    SimpleIO = _GetListSIO

    def get_data(self):

        out = []

        for ps_tool in self.pubsub.pubsub_tools: # type: PubSubTool
            with ps_tool.lock:
                for sub_key, task in ps_tool.delivery_tasks.items(): # type: (str, DeliveryTask)

                    last_sync = task.last_iter_run #ps_tool.last_gd_run
                    if last_sync:
                        last_sync = datetime_from_ms(last_sync * 1000)

                    endpoint_id = self.pubsub.get_subscription_by_sub_key(task.sub_key).endpoint_id
                    endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)

                    out.append({
                        'server_name': ps_tool.server_name,
                        'server_pid': ps_tool.server_pid,
                        'endpoint_id': endpoint.id,
                        'endpoint_name': endpoint.name,
                        'py_object': task.py_object,
                        'sub_key': task.sub_key,
                        'topic_id': self.pubsub.get_topic_id_by_name(task.topic_name),
                        'topic_name': task.topic_name,
                        'messages': len(task.delivery_list),
                        'last_sync': last_sync,
                        'last_iter_run': datetime_from_ms(task.last_iter_run * 1000),
                        'delivery_counter': task.delivery_counter
                    })

        # Return the list of tasks sorted by sub_keys and their Python names
        return sorted(out, key=itemgetter('sub_key', 'py_object'))

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryTaskList(AdminService):
    """ Returns all delivery tasks for a particular server process (possibly a remote one).
    """
    name = 'pubsub.task.get-list2'

    class SimpleIO(GetListAdminSIO, _GetListSIO):
        input_required = 'cluster_id', 'server_name', 'server_pid'

    def handle(self):

        response = self.servers[self.request.input.server_name].invoke(GetServerDeliveryTaskList.get_name(), {
            'cluster_id': self.request.input.cluster_id,
        }, pid=self.request.input.server_pid)

        self.response.payload[:] = response['response']

# ################################################################################################################################
# ################################################################################################################################
'''
