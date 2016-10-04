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


import urlparse,base64,urllib, json
import re, time, datetime


from resources.lib.lib import control
from resources.lib.lib import client2
from resources.lib.lib import client


headers = {'User-Agent': 'videostar/1.41 CFNetwork/758.3.15 Darwin/15.4.0'}


def login():
    #if getYoyCredentialsInfo() == False:
    #    raise Exception()
    try:
        params = {}
        url = 'http://yoy.tv/signin'
        result = client2.http_get(url)
        params['remember_me']='1'
        params['email'] = control.get_setting('yoytv.user')
        params['password'] = control.get_setting('yoytv.pass')
        params['_token']=client.parseDOM(result, 'input', ret='value', attrs={'name': '_token'})[0]
        result = client2.http_get(url, data=params)
        #control.set_setting('videostar.sess', result)
        '<a class="dropdown-toggle" href="http://yoy.tv/signout">Wyloguj się'
        if not 'http://yoy.tv/signout' in result:
            control.log('BBBBB LOGIN %s' % 'yoy.tv')
            control.infoDialog(control.lang(30484).encode('utf-8'))
    except:
        pass


def getYoyCredentialsInfo():
    user = control.setting('yoytv.user').strip()
    password = control.setting('yoytv.pass')
    if (user == '' or password == ''): return False
    return True



def getstream(id):
    login()
    try:
        url = 'http://yoy.tv/channels/%s' % id
        result = client2.http_get(url)
        #control.log('RES:%s'%result)

        if 'http://yoy.tv/accept/' in result:
            if 'true' == control.get_setting('xxxmode'):
                control.log('EROTYK ')
                u1 = client.parseDOM(result, 'form', ret='action')[0]
                params = {}
                params['_token'] = client.parseDOM(result, 'input', ret='value', attrs={'name': '_token'})[0]
                control.log('params: %s' % params['_token'])
                result = client2.http_get(u1, data=params)
            else:
                control.infoDialog(control.lang(30799).encode('utf-8') + ' ' +control.lang(30798).encode('utf-8'))
                return None

        if '<title>Kup konto premium w portalu yoy.tv</title>' in result:
            control.infoDialog(control.lang(30485).encode('utf-8'))
            return None

        #control.log('r %s' % result)
        result = client.parseDOM(result, 'param', ret='value', attrs={'name': 'FlashVars'})[0].encode('utf-8')
        lpi = result.index("s=") + result.index("=") * 3
        rpi = result.index("&", lpi) - result.index("d") * 2
        dp=[]
        cp=result[lpi:rpi].split('.')
        for i, item in enumerate(cp):
            j = 2 ^ i ^ ((i ^ 3) >> 1)
            k = 255 - int(cp[j])
            dp.append(k)
        myip = '.'.join(map(str, dp))
        control.log(myip)
        result = dict(urlparse.parse_qsl(result))
        myplaypath='%s?email=%s&secret=%s&hash=%s' %(result['cid'],result['email'],result['secret'],result['hash'])
        myurl = 'rtmp://'+myip + ' app=yoy/_definst_ playpath=' + myplaypath + ' swfUrl=http://yoy.tv/playerv3a.swf' \
                ' swfVfy=true tcUrl=' + 'rtmp://'+myip+'/yoy/_definst_ live=true pageUrl=' + url
        #control.log("########## TAB:%s" % myurl)

        return myurl

    except Exception as e:
        control.log('Error yoy.getstream %s' % e)

def getchanels():
    try:
        if getYoyCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40004).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'YOY', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.openSettings('1.21')
            raise Exception()
        login()
        items = []
        for j in range(1,10):
            try:
                url = 'http://yoy.tv/channels?live=1&country=140&page=%s' % j
                result = client2.http_get(url)
                result = client.parseDOM(result, 'a', attrs = {'class': 'thumb-info team'})
                result = [(client.parseDOM(i, 'img', ret='src')[0], client.parseDOM(i, 'img', ret='alt')[0]) for i in result]
                for i in result:
                    item = {}
                    item['id'] = i[0].replace('http://yoy.tv/channel/covers/','').replace('.jpg?cache=32','')
                    control.log('YOY channel %s' % item['id'])
                    item['id']=item['id'].encode('utf-8')
                    item['title'] = i[1].upper().encode('utf-8')
                    items.append(item)
            except:
                control.log('YOY url: %s' % url)
                pass

        if 'true'== control.get_setting('xxxmode'):
            url = 'http://yoy.tv/channels?category=erotyka'
            result = client2.http_get(url)
            result = client.parseDOM(result, 'a', attrs = {'class': 'thumb-info team'})
            result = [(client.parseDOM(i, 'img', ret='src')[0], client.parseDOM(i, 'img', ret='alt')[0]) for i in result]
            for i in result:
                control.log('XXX: %s' %i[0])
                item = {}
                item['id'] = i[0].replace('http://yoy.tv/channel/covers/','').replace('.jpg?cache=32','')
                control.log('XXX Alina %s' % item['id'])
                item['id']=item['id'].encode('utf-8')
                item['title'] = 'XXX '+ i[1].upper().encode('utf-8')
                items.append(item)

        return items
    except Exception as e:
        control.log('Error yoy.getchanels %s' % e)






