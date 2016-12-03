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


import urlparse
import urllib, json
import re
import time, datetime


from resources.lib.lib import control
from resources.lib.lib import client2
from resources.lib.lib import client


headers = {'User-Agent': 'videostar/1.41 CFNetwork/758.3.15 Darwin/15.4.0'}
HOST = {'User-Agent': 'Specto for Kodi'}

def yoylogin():
    if getYoyCredentialsInfo() == False:
        raise ValueError('Brak ustawienia logiun lub hasła ')
    try:

        params = {}
        url = 'http://yoy.tv/signin'
        result, headers, content, cookie = client.request(url, output='extended')

        params['remember_me']='1'
        params['email'] = control.get_setting('yoytv.user')
        params['password'] = control.get_setting('yoytv.pass')
        params['_token']=client.parseDOM(result, 'input', ret='value', attrs={'name': '_token'})[0]
        result1, headers, content, cookie = client.request(url, post=params, cookie=cookie, output='extended', redirect=False)
        mycookies = re.findall('Set-Cookie: (.*?);', '%s' % content)
        cookie = ";".join(mycookies)
        control.set_setting('yoytv.sess', cookie)
        control.log('#####   cookie1: %s' % cookie)
        url = 'http://yoy.tv/'
        result = client.request(url, cookie=cookie)

        if not 'http://yoy.tv/signout' in result:
            control.log('BBBBB LOGIN %s' % 'yoy.tv')
            control.infoDialog(control.lang(30484).encode('utf-8'))
            control.dialog.ok(control.addonInfo('name') + ' - YOY TV', control.lang(30484).encode('utf-8'), '')
            control.openSettings('1.12')
            return False
        else:
            url = 'http://yoy.tv/user/settings'
            result = client.request(url, cookie=cookie)
            premium = re.findall('Aktywne do: ([0-9 :-]+)',result)
            if len(premium)>0:
                control.log('CCCCC LOGIN %s' % premium)
                control.infoDialog(control.lang(30496) + premium[0].encode('utf-8') )

            return True

    except Exception as e:
        control.log('Yoylogin ERROR %s' % e)
        return False


def getYoyCredentialsInfo():
    user = control.setting('yoytv.user').strip()
    password = control.setting('yoytv.pass')
    if (user == '' or password == ''): return False
    return True



def getstream(id):
    try:

        if yoylogin():
            cookie = control.get_setting('yoytv.sess').strip()
            control.log('#####   cookie2: %s' % cookie)
            url = 'http://yoy.tv/channels/%s' % id
            result = client.request(url, cookie=cookie)

            if 'http://yoy.tv/accept/' in result:
                if 'true' == control.get_setting('xxxmode'):
                    control.log('EROTYK ')
                    u1 = client.parseDOM(result, 'form', ret='action')[0]
                    params = {}
                    params['_token'] = client.parseDOM(result, 'input', ret='value', attrs={'name': '_token'})[0]
                    control.log('params: %s' % params['_token'])
                    result = client.request(u1, data=params, cookie=cookie)
                else:
                    control.infoDialog(control.lang(30799).encode('utf-8') + ' ' +control.lang(30798).encode('utf-8'))
                    return None

            if '<title>Kup konto premium w portalu yoy.tv</title>' in result:
                control.infoDialog(control.lang(30485).encode('utf-8'))
                return None

            myobj = client.parseDOM(result, 'object', ret='data', attrs={'type': 'application/x-shockwave-flash'})[0].encode('utf-8')
            result = client.parseDOM(result, 'param', ret='value', attrs={'name': 'FlashVars'})[0].encode('utf-8')
            control.log("YOY res: %s |%s| "  % (result,myobj))

            p = urlparse.parse_qs(result)
            #control.log('# %s' % query)
            control.log('# %s' % p)
            control.log('# %s' % p['fms'])
            control.log('# %s' % p['cid'])

            #lpi = result.index("s=") + result.index("=") * 3
            #control.log('# %s' )
            #rpi = result.index("&", lpi) - result.index("d") * 2
            #dp=[]
            #cp=result[lpi:rpi].split('.')
            #for i, item in enumerate(cp):
            #    j = 2 ^ i ^ ((i ^ 3) >> 1)
            #    k = 255 - int(cp[j])
            #    dp.append(k)
            #myip = '.'.join(map(str, dp))
            #control.log("YOY myip: %s " % (myip))

            #myplaypath='%s?email=%s&secret=%s&hash=%s' %(result['cid'],result['email'],result['secret'],result['hash'])
            #myurl = 'rtmp://'+myip + ' app=yoy/_definst_ playpath=' + myplaypath + ' swfUrl=' + myobj + \
            #        ' swfVfy=true tcUrl=' + 'rtmp://'+myip+'/yoy/_definst_ live=true timeout=15 pageUrl=' + url

            myurl = p['fms'][0] + '/' + p['cid'][0] + ' swfUrl=' + myobj + ' swfVfy=true tcUrl=' + p['fms'][
                0] + '/_definst_ live=true timeout=15 pageUrl=' + url
            myurl = p['fms'][0] + '/' + p['cid'][0] + ' swfUrl=' + myobj + ' swfVfy=true live=true timeout=15 pageUrl=' + url

            #        ' swfVfy=true tcUrl=' + 'rtmp://'+myip+'/oyo/_definst_ live=true pageUrl=' + url
            control.log("########## TAB:%s" % myurl)
            #myurl = myurl.replace('oyo','yoy')


            return myurl
        else:
            return None

    except Exception as e:
        control.log('Error yoy.getstream %s' % e)
        return None

def getchanels():
    try:
        if getYoyCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40004).encode('utf-8'), control.lang(30481).encode('utf-8'), '', 'YOY', control.lang(30483).encode('utf-8'), control.lang(30482).encode('utf-8')):
                control.openSettings('1.21')
            raise Exception()
        #login()
        items = []
        for j in range(1,10):
            try:
                url = 'http://yoy.tv/channels?live=1&country=140&page=%s' % j
                result = client.request(url)
                result = client.parseDOM(result, 'a', attrs = {'class': 'thumb-info team'})
                result = [(client.parseDOM(i, 'img', ret='src')[0], client.parseDOM(i, 'img', ret='alt')[0]) for i in result]
                for i in result:
                    item = {}
                    item['id'] = i[0].replace('http://yoy.tv/channel/covers/','').replace('.jpg?cache=32','')
                    control.log('YOY channel %s' % item['id'])
                    item['id']=item['id'].encode('utf-8')
                    item['title'] = control.trans(i[1].upper().encode('utf-8'))
                    items.append(item)
            except:
                control.log('YOY url: %s' % url)
                pass

        if 'true'== control.get_setting('xxxmode'):
            url = 'http://yoy.tv/channels?category=erotyka'
            result = client.request(url)
            result = client.parseDOM(result, 'a', attrs = {'class': 'thumb-info team'})
            result = [(client.parseDOM(i, 'img', ret='src')[0], client.parseDOM(i, 'img', ret='alt')[0]) for i in result]
            for i in result:
                control.log('XXX: %s' %i[0])
                item = {}
                item['id'] = i[0].replace('http://yoy.tv/channel/covers/','').replace('.jpg?cache=32','')
                control.log('XXX Alina %s' % item['id'])
                item['id']=item['id'].encode('utf-8')
                item['title'] = 'XXX '+ control.trans(i[1].upper().encode('utf-8'))
                items.append(item)

        return items
    except Exception as e:
        control.log('Error yoy.getchanels %s' % e)






