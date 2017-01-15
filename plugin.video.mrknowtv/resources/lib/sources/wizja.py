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


HOST = {'User-Agent': 'Specto for Kodi'}
headers = {'User-Agent': 'Specto for Kodi', 'ContentType': 'application/x-www-form-urlencoded'}

def wizjalogin():
    try:
        params = {}
        url = 'http://wizja.tv/users/index.php'
        #result, headers, content, cookie = client.request(url, output='extended')

        params['login']='zaloguj'
        params['user_name'] = control.get_setting('wizja.user')
        params['user_password'] = control.get_setting('wizja.pass')

        #login to site
        result, headers, content, cookie = client.request(url, post=params, headers=HOST, output='extended')
        control.set_setting('wizja.token', cookie)

        #wrong login
        if  '<font color="#FF0000">Błędne hasło..</font>' in result: #zly login
            control.log('WIZJA.TV ZLY LOGIN: %s' % result)
            control.infoDialog(control.lang(30497).encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - WIZJA TV',control.lang(30497).encode('utf-8'), '')
            raise Exception()
        elif  'lub hasło.</font>' in result: #zly login
            control.log('WIZJA.TV ZLY LOGIN: %s' % result)
            control.infoDialog(control.lang(30486).encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - WIZJA TV',control.lang(30486).encode('utf-8'), '')

            raise Exception()

        elif 'Zalogowany jako :' in result:
            #no premium
            if '<font color=ff0000>Brak premium' in result:
                control.log('WIZJA.TV BRAK PREMIUM: %s' % result)
                control.infoDialog(control.lang(30490).encode('utf-8'), time=6000)
                control.dialog.ok(control.addonInfo('name') + ' - WIZJA TV', control.lang(30490).encode('utf-8'), '')

                raise Exception('NO premium')
            else:
                try:
                    premium = re.findall('Premium aktywne do (\d{4}.*?)</font>', result)[0]
                    control.set_setting('wizja.expire', premium)
                    control.infoDialog('Premium Wizja.tv do: '+ premium.encode('utf-8'), time=2000)
                except:
                    pass
                return True, cookie
        #account locked - wait 60 minutes
        elif '<font color="#FF0000">Wpisa' in result:
            control.log('WIZJA.TV zbyt wiele razy pobowales - poczekaj 60 minut: %s' % result)
            control.infoDialog(control.lang(30487).encode('utf-8'),time=6000)
            control.dialog.ok(control.addonInfo('name') + ' - WIZJA TV',control.lang(30487).encode('utf-8'), '')

            raise Exception('zbyt wiele razy pobowales - poczekaj 60 minut')
        #Other error
        else:
            control.log('WIZJA.TV inny blad: %s' % result)
            control.infoDialog(control.lang(30488).encode('utf-8'), time=6000)
            raise Exception('Inny bład: '+ result)
        return False

    except Exception as e:
        control.log('Error wizja.login %s' % e)
        return False

def getstream(id):
    try:

        if wizjalogin():
            cookie = control.setting('wizja.token').strip()
            ref='http://wizja.tv/watch.php?id=%s' % id
            result =  client.request(ref, headers=HOST, cookie=cookie)
            HOST['Referer']=ref
            url = 'http://wizja.tv/porter.php?ch=%s' % id
            result =  client.request(url, headers=HOST, cookie=cookie)
            mylink = re.compile('src: "(.*?)"').findall(result)
            mykill = re.compile('<a href="killme.php\?id=(.*?)" target="_top">').findall(result)
            control.log('AMA %s|%s' %(mylink,mykill))
            if len(mylink)>0:
                rtmp2 = urllib.unquote(mylink[0]).decode('utf8')
                rtmp1 = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(rtmp2)
                control.log('AMA1 %s' % (rtmp1))
                control.log('AMA2 %s' % (rtmp2))
                rtmp = 'rtmp://' + rtmp1[0][0] + '/' + rtmp1[0][1] + '?' + rtmp1[0][3] + \
                       ' playpath=' + rtmp1[0][2] + '?' + rtmp1[0][3] + \
                       ' app=' + rtmp1[0][1] + '?' + rtmp1[0][3] + \
                       ' swfVfy=1 flashver=WIN\\2020,0,0,306 timeout=25 swfUrl=http://wizja.tv/player/StrobeMediaPlayback_v3.swf live=true pageUrl=' + ref
                control.log('AMA3 %s' % (rtmp))

                return rtmp
            #kill other sessions
            elif len(mykill)>0:
                control.log('Error KILL %s' % mykill)
                urlkill = 'http://wizja.tv/killme.php?id=%s' % mykill[0]
                result = client.request(urlkill , headers=HOST, cookie=cookie)
                control.sleep(300)
                url = 'http://wizja.tv/porter.php?ch=%s' % id
                result = client.request(url, headers=HOST, cookie=cookie)
                mylink = re.compile('src: "(.*?)"').findall(result)
                if len(mylink)>0:
                    rtmp2 = urllib.unquote(mylink[0]).decode('utf8')
                    rtmp1 = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(rtmp2)
                    rtmp = 'rtmp://' + rtmp1[0][0] + '/' + rtmp1[0][1] +'?'+ rtmp1[0][3]+ \
                           ' playpath=' + rtmp1[0][2] + '?'+ rtmp1[0][3] + \
                           ' app=' + rtmp1[0][1] + '?' +rtmp1[0][3]+ \
                           ' swfVfy=1 flashver=WIN\\2020,0,0,306 timeout=25 swfUrl=http://wizja.tv/player/StrobeMediaPlayback_v3.swf live=true pageUrl='+ref
                    return rtmp
            else:
                raise Exception('WWW: '+result)
        else:
            return
    except Exception as e:
        control.log('Error wizja.getstream %s' % e)

def getWizjaCredentialsInfo():
    user = control.setting('wizja.user').strip()
    password = control.setting('wizja.pass')
    if (user == '' or password == ''): return False
    return True

def wizjachanels():
    try:
        if getWizjaCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40005).encode('utf-8'), control.lang(30481).encode('utf-8'), '',
                                   'Wizja', control.lang(30483).encode('utf-8'),
                                   control.lang(30482).encode('utf-8')):
                control.openSettings('1.18')
            raise Exception()

        if wizjalogin() == False: raise Exception()

        items = []
        url = 'http://wizja.tv/'
        result = client.request(url, headers=headers)
        result = client.parseDOM(result, 'td')

        for i in result:
            item = {}
            try:
                result2 = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'img', ret='src')[0])]
                item['img'] = 'http://wizja.tv/' + result2[0][1]
                item['img'] = item['img'].encode('utf-8')
                item['id'] = result2[0][0].replace('watch.php?id=','')
                item['id'] = item['id'].encode('utf-8')
                item['title'] = result2[0][1].replace('ch_logo/','').replace('.png','')
                item['title'] = item['title'].upper().encode('utf-8')
                items.append(item)
            except Exception as e:
                control.log('Error wizja.wizjachanels for %s' % e)
                pass
        return items
    except Exception as e:
        control.log('Error wizja.wizjachanels %s' % e)


"""
rtmpdump -r "rtmp://93.115.60.10:1939/pecEruxam24eTe8e?event=50&token=UQ1FdywLYH7gimlc4KIuMVz3hkADPq&user=mrknow"
-a "pecEruxam24eTe8e?event=50&token=UQ1FdywLYH7gimlc4KIuMVz3hkADPq&user=mrknow"
-f "LNX 23,0,0,207"
-W "http://wizja.tv/player/StrobeMediaPlayback_v3.swf" -p "http://wizja.tv/player.php?target=barbon1_p&ch=50"
-y "pHe7repheT?event=50&token=UQ1FdywLYH7gimlc4KIuMVz3hkADPq&user=mrknow" -o pHe7repheT.flv

 rtmp://93.115.60.10:1939/zusw6wEbawurEpUw/fredUw7pRu?event=136&token=CbFi6WgZnxrPsQTv13EYVq7OcNkeu2&user=mrknow app=zusw6wEbawurEpUw?event=136&token=CbFi6WgZnxrPsQTv13EYVq7OcNkeu2&user=mrknow swfVfy=1 flashver=WIN/2020,0,0,306 timeout=25 swfUrl=http://wizja.tv/player/StrobeMediaPlayback.swf live=true pageUrl=http://wizja.tv/watch.php?id=136


 pecEruxam24eTe8e


"""
