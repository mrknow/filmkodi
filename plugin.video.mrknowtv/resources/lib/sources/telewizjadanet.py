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
import re, time
import json, urllib2
import datetime


from resources.lib.lib import control
from resources.lib.lib import client

base_url = 'http://www.telewizjada.net'

refreshtime=200

def getstream(id):
    try:

        if login() == False:
            control.log('Błędny login')
            raise ValueError('Błędny login')

        ua = control.get_setting('telewizjada.ua')
        myheaders = {'User-Agent':ua}
        token = control.get_setting('telewizjada.token')

        mainurl = 'http://www.telewizjada.net/live.php?cid=%s' % id
        myheaders['referer']=mainurl
        sidcookie = client.request(mainurl, headers=myheaders, output='cookie')
        #control.log('SidCookie: %s' % (sidcookie))

        url='http://www.statsgather.com/activatehls/getstats.php'
        hlsresult = client.request(url, post='', headers=myheaders, cookie='hls_stats=%s' % token)
        control.log('GetSTAT Result: %s' % hlsresult)
        mastercookie = '%s;%s;%s;%s ' % (sidcookie, 'hlsplugin=%s' % token, 'cb-enabled=accepted', 'cookieView=all' )
        #control.log('MASTERCOOKIE ' + mastercookie)


        url = 'http://www.telewizjada.net/net/service/verifydevice.php'
        params = json.dumps({'action':'new', 'key':hlsresult})
        jsonmyheaders = myheaders
        jsonmyheaders['Content-Type'] = 'application/json'
        jsonmyheaders['cookie'] = mastercookie
        #result = client.request(url, post=params, headers=jsonmyheaders)
        result, h1, content, cookie10 = client.request(url, post=params, headers=jsonmyheaders,output='extended')
        refreshcookie = '%s;%s;%s;%s ' % (sidcookie, '%s' % content['Set-Cookie'].split(';')[0], 'cb-enabled=accepted', 'cookieView=all' )
        #control.log('AccessCookie: %s|%s' % (result,content['Set-Cookie']))
        control.set_setting('telewizjada.refreshcookie', refreshcookie)
        control.set_setting('telewizjada.referer',mainurl)

        result = json.loads(result)

        if result['status'] == 'Active':
            #time.sleep(1)
            control.set_setting('telewizjada.expire', result['expire'])
            expirewhen  = datetime.datetime.now() + datetime.timedelta(seconds=refreshtime)
            control.set_setting('telewizjada.tokenExpireIn', str(int(time.mktime(expirewhen.timetuple()))))

            url = 'http://www.telewizjada.net/get_channel_data.php'
            myheaders1 = {'cookie': mastercookie, 'User-Agent':ua, 'referer': mainurl}
            params = {'cid':str(id)}
            result = client.request(url, post=params, headers=myheaders1)
            result = json.loads(result)
            vidlink = '%s|Cookie=%s' % (result['channelurl'], sidcookie)
            control.log('TELEWIZJADA VID %s' % vidlink)
            return vidlink

        return None

    except Exception as e:
        control.log('Error telewizjada.net .getstream %s' % e )

def getTelewizjadaCredentialsInfo():
    user, password = control.get_setting('telewizjada.user'), control.get_setting('telewizjada.pass')
    if (user == '' or password == ''): return False
    return True

def chanels():
    adult = control.get_setting('xxxmode')

    #if login() == False:
    #    control.log('Błędny login')
    #    raise ValueError('Błędny login')
    url = 'http://www.telewizjada.net/get_channels_cache.php'
    items = []
    try:
        result = client.request(url)
        result = json.loads(result)

        for i in result['channels']:
            try:
                if adult == 'false':
                    if i['isAdult'] == 1:
                        control.log('Adult telewizjada.chanels %s' % i['displayName'])
                        raise ValueError('Adult channel %s' % i['displayName'])
                item={}
                item['img'] =  urlparse.urljoin(base_url, i['bigThumb']).encode('utf-8')
                item['id'] = i['id']
                item['title'] = i['displayName'].upper().encode('utf-8')
                item['plot'] = i['description'].encode('utf-8')
                item = {'title': item['title'], 'originaltitle': item['title'], 'genre': '0', 'plot': item['plot'],
                        'name': item['title'], 'tagline': '0', 'poster': item['img'], 'fanart': '0', 'id': item['id'],
                        'service': 'telewizjadanet', 'next': ''}
                items.append(item)

            except:
                pass
        return items

    except Exception as e:
        control.log('Error telewizjada.chanels %s' % e)
        control.dialog.ok(control.addonInfo('name') + ' - Telewizjada.net', control.lang(30602).encode('utf-8'), '')
        return

def login():
    try:
        if getTelewizjadaCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40003).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'Trakt', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.set_setting('telewizjada.user', '')
                control.set_setting('telewizjada.password', '')
                control.openSettings('1.20')
        control.log('>>>>  LOGIN()' )

        expire = control.get_setting('telewizjada.expire')
        control.log('Expire1: %s' % expire)

        if expire != '':
            from datetime import datetime
            d = datetime.strptime(expire, '%Y-%m-%d %H:%M:%S')
            d2 = datetime.now()
            if d>d2:
                control.log('Expire OK: %s %s' % (d,d2))
                return True

        url = 'http://www.deltamediaplayer.com/index.php?option=com_users&view=login&Itemid=116'
        result, h1, content, cookie1 = client.request(url,output='extended')
        headers= {'referer':url}
        result = client.parseDOM(result, 'div', attrs={'class':'login'})[0]
        result = re.findall('<input type="hidden" name="([^"]+)" value="([^"]+)"',result)
        params = {  'username':control.get_setting('telewizjada.user'),
                    'password':control.get_setting('telewizjada.pass'),
                    'remember':'yes',
                    str(result[0][0]): urllib.quote(str(result[0][1])),
                    str(result[1][0]): urllib.quote(str(result[1][1]))
                    }
        #paramslog = {  'username':'',
        #            'password':'',
        #            'remember':'yes',
        #            str(result[0][0]): urllib.quote(str(result[0][1])),
        #            str(result[1][0]): urllib.quote(str(result[1][1]))
        #            }
        #control.log('>>>>  PARAMS %s' % (paramslog))

        url='http://www.deltamediaplayer.com/index.php?option=com_users&task=user.login'

        result, h2, content, cookie2 = client.request(url, redirect=False, post=params, headers=headers, cookie=cookie1, output='extended')
        #control.log('>>>>  Othe  L:%s | C:%s | ' % (content ,result))

        if content['Location'] != 'https://www.deltamediaplayer.com/index.php?option=com_users&view=profile':
            control.infoDialog(control.lang(30600).encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - Telewizzjada.net',control.lang(30600).encode('utf-8'), '')
            raise ValueError('Bledny login lub haslo.')

        #control.set_setting('wizja.token', cookie)

        url = 'http://www.deltamediaplayer.com/playercode/authorised/gethlsusers.php'
        headers['referer']='http://www.deltamediaplayer.com/index.php?option=com_acctexp&view=user&layout=subscriptiondetails&Itemid=119'
        headers['X-Requested-With']='XMLHttpRequest'
        headers['Content-Type'] = 'application/json'
        headers['cookie'] = '%s; %s' % (cookie1,content['Set-Cookie'].split(';')[0])
        params2=json.dumps({'browser':'Desktop;Windows;Chrome 54'})
        result = client.request(url,  post=params2, headers=headers)
        control.log('>>>>  RES r:%s ' % (result))

        r = json.loads(result)
        #control.log('QQQQQQQQQQQQQQ %s' % result, )

        result = [i for i in r if i['registered'] != 0]
        #control.log('QQQQQQQQQQQQQQ %s' % result, )

        if len(result)>0:
            for i in result:
                control.log('I %s' %i)

            control.log('QQQQQQQQQQQQQQ %s' % r[0]['hash'], )
            control.set_setting('telewizjada.token', r[0]['hash'])
            control.set_setting('telewizjada.os', r[0]['os'])
            control.set_setting('telewizjada.browser', r[0]['browser'])
            control.set_setting('telewizjada.device', r[0]['device'])
            control.log("Brovser: %s" % r[0]['browser'].split(' ')[0])
            ua = 'Mozilla/5.0 (%s; %s; rv:%s) Gecko/20100101 %s/%s' % (r[0]['os'], r[0]['device'], r[0]['browser'].split(' ')[-1],
                                                                       r[0]['browser'].split(' ')[0], r[0]['browser'].split(' ')[-1])
            control.log('UA %s' %ua)
            control.set_setting('telewizjada.ua', ua)
            return True

        else:
            control.infoDialog(control.lang(30601).encode('utf-8'), time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - Telewizzjada.net',control.lang(30601).encode('utf-8'), '')
            raise ValueError('Brak zarejestrowanych przeglądarek.')
        return False


    except Exception as e:
        control.log('Exception telewizjada.net login %s' % e)
        return False

def streamrefresh():
    try:
        #mynow = int(datetime.datetime.now().strftime('%s'))
        mynow = int(str(int(time.mktime(datetime.datetime.now().timetuple()))))
        expired = int(control.get_setting('telewizjada.tokenExpireIn'))
        #control.log('XXXX Telewizjadanet Exp:%s Now:%s' % (expired, mynow))

        if mynow>expired:
            ua = control.get_setting('telewizjada.ua')
            refreshcookie = control.get_setting('telewizjada.refreshcookie')
            referer = control.get_setting('telewizjada.referer')
            myheaders = {'User-Agent': ua, 'Content-Type':'application/json','cookie': refreshcookie,'referer':referer}
            url = 'http://www.telewizjada.net/net/service/verifydevice.php'
            params = json.dumps({"action":"old","key":""})
            result = client.request(url, post=params, headers=myheaders)
            control.log('Telewizjada verifydevice result: %s' % (result))
            expirewhen = datetime.datetime.now() + datetime.timedelta(seconds=refreshtime)
            control.set_setting('telewizjada.tokenExpireIn', str(int(time.mktime(expirewhen.timetuple()))))
    except Exception as e:
        control.log('Error telewizjada.refresh %s' % e )
        raise Exception()