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


import re,urllib
from resources.lib.libraries import client


def resolve(url):
    try:
        data = str(url).replace('\r','').replace('\n','').replace('\t','')
        doregex = re.compile('\$doregex\[(.+?)\]').findall(data)

        for i in range(0, 5):
            for x in doregex:
                try:
                    if not '$doregex[%s]' % x in data: raise Exception()

                    regex = re.compile('<regex>(.+?)</regex>').findall(data)
                    regex = [r for r in regex if '<name>%s</name>' % x in r][0]

                    if '$doregex' in regex: raise Exception()

                    expres = re.compile('<expres>(.+?)</expres>').findall(regex)[0]

                    try: referer = re.compile('<referer>(.+?)</referer>').findall(regex)[0]
                    except: referer = ''
                    referer = urllib.unquote_plus(referer)
                    referer = client.replaceHTMLCodes(referer)
                    referer = referer.encode('utf-8')

                    page = re.compile('<page>(.+?)</page>').findall(regex)[0]
                    page = urllib.unquote_plus(page)
                    page = client.replaceHTMLCodes(page)
                    page = page.encode('utf-8')

                    result = client.request(page, referer=referer)
                    result = str(result).replace('\r','').replace('\n','').replace('\t','')
                    result = str(result).replace('\/','/')

                    r = re.compile(expres).findall(result)[0]
                    data = data.replace('$doregex[%s]' % x, r)
                except:
                    pass

        url = re.compile('(.+?)<regex>').findall(data)[0]
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')

        if not '$doregex' in url: return url
    except:
        return

