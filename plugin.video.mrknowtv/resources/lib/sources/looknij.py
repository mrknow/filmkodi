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
        if getLooknijCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40008).encode('utf-8'), control.lang(30481).encode('utf-8'), '',
                                   'Looknij', control.lang(30483).encode('utf-8'),
                                   control.lang(30482).encode('utf-8')):
                control.openSettings('1.4')
            raise Exception()


        params = {}
        #url = 'http://itivi.pl/include/login.php'
        #params['log'] = control.get_setting('itivi.user')
        #params['pwd'] = control.get_setting('itivi.pass')
        #result = client2.http_get(url, data=params)

        return True

    except Exception as e:
        control.log('Error wizja.login %s' % e)
        return False

def getstream(id):
    try:
        #if login():
        url='https://looknij.in/tv/data/%s' % id
        headers={'Referer':url, "X-Requested-With":"XMLHttpRequest"}
        params = {"isMobile":"false"}
        result =  client2.http_get(url, data=params, headers=headers)
        result = json.loads(result)
        #control.log('RES %s' % dump(result))
        if len(result)>0:
            link = result['Url']
            #control.log('RES %s' % dump(link))
            return link
        return
    except Exception as e:
        control.log('Error looknij.getstream %s' % e)
        return

def getLooknijCredentialsInfo():
    user = control.setting('looknij.user').strip()
    password = control.setting('looknij.pass')
    if (user == '' or password == ''): return False
    return True


def weebchanels():
    try:

        items=[]
        login()
        url = 'https://looknij.in/telewizja-online/'
        result = client2.http_get(url)
        r = client.parseDOM(result, 'div', attrs={'class': 'normal radius'})
        r = [(client.parseDOM(i, 'h3')[0],client.parseDOM(i, 'img', ret='src')[0]) for i in r]
        r = [(client.parseDOM(i[0], 'a', ret='href')[0], client.parseDOM(i[0], 'a')[0], i[1]) for i in r]
        #control.log('RESULT R %s' % dump(r))

        for i in r:
            item = {}
            try:
                # control.log('Dalina %s' % result2)
                item['img'] = i[2].encode('utf-8')
                item['id'] = i[0].split('-')[-1]
                #item['id'] = item['id'].encode('utf-8')
                item['title'] = i[1].replace('[Lektor]', '').replace('  ', '')
                item['title'] = item['title'].upper().encode('utf-8')
                #control.log('RESULT I %s' % dump(item))
                # control.log('Calina %s' % item)
                item = {'title': item['title'], 'originaltitle': item['title'], 'genre': '0', 'plot': '0', 'name':item['title'], 'tagline': '0',  'poster': item['img'], 'fanart': '0', 'id':item['id'], 'service':'looknij', 'next': ''}
                items.append(item)
            except Exception as e:
                control.log('         Error wizja.looknij for %s' % e)
                pass
        return items
    except Exception as e:
        control.log('         Error wizja.looknij for %s' % e)
        pass
        return items

def dump(obj):
  '''return a printable representation of an object for debugging'''
  newobj=obj
  if '__dict__' in dir(obj):
    newobj=obj.__dict__
    if ' object at ' in str(obj) and not newobj.has_key('__type__'):
      newobj['__type__']=str(obj)
    for attr in newobj:
      newobj[attr]=dump(newobj[attr])
  return newobj