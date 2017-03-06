# -*- coding: utf-8 -*-
"""
App name
~~~~~~

:copyright: (c) 2014 by mrknow
:license: GNU GPL Version 3, see LICENSE for more details.
"""

import urllib

import urlparse, httplib, random, string


def getHostName(url):
    hostName = urlparse.urlparse(url)[1].split('.')
    return hostName[-2] + '.' + hostName[-1]

