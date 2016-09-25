# -*- coding: utf-8 -*-

'''
    Mrknow TV Add-on
    Copyright (C) 2016 mrknow

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urlparse,base64,urllib
import re, time, datetime
import json,sys


from resources.lib.lib import control
from resources.lib.lib import client
from resources.lib.lib import client2


HOST = 'XBMC'
headers = {'User-Agent': HOST, 'ContentType': 'application/x-www-form-urlencoded'}

def login():
    try:
        if getItiviCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40006).encode('utf-8'), control.lang(30481).encode('utf-8'), '',
                                   'Itivi', control.lang(30483).encode('utf-8'),
                                   control.lang(30482).encode('utf-8')):
                control.openSettings('2.1')
            raise Exception()


        params = {}
        url = 'http://itivi.pl/include/login.php'
        params['log'] = control.get_setting('itivi.user')
        params['pwd'] = control.get_setting('itivi.pass')
        result = client2.http_get(url, data=params)

        return True

    except Exception as e:
        control.log('Error wizja.login %s' % e)
        return False

def getstream(id):
    try:
        if login():
            ref='%s' % id
            result =  client2.http_get(ref)
            headers={'Referer':ref}
            url = '%s' % id
            result =  client2.http_get(url, headers=headers)
            mylink = re.compile("file[']*[:,]\s*[']([^']+)").findall(result)
            if len(mylink)>0:
                rtmp = mylink[0].replace('flv:','')
                rtmp = rtmp + ' live=true timeout=15'
                return rtmp
    except Exception as e:
        control.log('Error itivi.getstream %s' % e)

def getItiviCredentialsInfo():
    user = control.setting('itivi.user').strip()
    password = control.setting('itivi.pass')
    if (user == '' or password == ''): return False
    return True

