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

import urlparse,random,urllib
import re, time, datetime
from resources.lib.lib import control
from resources.lib.lib import client
import json
import urllib2
import hashlib
import sys
import requests


headers= {'User-Agent':'mipla_ios/122','Content-Type':'application/x-www-form-urlencoded', 'Accept-Language': 'pl-pl'}
headers1 = {'User-Agent':'mipla_ios/122', 'Accept-Language':'pl-pl'}
headers2 = {'User-Agent':'ipla_MOBILE/122.0 (iPhone; ARM OS 10_0_2 like Mac OS X)'}
headers3 = {'User-Agent':'IPLA/4.2.2.5 CFNetwork/808.0.2 Darwin/16.0.0'}

url_system = 'https://gm2.redefine.pl/rpc/system/'
url_preauth = 'http://b2c.redefine.pl/rpc/auth/'
url_category ='http://b2c.redefine.pl/rpc/navigation/'
url_navigation = 'http://b2c.redefine.pl/rpc/navigation/'
url_hls = 'http://hls.redefine.pl'
post_init = json.loads('{"jsonrpc":"2.0","method":"getConfiguration","id":2,"params":{"message":{"id":"CC3DFE81-1C70-403A-9C52-FC10EC51125A","timestamp":"2016-10-16T00:08:57Z"}}}')
post_preauth = json.loads('{"jsonrpc":"2.0","method":"getAllRules","id":3,"params":{"rulesType":"login","message":{"id":"CCE2DB52-E7F7-4B3B-88F4-8FD4D919E4DF","timestamp":"2016-10-15T23:02:20Z"}}}')


def _call_ipla(url,data=None, headers=None):
    s = requests.Session()

    if data != None: request = urllib2.Request(url, data=json.dumps(data))
    else: request = urllib2.Request(url, data=None)
    if headers is not None:
        for i in headers:
            #print i, headers[i]
            request.add_header(i, headers[i])
    response = urllib2.urlopen(request, timeout=10)
    result = response.read(5242880)
    response.close
    return result

def gen_hex_code(myrange=6):
   return ''.join([random.choice('0123456789ABCDEF') for x in range(myrange)])

def ipla_system_id():
    systemid = control.setting('ipla.systemid').strip()
    if (systemid == ''):
        myrand = gen_hex_code(10) + '-' + gen_hex_code(4) + '-' + gen_hex_code(4) + '-' + gen_hex_code(
            4) + '-' + gen_hex_code(12)
        control.set_setting('ipla.systemid', myrand)
    return True

def getstream(id):
    try:
        control.infoDialog(control.lang(30495).encode('utf-8'), time=200)

        if getIplaCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40003).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Trakt', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.set_setting('ipla.user', '')
                control.set_setting('ipla.pass', '')
                control.openSettings('1.1')

            raise Exception()
        user = control.setting('ipla.user').strip()
        password = hashlib.md5(control.setting('ipla.pass').strip()).hexdigest()
        systemid = control.setting('ipla.systemid').strip()
        passwdmd5 = control.setting('ipla.passwdmd5').strip()


        url_auth = 'https://getmedia.redefine.pl/tv/menu.json?passwdmd5='+password+'&api_client=mipla_ios&login='+user+'&machine_id=iOS%'+systemid+'&outformat=2&api_build=122'
        post_getMedia = json.loads(
            '{"jsonrpc":"2.0","method":"getMedia","id":10,"params":{"cpid":0,"message":{"id":"F26642A8-8000-4C7A-B1CB-C2EADFD82E23","timestamp":"2016-10-16T00:53:25Z"},"authData":{"login":"'+user+'"},"mediaId":"'+str(id)+'"}}')
        post_perPlayData = json.loads(
            '{"jsonrpc":"2.0","method":"prePlayData","id":"-1864568404","params":{"mediaId":"'+str(id)+'","cpid":0,"authData":{"login":"'+user+'"}}}')


        #control.log('ipla1 %s' % id)

        result = _call_ipla(url_auth, headers=headers1)
        moje = json.loads(result)
        loginstatus = ipla_check_login(moje)
        if loginstatus <> 'OK':
            control.log('Ipla Login Error %s ' % loginstatus)
            control.infoDialog(loginstatus.encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - IPLA',loginstatus.encode('utf-8'), '')
            return
        my_action1 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DInterfejs/Login/Email%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=action'
        my_action2 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DIInterfejs/Start_Aplikacji/Kolejny%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=action'
        my_action3 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DInterfejs/Przegl%C4%85danie%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=view'

        result = _call_ipla(my_action1, headers=headers2)
        result = _call_ipla(my_action2, headers=headers2)
        result = _call_ipla(my_action3, headers=headers2)
        result = _call_ipla(url_navigation, post_getMedia, headers)

        result = _call_ipla(url_navigation, post_perPlayData, headers)
        moje = json.loads(result)
        url = moje['result']['mediaItem']['playback']['mediaSources'][-1]['authorizationServices']['pseudo']['url']
        myid = moje['result']['mediaItem']['playback']['mediaId']['id']

        url = url + '?cltype=mobile&cpid=0&id=' + myid + '&login='+user+'&passwdmd5='+passwdmd5+'&client_id=iOS%'+systemid+'&outformat=2'
        result = _call_ipla(url, headers=headers1)
        result = json.loads(result)
        url = result['resp']['license']['url'] + '|User-Agent='+urllib.quote_plus('IPLA/4.2.2.5 CFNetwork/808.0.2 Darwin/16.0.0')
        url = result['resp']['license']['url']

        result = _call_ipla(url, headers=headers3)
        result = result.decode('utf-8')
        link = re.findall("BANDWIDTH=\d+\n(.*?m3u8)", result, re.MULTILINE)[0]
        if url_hls in link:
            url = link + '?userid=iOS%' + systemid + '&initial|User-Agent=' + urllib.quote_plus(headers2['User-Agent'])
        else:
            url = url_hls +link + '?userid=iOS%'+systemid+'&initial|User-Agent='+ urllib.quote_plus(headers2['User-Agent'])
        return url

        return None

    except Exception as e:
        control.log('Error ipla.getstream %s' % e )
        return None

def getIplaCredentialsInfo():
    user = control.setting('ipla.user').strip()
    password = control.setting('ipla.pass')
    if (user == '' or password == ''): return False
    return True

def ipla_check_login(data):
    if data['config']['auth_errors']['auth'] != 200:
        #errdesc
        control.log('### AUTH %s' % data['config']['auth_errors']['auth'])
        return data['config']['auth_errors']['errdesc']
    return 'OK'

def ipla_chanels():
    control.log('Python version %s' %  (sys.version))
    #url10 = 'https://gm2.redefine.pl/rpc/system/'
    #headers10 = {'User-Agent': 'mipla_ios/122', 'Content-Type': 'application/x-www-form-urlencoded',
    #             'Accept-Language': 'pl-pl'}
    #post_init10 = {"jsonrpc": "2.0", "method": "getConfiguration", "id": 2, "params": {
    #    "message": {"id": "CC3DFE81-1C70-403A-9C52-FC10EC51125A", "timestamp": "2016-10-16T00:08:57Z"}}}
    #data = requests.post(url10, data=post_init, headers=headers10)
    #print data.status_code, data.text
    #control.log('request %s|%s' % (data.status_code, data.text))

    try:
        ipla_system_id()
        if getIplaCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40009).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Ipla',
                                   control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.set_setting('ipla.user', '')
                control.set_setting('ipla.pass', '')
                control.openSettings('1.1')

            raise ValueError('No login orr password')

        user = control.setting('ipla.user').strip()
        password = hashlib.md5(control.setting('ipla.pass').strip()).hexdigest()
        systemid = control.setting('ipla.systemid').strip()
        items = []
        post_getTVChannels = json.loads(
            '{"jsonrpc":"2.0","method":"getTvChannels","id":5,"params":{"authData":{"login":"'+user+'"},"message":{"id":"4B737B56-A11D-4E65-BC86-47EA1E40EC4D","timestamp":"2016-10-15T17:03:21Z"}}}')
        url_auth = 'https://getmedia.redefine.pl/tv/menu.json?passwdmd5='+password+'&api_client=mipla_ios&login='+user+'&machine_id=iOS%'+systemid+'&outformat=2&api_build=122'

        result = _call_ipla(url_system, post_init, headers)
        control.log('request %s' % (result))
        result = _call_ipla(url_preauth, post_preauth, headers)
        result = _call_ipla(url_auth, headers=headers1)
        moje = json.loads(result)
        loginstatus = ipla_check_login(moje)
        if loginstatus <> 'OK':
            control.log('Ipla Login Error %s ' % loginstatus)
            control.infoDialog(loginstatus.encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - IPLA',loginstatus.encode('utf-8'), '')
            return

        myperms = []
        for i in moje['config']['access_groups']:
            #control.log('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s' % i)
            if 'sc:' in i['code']:
                myperms.append(str(i['code']))
            if 'oth:' in i['code']:
                myperms.append(str(i['code']))
            #if 'loc:' in i['code']:
            #    myperms.append(str(i['code']))
        #control.log('###################################' % moje['config'])

        control.set_setting('ipla.passwdmd5', moje['config']['user']['passwdmd5'])


        my_action1 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DInterfejs/Login/Email%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=action'
        my_action2 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DIInterfejs/Start_Aplikacji/Kolejny%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=action'
        my_action3 = moje['config']['traffic_url'] + 'id=' + moje['config']['traffic_id'] + \
                     '&extra=GoalName%3DInterfejs/Przegl%C4%85danie%7Cc%3Dipla-ios/122/10.0.2/Apple/iPhone&et=view'

        result = _call_ipla(my_action1, headers=headers2)
        control.log('Python version %s' % (result))

        result = _call_ipla(my_action2, headers=headers2)
        result = _call_ipla(my_action3, headers=headers2)
        post_getCat = json.loads(
            '{"jsonrpc":"2.0","method":"getCategoryWithFlatNavigation","id":4,"params":{"catid":0,"authData":{"login":"'+user+'"},"message":{"id":"47B80EF0-19D0-4BD0-82FF-80BC50EDF2A9","timestamp":"2016-10-15T23:02:22Z"}}}')

        #result = _call_ipla(url_navigation, post_getCat, headers)
        result = _call_ipla(url_navigation, post_getTVChannels, headers)

        moje = json.loads(result)

        print "GETCAT", result
        for i in moje['result']['results']:
            item = {}
            channelperms = i['grantExpression'].split('*')
            channelperms = [w.replace('+plat:all', '') for w in channelperms]
            for j in myperms:
                #control.log('BB: %s AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA %s' % (i['title'].upper(), i['grantExpression']))
                if j in channelperms:
                    #print("OK", i['id'], i['title'], i['published'], i['grantExpression'])
                    # control.log('Dalina %s' % result2)
                    item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
                    item['id'] = i['id']
                    item['title'] = i['title'].upper().encode('utf-8')
                    item['plot'] = i['description'].encode('utf-8')
                    #control.log('RESULT I %s' % dump(item))
                    # control.log('Calina %s' % item)
                    item = {'title': item['title'], 'originaltitle': item['title'], 'genre': '0', 'plot': item['plot'], 'name':item['title'], 'tagline': '0',  'poster': item['img'], 'fanart': '0', 'id':item['id'], 'service':'ipla', 'next': ''}
                    items.append(item)

        #Dupes
        dupes = []
        filter = []
        for entry in items:
            if not entry['id'] in dupes:
                filter.append(entry)
                dupes.append(entry['id'])

        items = filter
        return items
    except Exception as e:
        control.log('Ipla Error %s ' % e)
        return

