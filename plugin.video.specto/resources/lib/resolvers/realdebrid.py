# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

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


import urllib,json
from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import client


def getCredentials():
    user = control.setting('realdedrid_user') 
    password = control.setting('realdedrid_password')
    if (user == '' or password == ''): return False
    return (user, password)


def getHosts():
    try:
        user, password = getCredentials()
        url = 'http://real-debrid.com/api/hosters.php'
        result = cache.get(client.request, 24, url)
        hosts = json.loads('[%s]' % result)
        hosts = [i.rsplit('.' ,1)[0].lower() for i in hosts]
        return hosts
    except:
        return []


def resolve(url):
    try:
        user, password = getCredentials()

        login_data = urllib.urlencode({'user' : user, 'pass' : password})
        login_link = 'http://real-debrid.com/ajax/login.php?%s' % login_data
        result = client.request(login_link, close=False)
        result = json.loads(result)
        error = result['error']
        if not error == 0: raise Exception()
        cookie = result['cookie']

        url = 'http://real-debrid.com/ajax/unrestrict.php?link=%s' % url
        url = url.replace('filefactory.com/stream/', 'filefactory.com/file/')
        result = client.request(url, cookie=cookie, close=False)
        result = json.loads(result)
        url = result['generated_links'][0][-1]
        url = '%s|Cookie=%s' % (url, urllib.quote_plus(cookie))
        return url
    except:
        return

