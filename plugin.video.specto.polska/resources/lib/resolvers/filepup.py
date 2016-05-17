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


import re
from resources.lib.libraries import client
import urllib2


def resolve(url):
    #try:
        print("Entry URL",url)
        url = re.compile('//.+?/.+?/([\w]+)').findall(url)[0]
        url = 'http://www.filepup.net/play/%s?wmode=transparent' % url

        result = client.request(url)

        my1 = re.compile('url: [\'|\"].*remote/counter.php\?(.+?)[\'|\"]').findall(result)[0]
        print("my",my1)
        data={}
        myurl = 'http://www.filepup.net/remote/counter.php?'+my1
        result1 = client.request(myurl,data)
        #url: 'http://www.filepup.net/remote/counter.php?ip=88.156.134.241&file=3pfzZB6C1450869602',

        #url = client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video.+?'})[0]
        url = re.compile('type *: *[\'|\"]video/.+?[\'|\"].+?src *: *[\'|\"](.+?)[\'|\"]').findall(result)[0]
        print("Exit URL",url)
        return url+'|User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
    #except:
    #    return



