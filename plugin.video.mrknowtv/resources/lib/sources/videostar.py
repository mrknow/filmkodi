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

import json
import urlparse,base64,urllib
import re, time, datetime


from resources.lib.lib import control
from resources.lib.lib import client

headers = {'User-Agent': 'videostar/1.41 CFNetwork/758.3.15 Darwin/15.4.0'}


def get(url, params={}):
    try:
        if getVideostarCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40001).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Trakt', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.openSettings('1.11')
            raise Exception()

        url = urlparse.urljoin('https://api.videostar.pl', url)
        result = client.request(url, headers=headers, cookie=control.get_setting('videostar.sess'))
        r = json.loads(result)

        if r['status'] =="error" or result==None:
            if r['errors'][0]['code'] == 1:
                login()
                control.sleep(500)
                mycookie = control.get_setting('videostar.sess')
                result = client.source(url, headers=headers, cookie=control.get_setting('videostar.sess'))

        return result
    except Exception as e:
        control.log('Error videostar.get %s' % e)
        pass

#=mrknow@interia.pl&password=WestWest1!&permanent=1
def login():
    #f getVideostarCredentialsInfo() == False:
    #    raise Exception()
    params = {}
    #control.set_setting('videostar.sess', '')
    params['login'] = control.get_setting('videostar.user')
    params['password'] = control.get_setting('videostar.pass')
    params['permanent']=1
    url = 'https://api.videostar.pl/user/login'
    result = client.request(url, post=params, headers=headers, output='cookie')
    control.log('ResultC videostar.get %s' % result)

    control.set_setting('videostar.sess', result)
    url='https://api.videostar.pl/invitations/limit'
    headers['cookie']=result
    result2 = client.request(url, headers=headers)
    if 'error' in  result2:
        result2 = json.loads(result2)
        control.log('EEEEEEEEEEEE Result videostar.get %s' % result2['errors'][0]['msg'])
        control.infoDialog(result2['errors'][0]['msg'].encode('utf-8'))

    control.sleep(500)
    return result


def getVideostarCredentialsInfo():
    user = control.setting('videostar.user').strip()
    password = control.setting('videostar.pass')
    sess = control.setting('videostar.sess')

    if (user == '' or password == ''): return False
    return True



def getstream(id):
    try:
        url = 'https://api.videostar.pl/channels/get/%s?format_id=2' % id
        result = get(url)
        result = json.loads(result)
        if result['status'] == 'ok':
            url = result['stream_channel']['url_base']
            result = client.request(url, headers=headers, cookie=control.get_setting('videostar.sess'), output='geturl')
            return result

        raise Exception()
    except:
        #control.openSettings('6.1')
        control.log('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ' )










