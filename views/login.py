#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import functools
import os

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    import urllib
    quote = urllib.quote
if PY3:
    import urllib.parse
    quote = urllib.parse.quote

from flask import request, session, redirect, g
from utils.helpers import get_logger

log = get_logger(__name__)

def login_required(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        if g.user is None:
            return redirect('/api/v1/login?next=' + quote(request.url))
        return f(*args, **kwargs)
    return inner