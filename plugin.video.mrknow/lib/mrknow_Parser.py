# -*- coding: utf-8 -*-
import sys
import urllib
import urlparse
from utils import convert

try:
    scriptID = sys.modules["__main__"].scriptID
except:
    scriptID = 'plugin.video.mrknow'
scriptname = "mrknow Polish films online"


class mrknow_Parser(object):
    """Helper for parsing and generating plugin params"""

    def __init__(self, paramstring=None):
        self.paramstring = paramstring or sys.argv[2]

    def getParam(self, params, name):
        """Get given parameter from dictionary.
        For backward compability. Not needed now.
        """
        return params.get(name)

    def getIntParam(self, params, name):
        """Get given parameter from dictionary as int
        Not needed so much.
        """
        try:
            return int(params.get(name))
        except:
            return None

    def getBoolParam(self, params, name):
        """Get given parameter from dictionary as boolean."""
        return params.get(name) in ('True', 'true', '1')

    def getParams(self, paramstring=None):
        """Parse plugin arguments"""
        if paramstring is None:
            paramstring = self.paramstring
        return convert.urldecode(paramstring)

    def setParams(self, params, add=False):
        '''Returns encoded dict. If add is True, skip "?".'''
        #http://stackoverflow.com/questions/3121186/error-with-urlencode-in-python
        s = convert.urlencode(params)
        return s if add else ('?' + s)

