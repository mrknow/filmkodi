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


HOST = 'XBMC'
headers = {'User-Agent': HOST, 'ContentType': 'application/x-www-form-urlencoded'}


def get(url, params={}):
    try:
        params['platform'] = HOST
        params['v'] = '0.2.0~beta'

        if getWeebCredentialsInfo():
            params['username'] = control.setting('weeb.user').strip()
            params['userpassword'] = control.setting('weeb.pass')

        url = urlparse.urljoin('http://weeb.tv', url)

        result = client.request(url, headers=headers, post=params)
        return result
    except:
        pass


def getstream(id):
    try:
        params={}
        params['channel']=id
        url = '/api/setPlayer'
        result = get(url, params)
        result = dict(urlparse.parse_qsl(result))
        playPath = result['11']
        bitrate = result['20']
        token = result['73']
        if bitrate == '1':
            playPath = playPath + 'HI'

        rtmp = str(result['10']) + '/' + playPath + ' live=true pageUrl=token swfUrl=' + token

        return rtmp

        raise Exception()
    except:
        #control.openSettings('6.1')
        control.log('Error weeb.getstream' )



def getWeebCredentialsInfo():
    user = control.get_setting('weeb.user').strip()
    password = control.get_setting('weeb.pass')
    if (user == '' or password == ''): return False
    return True



def weebchanels():
    items = []
    try:
        result = get('/api/getChannelList')
        result = json.loads(result)

        for i in result:
            try:
                if result[i]['channel_online'] != '2': raise Exception()
                id = result[i]['channel_name']
                title = result[i]['channel_title'].encode('utf-8')

                poster = '0'
                try:
                    poster = result[i]['channel_logo_url']
                except: pass

                fanart = '0'
                try: fanart = result[i]['channel_logo_url']
                except: pass
                #fanart = fanart.encode('utf-8')

                plot = '0'
                try:
                    plot=result[i]['channel_description']
                    plot = client.replaceHTMLCodes(plot)
                except: pass
                #plot = plot.encode('utf-8')

                tagline = '0'
                try: tagline = tagline.encode('utf-8')
                except: pass
                #tagline = plot.encode('utf-8')

                #ala = {'name': title, 'id': id}
                ala={'title': title, 'originaltitle': title, 'genre': '0', 'plot': plot, 'name': title, 'tagline': tagline, 'poster': poster, 'fanart': fanart, 'id': id,'service':'weeb', 'next': ''}
                items.append(ala)
            except:
                pass
        if len(items) == 0:
            items = result
    except:
        control.log('Error weeb.chanels' )
        pass
    return items



