# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from logging import getLogger

# gevent
from gevent.lock import RLock

# netaddr
from netaddr import IPAddress, IPNetwork

# Zato
from zato.common.rate_limiting.common import Const, DefinitionItem, FromIPNotAllowed, ObjectInfo, RateLimitReached

# Python 2/3 compatibility
from future.utils import iterkeys
from past.builtins import unicode

# ################################################################################################################################
# ################################################################################################################################

class BaseLimiter(object):
    """ A per-server, approximate, rate limiter object. It is approximate because it does not keep track
    of what current rate limits in other servers are.
    """
    __slots__ = 'current_idx', 'lock', 'api', 'object_info', 'definition', 'has_from_any', 'from_any_rate', 'from_any_unit', \
        'is_limit_reached', 'ip_address_cache', 'current_period_func', 'by_period', 'parent_type', 'parent_name', \
        'is_exact'

    def __init__(self):
        self.current_idx = 0
        self.lock = RLock()
        self.api = None            # type: RateLimiting
        self.object_info = None    # type: ObjectInfo
        self.definition = None     # type: list
        self.has_from_any = None   # type: bool
        self.from_any_rate = None  # type: int
        self.from_any_unit = None  # type: unicode
        self.ip_address_cache = {} # type: dict
        self.by_period = {}        # type: dict
        self.parent_type = None    # type: unicode
        self.parent_name = None    # type: unicode
        self.is_exact = None       # type: bool

        self.current_period_func = {
            Const.Unit.day: self._get_current_day,
            Const.Unit.hour: self._get_current_hour,
            Const.Unit.minute: self._get_current_minute,
        }

# ################################################################################################################################

    @property
    def has_parent(self):
        return self.parent_type and self.parent_name

# ################################################################################################################################

    def cleanup(self):
        """ Cleans up time periods that are no longer needed.
        """
        with self.lock:

            # First, periodically clear out the IP cache to limit its size to 1,000 items
            if len(self.ip_address_cache) >= 1000:
                self.ip_address_cache.clear()

            now = datetime.utcnow()
            current_minute = self._get_current_minute(now)
            current_hour = self._get_current_hour(now)
            current_day = self._get_current_day(now)

            # We need a copy so as not to modify the dict in place
            periods = self._get_current_periods()
            to_delete = set()

            current_periods_map = {
                Const.Unit.minute: current_minute,
                Const.Unit.hour: current_hour,
                Const.Unit.day: current_day
            }

            for period in periods: # type: unicode
                period_unit = period[0] # type: unicode # One of Const.Unit instances
                current_period = current_periods_map[period_unit]

                # If this period is in the past, add it to the ones to be deleted
                if period < current_period:
                    to_delete.add(period)

# ################################################################################################################################

    def rewrite_rate_data(self, old_config):
        """ Writes rate limiting information from old configuration to our own. Used by RateLimiting.edit action.
        """
        # type: (RateLimiterApproximate)

        # Already collected rate limits
        self.by_period.clear()
        self.by_period.update(old_config.by_period)

# ################################################################################################################################

    def get_config_key(self):
        # type: () -> unicode
        return '{}:{}'.format(self.object_info.type_, self.object_info.name)

# ################################################################################################################################

    def _get_rate_config_by_from(self, orig_from, _from_any=Const.from_any):
        # type: (unicode, unicode) -> DefinitionItem

        from_ = self.ip_address_cache.setdefault(orig_from, IPAddress(orig_from)) # type: IPAddress
        found = None

        for line in self.definition: # type: DefinitionItem

            # A catch-all * pattern
            if line.from_ == _from_any:
                found = line
                break

            # A network match
            elif from_ in line.from_:
                found = line
                break

        # We did not match any line from configuration
        if not found:
            raise FromIPNotAllowed('From IP address not allowed `{}`'.format(orig_from))

        # We found a matching piece of from IP configuration
        return found

# ################################################################################################################################

    def _get_current_day(self, now, _prefix=Const.Unit.day, _format='%Y-%m-%d'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_hour(self, now, _prefix=Const.Unit.hour, _format='%Y-%m-%dT%H'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_minute(self, now, _prefix=Const.Unit.minute, _format='%Y-%m-%dT%H:%M'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

# ################################################################################################################################

    def _format_last_info(self, current_state):
        # type: (dict) -> unicode

        return 'last_from:`{last_from}; last_request_time_utc:`{last_request_time_utc}; last_cid:`{last_cid}`;'.format(
            **current_state)

# ################################################################################################################################

    def _raise_rate_limit_exceeded(self, rate, unit, orig_from, network_found, current_state, cid):
        raise RateLimitReached('Max. rate limit of {}/{} reached; from:`{}`, network:`{}`; {} ({})'.format(
            rate, unit, orig_from, network_found, self._format_last_info(current_state), cid))

# ################################################################################################################################

    def _check_limit(self, cid, orig_from, network_found, rate, unit, _rate_any=Const.rate_any, _utcnow=datetime.utcnow):
        # type: (unicode, unicode, unicode, object, unicode, unicode)

        # Local aliases
        now = _utcnow()

        # Get current period, e.g. current day, hour or minute
        current_period_func = self.current_period_func[unit]
        period = current_period_func(now)

        # Get or create a dictionary of requests information for current period
        period_dict = self.by_period.setdefault(period, {}) # type: dict

        # Get information about already stored requests for that network in current period
        current_state = period_dict.setdefault(network_found, {
            'requests': 0,
            'last_cid': None,
            'last_request_time_utc': None,
            'last_from': None,
            'last_network': None,
        }) # type: dict

        # Unless we are allowed to have any rate ..
        if rate != _rate_any:

            # We may have reached the limit already ..
            if current_state['requests'] >= rate:
                self._raise_rate_limit_exceeded(rate, unit, orig_from, network_found, current_state, cid)

        # .. otherwise, we increase the counter and store metadata.
        else:
            current_state['requests'] += 1
            current_state['last_cid'] = cid
            current_state['last_request_time_utc'] = now.isoformat()
            current_state['last_from'] = orig_from
            current_state['last_network'] = str(network_found)

        # Above, we checked our own rate limit but it is still possible that we have a parent
        # that also wants to check it.
        if self.has_parent:
            self.api.check_limit(cid, self.parent_type, self.parent_name, orig_from)

# ################################################################################################################################

    def check_limit(self, cid, orig_from):
        # type: (unicode, unicode)

        with self.lock:

            if self.has_from_any:
                rate = self.from_any_rate
                unit = self.from_any_unit
                network_found = Const.from_any
            else:
                found = self._get_rate_config_by_from(orig_from)
                rate = found.rate
                unit = found.unit
                network_found = found.from_

            # Now, check actual rate limits
            self._check_limit(cid, orig_from, network_found, rate, unit)


# ################################################################################################################################

    def _get_current_periods(self):
        raise NotImplementedError()

    _delete_periods = _get_current_periods

# ################################################################################################################################
# ################################################################################################################################

class Approximate(BaseLimiter):

    def _get_current_periods(self):
        return list(iterkeys(self.by_period))

    def _delete_periods(self, to_delete):
        for item in to_delete: # item: unicode
            del self.by_period[item]

# ################################################################################################################################
# ################################################################################################################################

class Exact(BaseLimiter):
    pass

# ################################################################################################################################
# ################################################################################################################################
