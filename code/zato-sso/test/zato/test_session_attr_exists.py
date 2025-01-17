# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# Zato
from base import BaseTest

# ################################################################################################################################
# ################################################################################################################################

class SessionAttrExistsTestCase(BaseTest):

# ################################################################################################################################

    def test_exists(self):

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        self.post('/zato/sso/session/attr', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        response = self.get('/zato/sso/session/attr/exists', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'name': name,
        })

        self.assertTrue(response.result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
