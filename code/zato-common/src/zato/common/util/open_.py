# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

# Default encoding used with all text files
default_encoding = 'utf8'

# ################################################################################################################################

if 0:
    from zato.common.typing_ import binaryio_, iobytes_, textio_

# ################################################################################################################################

def open_r(path:'str', encoding:'str'=default_encoding) -> 'textio_':
    return open(path, 'r', encoding=encoding)

# ################################################################################################################################

def open_rb(path:'str') -> 'binaryio_':
    return open(path, 'rb')

# ################################################################################################################################

def open_rw(path:'str', encoding:'str'=default_encoding) -> 'textio_':
    return open(path, 'w+', encoding=encoding)

# ################################################################################################################################

def open_w(path:'str', encoding:'str'=default_encoding) -> 'textio_':
    return open(path, 'w', encoding=encoding)

# ################################################################################################################################

def open_wb(path:'str') -> 'iobytes_':
    return open(path, 'wb')

# ################################################################################################################################
