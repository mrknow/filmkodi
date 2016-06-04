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
import json


from resources.lib.lib import control
from resources.lib.lib import client
from resources.lib.lib import stale


def get(url, params={}):
    try:

        params['api_id'] = stale.pierwszatv_apiid
        params['checksum'] = stale.pierwszatv_checksum
        url = urlparse.urljoin('http://pierwsza.tv', url)
        url = url + '?' + urllib.urlencode(params)
        headers = {'Content-Type': 'application/json'}

        result = client.request(url, headers=headers, output='response', error=True)
        if not (result[0] == '401' or result[0] == '405'): return result[1]

        result = client.request(url, headers=headers)
        #control.log('ZZZZZZZZ PIerwsza result: %s' % result)
        return result
    except:
        pass


def getstream(id):
    try:
        control.set_setting('pierwszatv.tokenExpireIn', '')
        control.set_setting('pierwszatv.serverId', '')
        control.set_setting('pierwszatv.streamId', '')
        control.set_setting('pierwszatv.token', '')

        if getPierwszaCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40003).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Trakt', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.set_setting('pierwszatv.user', '')
                control.set_setting('pierwszatv.password', '')
                control.openSettings('2.1')

            raise Exception()
        url = '/api/stream/create'
        params = {}
        params['id'] =id
        params['user'] =control.setting('pierwszatv.user').strip()
        params['password'] = urllib.quote_plus(control.setting('pierwszatv.password'))

        result = get(url, params)
        result = json.loads(result)

        if result['status'] == 'ok':
            #time.sleep(1)
            #control.log('x1x1x1: %s' % result['status'])
            expirein = int(int(result['tokenExpireIn'])*0.75)
            expirewhen  = datetime.datetime.now() + datetime.timedelta(seconds=expirein)
            control.set_setting('pierwszatv.tokenExpireIn', str(int(time.mktime(expirewhen.timetuple()))))
            control.set_setting('pierwszatv.serverId', result['serverId'])
            control.set_setting('pierwszatv.streamId', result['streamId'])
            control.set_setting('pierwszatv.token', result['token'])

            for i in range(0, 5):
                try:
                    r = get('/api/stream/status', {'serverId': result['serverId'] , 'streamId': result['streamId'], 'token': result['token']})
                    r = json.loads(r)
                    if r['status'] == 'ok':
                        control.infoDialog(control.lang(30489).encode('utf-8'), time=6000)
                        for j in range(0, 10):
                            time.sleep(1)
                            control.log('x1x1x1: %s' % j)

                            try:
                                result2 = client.request(r['source']+'?token='+result['token'],safe=True, timeout='2')
                                control.log('x1x1x1: %s' % result2)

                                if result2 == None: raise Exception()
                                else: return r['source']+'?token='+result['token']
                            except:
                                pass

                        return r['source']+'?token='+result['token']
                    time.sleep(3)

                except:
                    pass
        if result['status'] == 'error':
            control.infoDialog('%s' % result['message'].encode('utf-8'))

        return None

    except Exception as e:
        control.log('Error pierwsza.getstream %s' % e )


def getPierwszaCredentialsInfo():
    user = control.setting('pierwszatv.user').strip()
    password = control.setting('pierwszatv.password')
    if (user == '' or password == ''): return False
    return True

def streamrefresh():
    try:
        #mynow = int(datetime.datetime.now().strftime('%s'))
        mynow = int(str(int(time.mktime(datetime.datetime.now().timetuple()))))
        expired = int(control.get_setting('pierwszatv.tokenExpireIn'))
        #control.log('XXXX Exp:%s Now:%s' % (expired, mynow))

        if mynow>expired:
            control.log('Pierwsza refresh')
            url = '/api/stream/refresh'
            params = {}
            params['serverId'] =control.get_setting('pierwszatv.serverId')
            params['streamId'] =control.get_setting('pierwszatv.streamId')
            params['token'] = control.get_setting('pierwszatv.token')
            result = get(url, params)
            result = json.loads(result)
            expirein = int(int(result['tokenExpireIn'])*0.75)
            expirewhen = datetime.datetime.now() + datetime.timedelta(seconds=expirein)
            control.set_setting('pierwszatv.tokenExpireIn', str(int(time.mktime(expirewhen.timetuple()))))
    except Exception as e:
        control.log('Error pierwsza.refresh %s' % e )
        raise Exception()


def chanels():
    items = []
    try:
        result = get('/api/channels')
        result = json.loads(result)
        for i in result['channels']:
            try:
                items.append(i)
            except:
                pass
        if len(items) == 0:
            items = result
    except:
        control.log('Error pierwsza.chanels' )
        pass
    return items


