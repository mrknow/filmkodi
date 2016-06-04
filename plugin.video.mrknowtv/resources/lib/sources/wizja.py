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
    #if getYoyCredentialsInfo() == False:
    #    raise Exception()
    try:
        params = {}
        url = 'http://wizja.tv/users/index.php'
        result = client2.http_get(url)
        params['login']='zaloguj'
        params['user_name'] = control.get_setting('wizja.user')
        params['user_password'] = control.get_setting('wizja.pass')
        result = client2.http_get(url, data=params)
        control.log('DATA %s' % result)
        if  'o..</font><br>' in result:
            control.log('CCCC LOGIN %s' % 'wizja.tv')
            control.infoDialog(control.lang(30486).encode('utf-8'),time=6000)
            raise Exception()
        elif 'Zalogowany jako :' in result:
            if '<font color=ff0000>Brak premium' in result:
                control.infoDialog(control.lang(30490).encode('utf-8'), time=6000)
                return True
            else:
                return True
        elif '<font color="#FF0000">Wpisa' in result:
            control.log('CCCC LOGIN %s' % 'wizja.tv')
            control.infoDialog(control.lang(30487).encode('utf-8'),time=6000)
        else:
            control.log('CCCC LOGIN %s' % 'wizja.tv')
            control.infoDialog(control.lang(30488).encode('utf-8'), time=6000)

        return False

    except Exception as e:
        control.log('Error wizja.login %s' % e)


def getstream(id):
    try:
        if login():
            ref='http://wizja.tv/watch.php?id=%s' % id
            result =  client2.http_get(ref)
            headers={'Referer':ref}
            url = 'http://wizja.tv/porter.php?ch=%s' % id
            result =  client2.http_get(url, headers=headers)
            mylink = re.compile('src: "(.*?)"').findall(result)
            if len(mylink)>0:
                rtmp2 = urllib.unquote(mylink[0]).decode('utf8')
                rtmp1 = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(rtmp2)
                rtmp = 'rtmp://' + rtmp1[0][0] + '/' + rtmp1[0][1] +'/' +rtmp1[0][2]+ '?'+ rtmp1[0][3]+ ' app=' + rtmp1[0][1] + '?' +rtmp1[0][3]+' swfVfy=1 flashver=WIN\\2020,0,0,306 timeout=25 swfUrl=http://wizja.tv/player/StrobeMediaPlayback.swf live=true pageUrl='+ref
                return rtmp
            else:
                raise Exception()
        else:
            return
    except Exception as e:
        control.log('Error wizja.login %s' % e)



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
                control.openSettings('2.3')
            raise Exception()
        login()
        items = []
        url = 'http://wizja.tv/'
        result = client2.http_get(url)
        result = client.parseDOM(result, 'td')

        for i in result:
            item = {}
            try:
                result2 = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'img', ret='src')[0])]
                #control.log('Dalina %s' % result2)
                item['img'] = 'http://wizja.tv/' + result2[0][1]
                item['img'] = item['img'].encode('utf-8')
                item['id'] = result2[0][0].replace('watch.php?id=','')
                item['id'] = item['id'].encode('utf-8')
                item['title'] = result2[0][1].replace('ch_logo/','').replace('.png','')
                item['title'] = item['title'].upper().encode('utf-8')
                # control.log('Calina %s' % item)
                items.append(item)
            except Exception as e:
                control.log('                               Error wizja.wizjachanels for %s' % e)
                pass

        return items
    except Exception as e:
        control.log('Error wizja.wizjachanels %s' % e)