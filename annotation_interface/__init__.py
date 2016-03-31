#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Radim Rehurek <me@radimrehurek.com>
# Copyright (C) 2016 RaRe Technologies s.r.o.

import logging

try:
    __version__ = __import__('pkg_resources').get_distribution('analysis').version
except:
    __version__ = '?'


class NullHandler(logging.Handler):
    """For python versions <= 2.6; same as `logging.NullHandler` in 2.7."""
    def emit(self, record):
        pass

logger = logging.getLogger('analysis')
if not logger.handlers:  # ensure reload() doesn't add another one
    logger.addHandler(NullHandler())