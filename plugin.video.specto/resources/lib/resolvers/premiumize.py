# -*- coding: utf-8 -*-

'''
    Specto Add-on
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


import json,urllib
from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import client


def getCredentials():
    user = control.setting('premiumize_user') 
    password = control.setting('premiumize_password')
    if (user == '' or password == ''): return False
    return (user, password)


def getHosts():
    try:
        user, password = getCredentials()
        url = 'http://api.premiumize.me/pm-api/v1.php?method=hosterlist&params[login]=%s&params[pass]=%s' % (user, password)
        result = cache.get(client.request, 24, url)
        hosts = json.loads(result)['result']['hosterlist']
        hosts = [i.rsplit('.' ,1)[0].lower() for i in hosts]
        return hosts
    except:
        return []


def resolve(url):
    try:
        user, password = getCredentials()

        url = 'http://api.premiumize.me/pm-api/v1.php?method=directdownloadlink&params[login]=%s&params[pass]=%s&params[link]=%s' % (user, password, urllib.quote_plus(url))
        url = url.replace('filefactory.com/stream/', 'filefactory.com/file/')

        result = client.request(url, close=False)
        url = json.loads(result)['result']['location']
        return url
    except:
        return

