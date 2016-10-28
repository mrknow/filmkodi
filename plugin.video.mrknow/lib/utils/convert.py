# -*- coding: utf-8 -*-

import urllib
import urlparse 


def utf8(s):
    '''Convert str or unicode to UTF-8 str'''
    if isinstance(s, unicode):
        s = s.encode('utf8')
    elif isinstance(s, str):
        # Must be encoded in UTF-8, no result but only check
        s.decode('utf8')  # can raise UnicodeDecodeError
    return s


def urlencode(in_dict):
    '''Encode dict to URL string'''
    out_dict = {}
    for k, v in in_dict.iteritems():
        out_dict[k] = utf8(v)
    return urllib.urlencode(out_dict)


def urldecode(paramstring):
    '''Decode URL string to dict'''
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict(urlparse.parse_qsl(paramstring))  # returns normal dict, ignores duplicates
    #return urlparse.parse_qs(paramstring)  # returns dict with keys and LIST of values

