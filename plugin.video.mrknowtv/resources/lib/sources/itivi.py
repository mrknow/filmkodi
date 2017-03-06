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
#from resources.lib.lib import client2


HOST = 'XBMC'
headers = {'User-Agent': HOST, 'ContentType': 'application/x-www-form-urlencoded', 'Referer':"http://itivi.pl/"}
MAINURL = 'http://itivi.pl/'



def get(url, params={}):
    try:
        params['platform'] = HOST
        params['v'] = '0.2.0~beta'

        #if getWeebCredentialsInfo():
        #    params['username'] = control.setting('weeb.user').strip()
        #    params['userpassword'] = control.setting('weeb.pass')

        url = urlparse.urljoin(MAINURL, url)

        result = client.request(url, headers=headers, post=params)
        return result
    except:
        pass

def login():
    try:
        if getItiviCredentialsInfo() == False:
            if control.yesnoDialog(control.lang(40006).encode('utf-8'), control.lang(30481).encode('utf-8'), '',
                                   'Itivi', control.lang(30483).encode('utf-8'),
                                   control.lang(30482).encode('utf-8')):
                control.openSettings('2.1')
            raise Exception()


        params = {}
        #url = 'http://itivi.pl/include/login.php'
        #params['log'] = control.get_setting('itivi.user')
        #params['pwd'] = control.get_setting('itivi.pass')
        #client2._clean_cookies(url)
        #result = client2.http_get(url, data=params)
        #myres = client.parseDOM(result,'div', attrs={'class': 'account_field_box'})[0]
        #myres = client.parseDOM(myres,'font')
        #premium = myres[0] + client.parseDOM(myres[1],'b')[0] + ' ' + control.lang(30493)
        #control.infoDialog(premium.encode('utf-8'), time=200)
        return True

    except Exception as e:
        control.infoDialog(control.lang(30485).encode('utf-8'), time=400)
        control.log('Error itivi.login %s' % e)
        return True

def getstream(id):
    try:
        if login():
            #control.infoDialog(control.lang(30493).encode('utf-8'), time=200)
            ref='%s' % id
            result =  client.request(ref)
            headers={'Referer':ref}
            url = '%s' % id
            result =  client2.http_get(url, headers=headers)
            control.log('itivi.getstream0 %s' % result)

            mylink = re.compile("playM3U8byGrindPlayer\([\"'](.*?)[\"']\)").findall(result)
            control.log('itivi.getstream0 %s' % mylink)
            if len(mylink)>0:
                rtmp = mylink[0].replace('flv:','')
                for j in range(0, 5):
                    time.sleep(1)
                    try:
                        code, result2 = client.request(rtmp, output='response2', timeout='2')
                        control.log('Pierwsza link check nr: %s: result:%s %s|%s' % (j, result2,code, len(result2)))
                        if '404 Not Found' in result2:
                            return None
                        if 'offline.mp4' in result2:
                            return None
                        if result2 == None:
                            raise Exception()
                        elif len(result2) <1:
                            return None
                        else:
                            return rtmp
                    except:
                        pass
                #rtmp = rtmp + ' live=true timeout=15'
                return rtmp
            else:
                return None
    except Exception as e:
        control.log('Error itivi.getstream %s' % e)
        return

def getItiviCredentialsInfo():
    user = control.setting('itivi.user').strip()
    password = control.setting('itivi.pass')
    if (user == '' or password == ''): return False
    return True

def itivichanels():
    items = []
    try:
        result = get('/api.php',{'action':"GetStreams"})
        result = json.loads(result)
        result = re.compile('<img class="thumbnail" src="([^"]+)">\s.*<h5>(.*?)</h5>\s.*\s.*<a href="([^"]+)"').findall(result['html'])
        control.log('RED %s' % result)

        for i in result:
            try:
                id = i[2]
                title = i[1].encode('utf-8')

                poster = '0'
                try:
                    poster = MAINURL + [i][0]
                    poster = poster.encode('utf-8')
                except: pass
                control.log('Poster %s' % poster)
                fanart = '0'
                try:
                    fanart = MAINURL + [i][0]
                    fanart = fanart.encode('utf-8')
                except: pass
                #fanart = fanart.encode('utf-8')

                plot = '0'
                plot = plot.encode('utf-8')

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