# -*- coding: utf-8 -*-
import re, sys, os, cgi
import urllib, urllib2

scriptID = sys.modules[ "__main__" ].scriptID
scriptname = "mrknow Polish films online"

class mrknow_Parser:
    def __init__(self):
        pass
    
    def getParam(self, params, name):
        try:
            result = params[name]
            result = urllib.unquote_plus(result)
            return result
        except:
            return None

    def getIntParam (self, params, name):
        try:
            param = self.getParam(params, name)
            return int(param)
        except:
            return None
    
    def getBoolParam (self, params, name):
        try:
            param = self.getParam(params,name)
            return 'True' == param
        except:
            return None
        
    def getParams(self, paramstring = sys.argv[2]):
        param=[]
        if len(paramstring) >= 2:
            params = paramstring
            cleanedparams = params.replace('?', '')
            if (params[len(params)-1] == '/'):
                params = params[0:len(params)-2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        return param

    def setParam(self, params, add=False):
        #http://stackoverflow.com/questions/3121186/error-with-urlencode-in-python
        params_data = self.encoded_dict(params)
        #for k, v in params.iteritems():
        #    params_data[k] = unicode(v).encode('utf-8','replace')
        param = urllib.urlencode(params_data)

        if add == False:
            return "?"+param
        else:
            return param

    def encoded_dict(self,in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, str):
                # Must be encoded in UTF-8
                v.decode('utf8')
            out_dict[k] = v
        return out_dict

